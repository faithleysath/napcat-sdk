"""
NapCat 客户端实现

提供 NapCatClient 类，用于与 NapCatQQ 建立连接（正向 WebSocket）或复用现有连接（反向 WebSocket）。
包含事件生成器 (_events) 和 API 调用方法 (call_action)。
"""

import asyncio
from collections.abc import AsyncGenerator, Mapping
from types import TracebackType
from typing import Any, cast

from websockets.asyncio.client import connect as ws_connect

from .client_api import NapCatAPIMixin
from .connection import Connection
from .types import NapCatEvent
from .types.messages import Message


class NapCatClient(NapCatAPIMixin):
    def __init__(
        self,
        ws_url: str | None = None,
        token: str | None = None,
        _existing_conn: Connection | None = None,
    ):
        self.ws_url = ws_url
        self.token = token
        self._conn = _existing_conn
        self._has_external_conn = _existing_conn is not None
        self._ws_ctx: ws_connect | None = None
        self._entered = False
        self._context_refs = 0
        self._lifecycle_lock = asyncio.Lock()
        self.self_id: int = -1  # 连接后更新

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
                # 如果是 Server 模式（_existing_conn 存在），直接启动该连接的循环
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
                except Exception as e:
                    print(f"Warning: Failed to get self_id: {e}")
                    self.self_id = -1
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

            # 如果有清理错误，记录并抛出第一个
            if cleanup_errors:
                for err in cleanup_errors:
                    import logging

                    logging.getLogger("napcat.client").warning(f"Cleanup error: {err}")
                if exc_type is None:
                    raise cleanup_errors[0]

    async def _events(self) -> AsyncGenerator[NapCatEvent, None]:
        if not self._conn:
            raise RuntimeError("Client not connected")
        if not self._connection_running():
            raise RuntimeError("Client not connected or already closed")

        async for event in self._conn.events():
            event = NapCatEvent.from_dict(event)
            object.__setattr__(event, "_client", self)
            yield event

    def __aiter__(self) -> AsyncGenerator[NapCatEvent, None]:
        async def _iter() -> AsyncGenerator[NapCatEvent, None]:
            if self._has_external_conn:
                async for event in self._events():
                    yield event
                return

            async with self:
                async for event in self._events():
                    yield event

        return _iter()

    async def send(self, data: dict[str, Any], timeout: float = 10.0) -> dict[str, Any]:
        if not self._conn:
            raise RuntimeError("Client not connected")
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

        if action in {"send_private_msg", "send_group_msg", "send_msg"} and "message" in params:
            normalized_params = dict(params)
            message_for_send = cast(
                str | list[Message] | Message, normalized_params["message"]
            )
            normalized_params["message"] = self._normalize_message_for_send(
                message_for_send
            )
            params = normalized_params

        resp = await self.send({"action": action, "params": params})
        if resp.get("status") != "ok" or resp.get("retcode") != 0:
            raise RuntimeError(f"API call failed: {resp}")
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

    # --- 黑魔法区域 ---

    def __getattr__(self, item: str):
        if item.startswith("_"):
            raise AttributeError(item)

        async def dynamic_api_call(**kwargs: Any) -> Mapping[str, Any] | None:
            return await self.call_action(item, kwargs)

        return dynamic_api_call
