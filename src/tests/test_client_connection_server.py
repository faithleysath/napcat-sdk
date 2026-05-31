from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncGenerator, Callable, Mapping
from contextlib import suppress
from types import TracebackType
from typing import Any, ClassVar, cast

import orjson
import pytest

import napcat.client as client_module
from napcat.client import NapCatClient
from napcat.connection import Connection
from napcat.exceptions import NapCatAPIError, NapCatProtocolError, NapCatStateError
from napcat.matcher import event_match
from napcat.server import ReverseWebSocketServer
from napcat.types import GroupMessageEvent, NapCatEvent
from napcat.types.messages import NodeReference, Text


class StubClient(NapCatClient):
    def __init__(self, response: dict[str, Any]) -> None:
        super().__init__()
        self._response = response

    async def _send(self, data: dict[str, Any], timeout: float = 10.0) -> dict[str, Any]:
        return self._response


class RecordingClient(NapCatClient):
    def __init__(self) -> None:
        super().__init__()
        self.last_request: dict[str, Any] | None = None

    async def _send(self, data: dict[str, Any], timeout: float = 10.0) -> dict[str, Any]:
        self.last_request = data
        return {"status": "ok", "retcode": 0, "data": None}


class CancelLoginClient(NapCatClient):
    @property
    def context_refs(self) -> int:
        return self._context_refs

    @property
    def connection(self) -> Connection | None:
        return self._conn

    @property
    def ws_context(self) -> Any | None:
        return self._ws_ctx

    async def cleanup_after_failed_enter(self) -> None:
        if self._conn is not None:
            await self._conn.close()
        if self._ws_ctx is not None:
            await self._ws_ctx.__aexit__(None, None, None)

    async def call_action(
        self,
        action: str,
        params: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any] | None:
        _ = action, params
        raise asyncio.CancelledError


class StateErrorLoginClient(CancelLoginClient):
    async def call_action(
        self,
        action: str,
        params: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any] | None:
        _ = action, params
        raise NapCatStateError("connection became invalid")


