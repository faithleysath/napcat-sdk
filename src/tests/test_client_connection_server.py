from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncGenerator, Callable
from contextlib import suppress
from types import TracebackType
from typing import Any, cast

import orjson
import pytest

from napcat.client import NapCatClient
from napcat.connection import Connection
from napcat.exceptions import NapCatAPIError
from napcat.matcher import TRUE, event_match
from napcat.server import ReverseWebSocketServer
from napcat.types import GroupMessageEvent, NapCatEvent
from napcat.types.messages import NodeReference, Text


class StubClient(NapCatClient):
    def __init__(self, response: dict[str, Any]) -> None:
        super().__init__()
        self._response = response

    async def send(self, data: dict[str, Any], timeout: float = 10.0) -> dict[str, Any]:
        return self._response


class RecordingClient(NapCatClient):
    def __init__(self) -> None:
        super().__init__()
        self.last_request: dict[str, Any] | None = None

    async def send(self, data: dict[str, Any], timeout: float = 10.0) -> dict[str, Any]:
        self.last_request = data
        return {"status": "ok", "retcode": 0, "data": None}


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


_WS_STOP = object()


class EventWS:
    def __init__(self) -> None:
        self._incoming: asyncio.Queue[bytes | object] = asyncio.Queue()
        self.closed = False

    async def send(self, data: bytes) -> None:
        _ = data

    def __aiter__(self) -> EventWS:
        return self

    async def __anext__(self) -> bytes:
        item = await self._incoming.get()
        if item is _WS_STOP:
            raise StopAsyncIteration
        return cast(bytes, item)

    async def emit(self, payload: dict[str, Any]) -> None:
        await self._incoming.put(orjson.dumps(payload))

    async def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        await self._incoming.put(_WS_STOP)


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


def make_group_message_event(
    text: str,
    *,
    message_id: int = 1,
    user_id: int = 10002,
    group_id: int = 123456,
) -> dict[str, Any]:
    return {
        "time": 0,
        "self_id": 10001,
        "post_type": "message",
        "message_type": "group",
        "sub_type": "normal",
        "message_id": message_id,
        "user_id": user_id,
        "message_seq": message_id,
        "real_id": message_id,
        "group_id": group_id,
        "raw_message": text,
        "message": [{"type": "text", "data": {"text": text}}],
        "font": 14,
        "sender": {
            "user_id": user_id,
            "nickname": "tester",
        },
    }


async def collect_first_event(
    events: AsyncGenerator[NapCatEvent, None],
) -> NapCatEvent:
    try:
        return await anext(events)
    finally:
        await events.aclose()


def is_group_message_with_text(text: str) -> Callable[[NapCatEvent], bool]:
    def _predicate(event: NapCatEvent) -> bool:
        return isinstance(event, GroupMessageEvent) and event.raw_message == text

    return _predicate


def always_true(event: NapCatEvent) -> bool:
    _ = event
    return True


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


def test_dot_handle_quick_operation_normalizes_segment_reply() -> None:
    async def _run() -> None:
        client = RecordingClient()

        await client.dot_handle_quick_operation(
            context={
                "time": 0,
                "self_id": 10001,
                "post_type": "message",
                "user_id": "10002",
            },
            operation={"reply": Text(text="hi")},
        )

        assert client.last_request == {
            "action": ".handle_quick_operation",
            "params": {
                "context": {
                    "time": 0,
                    "self_id": 10001,
                    "post_type": "message",
                    "user_id": "10002",
                },
                "operation": {
                    "reply": {
                        "type": "text",
                        "data": {"text": "hi"},
                    }
                },
            },
        }

    asyncio.run(_run())


def test_send_forward_msg_normalizes_messages_segments() -> None:
    async def _run() -> None:
        client = RecordingClient()

        await client.send_forward_msg(
            group_id="123456",
            messages=[NodeReference(id="654321")],
        )

        assert client.last_request == {
            "action": "send_forward_msg",
            "params": {
                "group_id": "123456",
                "messages": [
                    {
                        "type": "node",
                        "data": {
                            "id": "654321",
                        },
                    }
                ],
            },
        }

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


