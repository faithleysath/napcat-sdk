from __future__ import annotations

import asyncio
import time
from contextlib import suppress
from types import TracebackType
from typing import Any, cast

import pytest

from napcat.client import NapCatClient
from napcat.connection import Connection
from napcat.exceptions import NapCatAPIError
from napcat.server import ReverseWebSocketServer


class StubClient(NapCatClient):
    def __init__(self, response: dict[str, Any]) -> None:
        super().__init__()
        self._response = response

    async def send(self, data: dict[str, Any], timeout: float = 10.0) -> dict[str, Any]:
        return self._response


class FailingExitConnection:
    @property
    def is_running(self) -> bool:
        return True

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        raise RuntimeError("cleanup failed")


class BlockingSendWS:
    def __init__(self) -> None:
        self._send_block = asyncio.Event()
        self._iter_block = asyncio.Event()

    async def send(self, data: bytes) -> None:
        await self._send_block.wait()

    def __aiter__(self) -> BlockingSendWS:
        return self

    async def __anext__(self) -> bytes:
        await self._iter_block.wait()
        raise StopAsyncIteration

    async def close(self) -> None:
        self._send_block.set()
        self._iter_block.set()


class FakeServer:
    def __init__(self, closed_signal: asyncio.Event) -> None:
        self._closed_signal = closed_signal
        self.close_called = False

    def close(self) -> None:
        self.close_called = True

    async def wait_closed(self) -> None:
        await self._closed_signal.wait()


class InspectableServer(ReverseWebSocketServer):
    def inject_server(self, server: Any) -> None:
        self._server = server

    def register_task(self, task: asyncio.Task[None]) -> None:
        self._active_tasks.add(task)

    @property
    def active_task_count(self) -> int:
        return len(self._active_tasks)

    @property
    def internal_server(self) -> Any:
        return self._server


@pytest.mark.parametrize(
    "response",
    [
        {"status": "failed", "retcode": 0, "data": {}},
        {"status": "ok", "retcode": 10001, "data": {}},
    ],
)
def test_call_action_raises_when_status_or_retcode_failed(
    response: dict[str, Any],
) -> None:
    async def _run() -> None:
        client = StubClient(response)
        with pytest.raises(NapCatAPIError):
            await client.call_action("test_action")

    asyncio.run(_run())


def test_call_action_returns_data_on_success() -> None:
    async def _run() -> None:
        client = StubClient({"status": "ok", "retcode": 0, "data": {"ok": True}})
        data = await client.call_action("test_action")
        assert data == {"ok": True}

    asyncio.run(_run())


def test_client_aexit_does_not_mask_original_error() -> None:
    async def _run() -> None:
        conn = cast(Connection, FailingExitConnection())
        client = NapCatClient(_existing_conn=conn)
        with pytest.raises(ValueError, match="biz error"):
            async with client:
                raise ValueError("biz error")

    asyncio.run(_run())


def test_client_aexit_raises_cleanup_error_without_original_error() -> None:
    async def _run() -> None:
        conn = cast(Connection, FailingExitConnection())
        client = NapCatClient(_existing_conn=conn)
        with pytest.raises(RuntimeError, match="cleanup failed"):
            async with client:
                pass

    asyncio.run(_run())


def test_connection_send_timeout_also_covers_send_phase() -> None:
    async def _run() -> None:
        conn = Connection(cast(Any, BlockingSendWS()))
        await conn.__aenter__()

        started = time.monotonic()
        try:
            with pytest.raises(TimeoutError):
                await asyncio.wait_for(
                    conn.send({"action": "ping"}, timeout=0.01),
                    timeout=0.30,
                )
        finally:
            await conn.close()

        elapsed = time.monotonic() - started
        assert elapsed < 0.15

    asyncio.run(_run())


def test_server_close_cancels_active_tasks_before_wait_closed() -> None:
    async def handler(client: NapCatClient) -> None:
        _ = client

    async def _run() -> None:
        closed_signal = asyncio.Event()
        server = InspectableServer(
            handler=handler,
            shutdown_timeout=0.5,
        )
        fake_server = FakeServer(closed_signal)
        server.inject_server(cast(Any, fake_server))

        async def active_task() -> None:
            try:
                await asyncio.Event().wait()
            finally:
                closed_signal.set()

        task = asyncio.create_task(active_task())
        server.register_task(task)
        await asyncio.sleep(0)

        try:
            await asyncio.wait_for(server.close(), timeout=1.0)
        finally:
            if not task.done():
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task

        assert fake_server.close_called is True
        assert task.cancelled()
        assert server.active_task_count == 0
        assert server.internal_server is None

    asyncio.run(_run())