class MalformedLoginInfoClient(CancelLoginClient):
    def __init__(self, login_info: Mapping[str, Any] | None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._login_info = login_info

    async def call_action(
        self,
        action: str,
        params: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any] | None:
        _ = action, params
        return self._login_info


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


class ClientModeWS(EventWS):
    def __init__(self) -> None:
        super().__init__()
        self.close_calls: int = 0

    async def send(self, data: bytes) -> None:
        payload = cast(dict[str, Any], orjson.loads(data))
        echo = payload.get("echo")
        if payload.get("action") == "get_login_info" and echo:
            await self.emit(
                {
                    "status": "ok",
                    "retcode": 0,
                    "data": {
                        "user_id": 10001,
                        "nickname": "tester",
                    },
                    "echo": echo,
                }
            )

    async def close(self) -> None:
        self.close_calls += 1
        await super().close()


class FakeConnectContext:
    def __init__(self, ws: ClientModeWS) -> None:
        self.ws = ws
        self.exit_calls: int = 0

    async def __aenter__(self) -> ClientModeWS:
        return self.ws

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.exit_calls += 1
        await self.ws.close()


class InspectableConnection(Connection):
    last_instance: ClassVar[InspectableConnection | None] = None

    def __init__(self, ws: Any) -> None:
        super().__init__(ws)
        self.active_event_streams: int = 0
        type(self).last_instance = self

    async def events(self) -> AsyncGenerator[dict[str, Any], None]:
        self.active_event_streams += 1
        try:
            async for event in super().events():
                yield event
        finally:
            self.active_event_streams -= 1


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


def test_send_is_not_public_dynamic_api() -> None:
    client = NapCatClient()

    assert hasattr(client, "send") is False


def test_dynamic_api_call_emits_warning() -> None:
    async def _run() -> None:
        client = RecordingClient()
        action_name = "some_new_action"
        dynamic_call = getattr(client, action_name)

        with pytest.warns(RuntimeWarning, match="动态调用未封装的 API"):
            await dynamic_call(foo=1)

        assert client.last_request == {
            "action": "some_new_action",
            "params": {"foo": 1},
        }

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
        client = NapCatClient.from_connection(conn)
        with pytest.raises(ValueError, match="biz error"):
            async with client:
                raise ValueError("biz error")

    asyncio.run(_run())


def test_client_aexit_raises_cleanup_error_without_original_error() -> None:
    async def _run() -> None:
        conn = cast(Connection, FailingExitConnection())
        client = NapCatClient.from_connection(conn)
        with pytest.raises(RuntimeError, match="cleanup failed"):
            async with client:
                pass

    asyncio.run(_run())


def test_client_aenter_rolls_back_when_cancelled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _run() -> None:
        ws = ClientModeWS()
        ws_ctx = FakeConnectContext(ws)

        def fake_ws_connect(*args: object, **kwargs: object) -> FakeConnectContext:
            _ = args, kwargs
            return ws_ctx

        InspectableConnection.last_instance = None
        monkeypatch.setattr(client_module, "ws_connect", cast(Any, fake_ws_connect))
        monkeypatch.setattr(client_module, "Connection", InspectableConnection)

        client = CancelLoginClient(ws_url="ws://example.invalid")
        try:
            with pytest.raises(asyncio.CancelledError):
                await client.__aenter__()

            assert client.context_refs == 0
            assert client.connection is None
            assert client.ws_context is None
            assert ws.closed is True
            assert ws_ctx.exit_calls == 1
        finally:
            await client.cleanup_after_failed_enter()

    asyncio.run(_run())


def test_client_aenter_does_not_swallow_state_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _run() -> None:
        ws = ClientModeWS()
        ws_ctx = FakeConnectContext(ws)

        def fake_ws_connect(*args: object, **kwargs: object) -> FakeConnectContext:
            _ = args, kwargs
            return ws_ctx

        InspectableConnection.last_instance = None
        monkeypatch.setattr(client_module, "ws_connect", cast(Any, fake_ws_connect))
        monkeypatch.setattr(client_module, "Connection", InspectableConnection)

        client = StateErrorLoginClient(ws_url="ws://example.invalid")
        try:
            with pytest.raises(NapCatStateError, match="connection became invalid"):
                await client.__aenter__()

            assert client.context_refs == 0
            assert client.connection is None
            assert client.ws_context is None
            assert ws.closed is True
            assert ws_ctx.exit_calls == 1
        finally:
            await client.cleanup_after_failed_enter()

    asyncio.run(_run())


@pytest.mark.parametrize(
    "login_info",
    [
        None,
        {},
        {"user_id": None},
        {"user_id": "10001"},
        {"user_id": True},
    ],
)
def test_client_aenter_raises_protocol_error_for_malformed_login_info(
    monkeypatch: pytest.MonkeyPatch,
    login_info: Mapping[str, Any] | None,
) -> None:
    async def _run() -> None:
        ws = ClientModeWS()
        ws_ctx = FakeConnectContext(ws)

        def fake_ws_connect(*args: object, **kwargs: object) -> FakeConnectContext:
            _ = args, kwargs
            return ws_ctx

        InspectableConnection.last_instance = None
        monkeypatch.setattr(client_module, "ws_connect", cast(Any, fake_ws_connect))
        monkeypatch.setattr(client_module, "Connection", InspectableConnection)

        client = MalformedLoginInfoClient(
            login_info,
            ws_url="ws://example.invalid",
        )
        try:
            with pytest.raises(NapCatProtocolError, match="get_login_info response"):
                await client.__aenter__()

            assert client.context_refs == 0
            assert client.connection is None
            assert client.ws_context is None
            assert ws.closed is True
            assert ws_ctx.exit_calls == 1
        finally:
            await client.cleanup_after_failed_enter()

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


def test_wait_event_returns_matching_event() -> None:
    async def _run() -> None:
        ws = EventWS()
        conn = Connection(cast(Any, ws))
        await conn.__aenter__()
        client = NapCatClient.from_connection(conn)

        predicate = is_group_message_with_text("12")
        waiter = asyncio.create_task(client.wait_event(predicate, timeout=1.0))
        await asyncio.sleep(0)

        try:
            await ws.emit(make_group_message_event("11", message_id=1))
            await ws.emit(make_group_message_event("12", message_id=2))

            matched = await asyncio.wait_for(waiter, timeout=1.0)

            assert isinstance(matched, GroupMessageEvent)
            assert matched.raw_message == "12"
            assert matched.message_id == 2
        finally:
            await conn.close()

    asyncio.run(_run())


def test_concurrent_wait_event_in_client_mode_keeps_connection_open(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _run() -> None:
        ws = ClientModeWS()
        ws_ctx = FakeConnectContext(ws)

        def fake_ws_connect(*args: object, **kwargs: object) -> FakeConnectContext:
            _ = args, kwargs
            return ws_ctx

        InspectableConnection.last_instance = None
        monkeypatch.setattr(client_module, "ws_connect", cast(Any, fake_ws_connect))
        monkeypatch.setattr(client_module, "Connection", InspectableConnection)

        client = NapCatClient(ws_url="ws://example.invalid")
        waiter1 = asyncio.create_task(
            client.wait_event(is_group_message_with_text("12"), timeout=1.0)
        )
        waiter2 = asyncio.create_task(
            client.wait_event(is_group_message_with_text("13"), timeout=1.0)
        )
        try:
            for _ in range(100):
                conn = InspectableConnection.last_instance
                if conn is not None and conn.active_event_streams == 2:
                    break
                await asyncio.sleep(0.01)
            else:
                pytest.fail("wait_event consumers did not start in time")

            await ws.emit(make_group_message_event("12", message_id=21))
            matched1 = await asyncio.wait_for(waiter1, timeout=1.0)

            assert isinstance(matched1, GroupMessageEvent)
            assert matched1.raw_message == "12"
            assert not waiter2.done()
            assert not ws.closed
            assert ws_ctx.exit_calls == 0

            await ws.emit(make_group_message_event("13", message_id=22))
            matched2 = await asyncio.wait_for(waiter2, timeout=1.0)
            for _ in range(100):
                if ws_ctx.exit_calls:
                    break
                await asyncio.sleep(0.01)

            assert isinstance(matched2, GroupMessageEvent)
            assert matched2.raw_message == "13"
            assert ws.closed is True
            assert ws_ctx.exit_calls == 1
            assert ws.close_calls >= 1
        finally:
            for task in (waiter1, waiter2):
                if not task.done():
                    task.cancel()
                    with suppress(asyncio.CancelledError):
                        await task

    asyncio.run(_run())


def test_wait_event_accepts_composed_matcher_predicate() -> None:
    async def _run() -> None:
        ws = EventWS()
        conn = Connection(cast(Any, ws))
        await conn.__aenter__()
        client = NapCatClient.from_connection(conn)

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

def test_wait_event_timeout_closes_event_stream() -> None:
    async def _run() -> None:
        ws = EventWS()
        conn = InspectableConnection(cast(Any, ws))
        await conn.__aenter__()
        client = NapCatClient.from_connection(conn)

        try:
            with pytest.raises(TimeoutError):
                await client.wait_event(always_true, timeout=0.01)

            assert conn.active_event_streams == 0
        finally:
            await conn.close()

    asyncio.run(_run())


def test_multiple_waiters_can_match_same_event() -> None:
    async def _run() -> None:
        ws = EventWS()
        conn = Connection(cast(Any, ws))
        await conn.__aenter__()
        client = NapCatClient.from_connection(conn)

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


def test_wait_event_does_not_consume_event_stream() -> None:
    async def _run() -> None:
        ws = EventWS()
        conn = Connection(cast(Any, ws))
        await conn.__aenter__()
        client = NapCatClient.from_connection(conn)

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


def test_wait_event_predicate_errors_do_not_break_independent_stream() -> None:
    async def _run() -> None:
        ws = EventWS()
        conn = Connection(cast(Any, ws))
        await conn.__aenter__()
        client = NapCatClient.from_connection(conn)

        def explode(event: NapCatEvent) -> bool:
            _ = event
            raise ValueError("boom")

        waiter = asyncio.create_task(client.wait_event(explode, timeout=1.0))
        event_stream = asyncio.create_task(collect_first_event(client.events()))
        await asyncio.sleep(0)

        try:
            await ws.emit(make_group_message_event("12", message_id=60))

            with pytest.raises(ValueError, match="boom"):
                await asyncio.wait_for(waiter, timeout=1.0)

            streamed_event = await asyncio.wait_for(event_stream, timeout=1.0)
            assert isinstance(streamed_event, GroupMessageEvent)
            assert streamed_event.raw_message == "12"
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