def test_wait_event_returns_matching_event_and_cleans_up_waiter() -> None:
    async def _run() -> None:
        ws = EventWS()
        conn = Connection(cast(Any, ws))
        await conn.__aenter__()
        client = NapCatClient(_existing_conn=conn)

        predicate = is_group_message_with_text("12")
        waiter = asyncio.create_task(client.wait_event(predicate, timeout=1.0))
        await asyncio.sleep(0)

        assert (
            client.matches_waiters(
                NapCatEvent.from_dict(make_group_message_event("12", message_id=10))
            )
            is True
        )

        try:
            await ws.emit(make_group_message_event("11", message_id=1))
            await ws.emit(make_group_message_event("12", message_id=2))

            matched = await asyncio.wait_for(waiter, timeout=1.0)

            assert isinstance(matched, GroupMessageEvent)
            assert matched.raw_message == "12"
            assert matched.message_id == 2
            assert (
                client.matches_waiters(
                    NapCatEvent.from_dict(
                        make_group_message_event("12", message_id=11)
                    )
                )
                is False
            )
        finally:
            await conn.close()

    asyncio.run(_run())


def test_wait_event_accepts_composed_matcher_predicate() -> None:
    async def _run() -> None:
        ws = EventWS()
        conn = Connection(cast(Any, ws))
        await conn.__aenter__()
        client = NapCatClient(_existing_conn=conn)

        def has_expected_text(event: NapCatEvent) -> bool:
            return isinstance(event, GroupMessageEvent) and event.raw_message == "12"

        predicate = event_match(GroupMessageEvent, group_id=123456) & has_expected_text
        waiter = asyncio.create_task(client.wait_event(predicate, timeout=1.0))
        await asyncio.sleep(0)

        try:
            await ws.emit(make_group_message_event("11", message_id=70))
            await ws.emit(make_group_message_event("12", message_id=71))

            matched = await asyncio.wait_for(waiter, timeout=1.0)

            assert isinstance(matched, GroupMessageEvent)
            assert matched.raw_message == "12"
            assert matched.message_id == 71
        finally:
            await conn.close()

    asyncio.run(_run())


def test_wait_event_accepts_true_seeded_plain_function_chain() -> None:
    async def _run() -> None:
        ws = EventWS()
        conn = Connection(cast(Any, ws))
        await conn.__aenter__()
        client = NapCatClient(_existing_conn=conn)

        def is_group_message(event: NapCatEvent) -> bool:
            return isinstance(event, GroupMessageEvent)

        def has_expected_text(event: NapCatEvent) -> bool:
            return isinstance(event, GroupMessageEvent) and event.raw_message == "12"

        predicate = TRUE & is_group_message & has_expected_text
        waiter = asyncio.create_task(client.wait_event(predicate, timeout=1.0))
        await asyncio.sleep(0)

        try:
            await ws.emit(make_group_message_event("11", message_id=72))
            await ws.emit(make_group_message_event("12", message_id=73))

            matched = await asyncio.wait_for(waiter, timeout=1.0)

            assert isinstance(matched, GroupMessageEvent)
            assert matched.raw_message == "12"
            assert matched.message_id == 73
        finally:
            await conn.close()

    asyncio.run(_run())


def test_wait_event_timeout_removes_waiter() -> None:
    async def _run() -> None:
        ws = EventWS()
        conn = Connection(cast(Any, ws))
        await conn.__aenter__()
        client = NapCatClient(_existing_conn=conn)

        try:
            with pytest.raises(TimeoutError):
                await client.wait_event(always_true, timeout=0.01)

            assert (
                client.matches_waiters(
                    NapCatEvent.from_dict(make_group_message_event("12", message_id=20))
                )
                is False
            )
        finally:
            await conn.close()

    asyncio.run(_run())


def test_multiple_waiters_can_match_same_event() -> None:
    async def _run() -> None:
        ws = EventWS()
        conn = Connection(cast(Any, ws))
        await conn.__aenter__()
        client = NapCatClient(_existing_conn=conn)

        predicate = is_group_message_with_text("12")
        waiter1 = asyncio.create_task(client.wait_event(predicate, timeout=1.0))
        waiter2 = asyncio.create_task(client.wait_event(predicate, timeout=1.0))
        await asyncio.sleep(0)

        try:
            await ws.emit(make_group_message_event("12", message_id=30))
            matched1, matched2 = await asyncio.gather(waiter1, waiter2)

            assert isinstance(matched1, GroupMessageEvent)
            assert isinstance(matched2, GroupMessageEvent)
            assert matched1.raw_message == "12"
            assert matched2.raw_message == "12"
            assert matched1.message_id == 30
            assert matched2.message_id == 30
        finally:
            await conn.close()

    asyncio.run(_run())


