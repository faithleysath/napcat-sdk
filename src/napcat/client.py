"""
NapCat 客户端实现

提供 NapCatClient 类，用于与 NapCatQQ 建立连接（正向 WebSocket）或复用现有连接（反向 WebSocket）。
包含事件生成器 (_events) 和 API 调用方法 (call_action)。
"""

import asyncio
import logging
from collections.abc import AsyncGenerator, Callable, Mapping
from types import TracebackType
from typing import Any, Self, cast

import orjson
from websockets.asyncio.client import connect as ws_connect

from .client_api import NapCatAPIMixin
from .connection import Connection
from .exceptions import NapCatAPIError, NapCatError, NapCatStateError
from .types import NapCatEvent
from .types.messages import Message

logger = logging.getLogger("napcat.client")
type WaitPredicate = Callable[[NapCatEvent], bool]


class NapCatClient(NapCatAPIMixin):
    def __init__(
        self,
        ws_url: str | None = None,
        token: str | None = None,
    ):
        self.ws_url = ws_url
        self.token = token
        self._conn: Connection | None = None
        self._has_external_conn = False
        self._ws_ctx: ws_connect | None = None
        self._entered = False
        self._context_refs = 0
        self._lifecycle_lock = asyncio.Lock()
        self.self_id: int | None = None

        self._waiters: list[tuple[object, WaitPredicate]] = []
        self._matched_waiter_events: dict[bytes, None] = {}
        self._matched_waiter_cache_size = 1000

    @classmethod
    def from_connection(cls, conn: Connection) -> Self:
        client = cls()
        client._conn = conn
        client._has_external_conn = True
        return client

    def _connection_running(self) -> bool:
        return bool(self._conn and self._conn.is_running)

    @property
    def is_running(self) -> bool:
        return self._connection_running()

    async def __aenter__(self):
        async with self._lifecycle_lock:
            self._context_refs += 1

            # 已有活跃连接时，仅增加上下文引用计数即可
            # 不依赖引用计数值判断复用，直接以连接运行状态为准
            if self._connection_running():
                self._entered = True
                return self

            # 用于跟踪已打开的资源，便于异常时回滚
            ws_ctx_entered = False
            conn_entered = False

            try:
                # 如果是 Server 模式，直接启动 from_connection 传入的连接
                if self._has_external_conn:
                    if not self._conn:
                        raise ValueError("Invalid Client: Missing existing connection")
                    await self._conn.__aenter__()
                    conn_entered = True
                # 如果是 Client 模式（主动连接），建立连接并包装
                elif self.ws_url:
                    headers = (
                        {"Authorization": f"Bearer {self.token}"} if self.token else {}
                    )
                    self._ws_ctx = ws_connect(self.ws_url, additional_headers=headers)
                    ws = await self._ws_ctx.__aenter__()
                    ws_ctx_entered = True
                    self._conn = Connection(ws)
                    await self._conn.__aenter__()
                    conn_entered = True
                else:
                    raise ValueError(
                        "Invalid Client: No URL and no existing connection"
                    )

                self._entered = True
                # 获取自身 ID (增加容错处理)
                try:
                    resp = await self.get_login_info()
                    self.self_id = resp["user_id"]
                except NapCatError as e:
                    logger.warning("Failed to get self_id: %s", e)
                    self.self_id = None

                return self
            except Exception:
                # 异常时回滚已打开的资源
                if conn_entered and self._conn:
                    try:
                        await self._conn.__aexit__(None, None, None)
                    except Exception:
                        pass
                if ws_ctx_entered and self._ws_ctx:
                    try:
                        await self._ws_ctx.__aexit__(None, None, None)
                    except Exception:
                        pass
                # 清理状态
                if not self._has_external_conn:
                    self._conn = None
                self._ws_ctx = None
                self._context_refs -= 1
                if self._context_refs == 0:
                    self._entered = False
                raise

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        async with self._lifecycle_lock:
            if self._context_refs == 0:
                return

            self._context_refs -= 1
            if self._context_refs > 0:
                return

            # 级联关闭：Client -> Connection -> WebSocket
            conn = self._conn
            ws_ctx = self._ws_ctx
            cleanup_errors: list[BaseException] = []

            try:
                if conn:
                    try:
                        await conn.__aexit__(exc_type, exc_val, exc_tb)
                    except Exception as e:
                        cleanup_errors.append(e)
                # 仅在 Client 模式下关闭 ws_ctx（Server 模式由外部管理）
                if ws_ctx and not self._has_external_conn:
                    try:
                        await ws_ctx.__aexit__(exc_type, exc_val, exc_tb)
                    except Exception as e:
                        cleanup_errors.append(e)
            finally:
                self._entered = False
                if not self._has_external_conn:
                    self._conn = None
                self._ws_ctx = None

            if cleanup_errors:
                for err in cleanup_errors:
                    logger.warning("Cleanup error: %s", err)
                if exc_type is None:
                    raise cleanup_errors[0]

    async def _events(
        self,
        filter_waiters: bool = False,
    ) -> AsyncGenerator[NapCatEvent, None]:
        if not self._conn:
            raise NapCatStateError("Client not connected")
        if not self._connection_running():
            raise NapCatStateError("Client not connected or already closed")

        async for event in self._conn.events():
            event = NapCatEvent.from_dict(event)
            object.__setattr__(event, "_client", self)
            if filter_waiters:
                if self._is_waiter_matched_event(event):
                    continue
                if self.matches_waiters(event):
                    self._remember_waiter_match(event)
                    continue
            yield event

    def events(self, filter_waiters: bool = False) -> AsyncGenerator[NapCatEvent, None]:
        async def _iter() -> AsyncGenerator[NapCatEvent, None]:
            if self._has_external_conn:
                async for event in self._events(filter_waiters=filter_waiters):
                    yield event
                return

            async with self:
                async for event in self._events(filter_waiters=filter_waiters):
                    yield event

        return _iter()

    def __aiter__(self) -> AsyncGenerator[NapCatEvent, None]:
        return self.events()

    def _register_waiter(self, predicate: WaitPredicate) -> object:
        token = object()
        self._waiters.append((token, predicate))
        return token

    def _remove_waiter(self, token: object) -> None:
        for index, (registered_token, _) in enumerate(self._waiters):
            if registered_token is token:
                del self._waiters[index]
                break

    def _event_fingerprint(self, event: NapCatEvent) -> bytes:
        return orjson.dumps(event.to_dict(), option=orjson.OPT_SORT_KEYS)

    def _remember_waiter_match(self, event: NapCatEvent) -> None:
        signature = self._event_fingerprint(event)
        self._matched_waiter_events.pop(signature, None)
        self._matched_waiter_events[signature] = None

        if len(self._matched_waiter_events) > self._matched_waiter_cache_size:
            oldest_signature = next(iter(self._matched_waiter_events))
            del self._matched_waiter_events[oldest_signature]

    def _is_waiter_matched_event(self, event: NapCatEvent) -> bool:
        signature = self._event_fingerprint(event)
        return signature in self._matched_waiter_events

    def _call_waiter_predicate(
        self,
        predicate: WaitPredicate,
        event: NapCatEvent,
        *,
        suppress_exceptions: bool,
    ) -> bool:
        try:
            return bool(predicate(event))
        except Exception:
            if suppress_exceptions:
                logger.exception("Waiter predicate %r failed", predicate)
                return False
            raise

    def _matches_registered_waiters(
        self,
        event: NapCatEvent,
        *,
        suppress_exceptions: bool,
    ) -> bool:
        waiters = tuple(self._waiters)
        for _, predicate in waiters:
            if self._call_waiter_predicate(
                predicate,
                event,
                suppress_exceptions=suppress_exceptions,
            ):
                return True
        return False

    def matches_waiters(self, event: NapCatEvent) -> bool:
        """Return whether any active waiter predicate matches this event."""
        return self._matches_registered_waiters(event, suppress_exceptions=True)

    async def wait_event(
        self,
        predicate: WaitPredicate,
        timeout: float | None = None,
    ) -> NapCatEvent:
        """Wait until the first event satisfying ``predicate`` arrives."""

        token = self._register_waiter(predicate)

        async def _wait() -> NapCatEvent:
            async for event in self.events():
                if self._call_waiter_predicate(
                    predicate,
                    event,
                    suppress_exceptions=False,
                ):
                    self._remember_waiter_match(event)
                    return event
            raise NapCatStateError(
                "Client closed before wait_event received a matching event"
            )

        try:
            if timeout is None:
                return await _wait()
            async with asyncio.timeout(timeout):
                return await _wait()
        finally:
            self._remove_waiter(token)

    async def _send(self, data: dict[str, Any], timeout: float = 10.0) -> dict[str, Any]:
        if not self._conn:
            raise NapCatStateError("Client not connected")
        return await self._conn.send(data, timeout)

    async def call_action(
        self,
        action: str,
        params: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any] | None:
        """
        统一调用入口
        """
        if params is None:
            params = {}

        if (
            action in {"send_private_msg", "send_group_msg", "send_msg"}
            and "message" in params
        ):
            normalized_params = dict(params)
            message_for_send = cast(
                str | list[Message] | Message, normalized_params["message"]
            )
            normalized_params["message"] = self._normalize_message_for_send(
                message_for_send
            )
            params = normalized_params
        elif (
            action
            in {
                "send_forward_msg",
                "send_group_forward_msg",
                "send_private_forward_msg",
            }
            and "messages" in params
        ):
            normalized_params = dict(params)
            message_for_send = cast(
                str | list[Message] | Message, normalized_params["messages"]
            )
            normalized_params["messages"] = self._normalize_message_for_send(
                message_for_send
            )
            params = normalized_params
        elif action == ".handle_quick_operation":
            params = self._normalize_quick_operation_params(params)

        resp = await self._send({"action": action, "params": params})
        if resp.get("status") != "ok" or resp.get("retcode") != 0:
            raise NapCatAPIError(
                f"API call failed: {resp}",
                action=action,
                retcode=resp.get("retcode"),
                response=resp,
            )
        return resp.get("data", None)

    @staticmethod
    def _normalize_message_for_send(
        message: str | list[Message] | Message,
    ) -> str | list[dict[str, Any]] | dict[str, Any]:
        if isinstance(message, str):
            return message
        if isinstance(message, list):
            return [dict(segment) for segment in message]
        return dict(message)

    @classmethod
    def _normalize_quick_operation_params(
        cls,
        params: Mapping[str, Any],
    ) -> dict[str, Any]:
        operation = params.get("operation")
        if not isinstance(operation, Mapping) or "reply" not in operation:
            return dict(params)

        operation_mapping = cast(Mapping[str, Any], operation)
        reply = operation_mapping["reply"]
        if reply is None:
            return dict(params)

        normalized_params: dict[str, Any] = dict(params)
        normalized_operation: dict[str, Any] = dict(operation_mapping)
        normalized_operation["reply"] = cls._normalize_message_for_send(
            cast(str | list[Message] | Message, reply)
        )
        normalized_params["operation"] = normalized_operation
        return normalized_params

    # --- 黑魔法区域 ---

    def __getattr__(self, item: str):
        if item.startswith("_") or item == "send":
            raise AttributeError(item)

        async def dynamic_api_call(**kwargs: Any) -> Mapping[str, Any] | None:
            return await self.call_action(item, kwargs)

        return dynamic_api_call