def test_filtered_events_skip_waiter_matches() -> None:
    async def _run() -> None:
        ws = EventWS()
        conn = Connection(cast(Any, ws))
        await conn.__aenter__()
        client = NapCatClient(_existing_conn=conn)

        predicate = is_group_message_with_text("12")
        waiter = asyncio.create_task(client.wait_event(predicate, timeout=1.0))
        filtered = asyncio.create_task(
            collect_first_event(client.events(filter_waiters=True))
        )
        await asyncio.sleep(0)

        try:
            await ws.emit(make_group_message_event("12", message_id=40))
            await asyncio.sleep(0)
            assert filtered.done() is False

            await ws.emit(make_group_message_event("13", message_id=41))
            waited_event = await asyncio.wait_for(waiter, timeout=1.0)
            filtered_event = await asyncio.wait_for(filtered, timeout=1.0)

            assert isinstance(waited_event, GroupMessageEvent)
            assert isinstance(filtered_event, GroupMessageEvent)
            assert waited_event.raw_message == "12"
            assert filtered_event.raw_message == "13"
        finally:
            await conn.close()

    asyncio.run(_run())


def test_filtered_events_skip_waiter_matches_after_consumer_delay() -> None:
    async def _run() -> None:
        ws = EventWS()
        conn = Connection(cast(Any, ws))
        await conn.__aenter__()
        client = NapCatClient(_existing_conn=conn)

        predicate = is_group_message_with_text("12")
        waiter = asyncio.create_task(client.wait_event(predicate, timeout=1.0))
        filtered_events = client.events(filter_waiters=True)

        try:
            await ws.emit(make_group_message_event("11", message_id=42))
            first_event = await asyncio.wait_for(anext(filtered_events), timeout=1.0)
            assert isinstance(first_event, GroupMessageEvent)
            assert first_event.raw_message == "11"

            await ws.emit(make_group_message_event("12", message_id=43))
            waited_event = await asyncio.wait_for(waiter, timeout=1.0)
            assert isinstance(waited_event, GroupMessageEvent)
            assert waited_event.raw_message == "12"

            # Simulate a slow filtered consumer. The waiter match should still be
            # filtered when this iterator resumes much later.
            await asyncio.sleep(1.1)

            next_event_task = asyncio.create_task(anext(filtered_events))
            await asyncio.sleep(0)
            assert next_event_task.done() is False

            await ws.emit(make_group_message_event("13", message_id=44))
            next_event = await asyncio.wait_for(next_event_task, timeout=1.0)
            assert isinstance(next_event, GroupMessageEvent)
            assert next_event.raw_message == "13"
        finally:
            await filtered_events.aclose()
            await conn.close()

    asyncio.run(_run())


def test_unfiltered_events_keep_waiter_matches() -> None:
    async def _run() -> None:
        ws = EventWS()
        conn = Connection(cast(Any, ws))
        await conn.__aenter__()
        client = NapCatClient(_existing_conn=conn)

        predicate = is_group_message_with_text("12")
        waiter = asyncio.create_task(client.wait_event(predicate, timeout=1.0))
        unfiltered = asyncio.create_task(collect_first_event(client.events()))
        await asyncio.sleep(0)

        try:
            await ws.emit(make_group_message_event("12", message_id=50))
            waited_event = await asyncio.wait_for(waiter, timeout=1.0)
            unfiltered_event = await asyncio.wait_for(unfiltered, timeout=1.0)

            assert isinstance(waited_event, GroupMessageEvent)
            assert isinstance(unfiltered_event, GroupMessageEvent)
            assert waited_event.raw_message == "12"
            assert unfiltered_event.raw_message == "12"
        finally:
            await conn.close()

    asyncio.run(_run())


def test_wait_event_predicate_errors_do_not_break_filtered_stream() -> None:
    async def _run() -> None:
        ws = EventWS()
        conn = Connection(cast(Any, ws))
        await conn.__aenter__()
        client = NapCatClient(_existing_conn=conn)

        def explode(event: NapCatEvent) -> bool:
            _ = event
            raise ValueError("boom")

        waiter = asyncio.create_task(client.wait_event(explode, timeout=1.0))
        filtered = asyncio.create_task(
            collect_first_event(client.events(filter_waiters=True))
        )
        await asyncio.sleep(0)

        try:
            await ws.emit(make_group_message_event("12", message_id=60))

            with pytest.raises(ValueError, match="boom"):
                await asyncio.wait_for(waiter, timeout=1.0)

            filtered_event = await asyncio.wait_for(filtered, timeout=1.0)
            assert isinstance(filtered_event, GroupMessageEvent)
            assert filtered_event.raw_message == "12"
            assert (
                client.matches_waiters(
                    NapCatEvent.from_dict(make_group_message_event("12", message_id=61))
                )
                is False
            )
        finally:
            await conn.close()

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
