import asyncio
from collections.abc import AsyncGenerator, Mapping
from types import TracebackType
from typing import Any, cast

from websockets.asyncio.client import connect as ws_connect

from .client_api import NapCatAPI
from .connection import Connection
from .types import NapCatEvent
from .types.messages import Message


class NapCatClient:
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
        self._auto_iter_refs = 0
        self._lifecycle_lock = asyncio.Lock()

        self.api = NapCatAPI(self)
        self.self_id: int = -1  # 连接后更新

    def _connection_running(self) -> bool:
        return bool(self._conn and self._conn.is_running)

    async def __aenter__(self):
        if self._entered and self._connection_running():
            return self

        # 如果是 Server 模式（_existing_conn 存在），直接启动该连接的循环
        if self._has_external_conn:
            if not self._conn:
                raise ValueError("Invalid Client: Missing existing connection")
            await self._conn.__aenter__()
        # 如果是 Client 模式（主动连接），建立连接并包装
        elif self.ws_url:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            self._ws_ctx = ws_connect(self.ws_url, additional_headers=headers)
            ws = await self._ws_ctx.__aenter__()
            self._conn = Connection(ws)
            await self._conn.__aenter__()
        else:
            raise ValueError("Invalid Client: No URL and no existing connection")

        self._entered = True
        # 2. 获取自身 ID (增加容错处理)
        try:
            resp = await self.api.get_login_info()
            self.self_id = resp['user_id']

        except Exception as e:
            print(f"Warning: Failed to get self_id: {e}")
            self.self_id = -1
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        # 级联关闭：Client -> Connection -> WebSocket
        conn = self._conn
        ws_ctx = self._ws_ctx

        if conn:
            await conn.__aexit__(exc_type, exc_val, exc_tb)
        if ws_ctx:
            await ws_ctx.__aexit__(exc_type, exc_val, exc_tb)

        self._entered = False
        if not self._has_external_conn:
            self._conn = None
        self._ws_ctx = None

    async def events(self) -> AsyncGenerator[NapCatEvent, None]:
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
            should_manage_lifecycle = not self._has_external_conn
            acquired_ref = False

            if should_manage_lifecycle:
                async with self._lifecycle_lock:
                    self._auto_iter_refs += 1
                    acquired_ref = True
                    try:
                        if self._auto_iter_refs == 1:
                            await self.__aenter__()
                    except Exception:
                        self._auto_iter_refs -= 1
                        acquired_ref = False
                        raise

            try:
                async for event in self.events():
                    yield event
            finally:
                if should_manage_lifecycle and acquired_ref:
                    async with self._lifecycle_lock:
                        self._auto_iter_refs -= 1
                        if self._auto_iter_refs == 0:
                            await self.__aexit__(None, None, None)

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

        if action in {"send_private_msg", "send_group_msg"} and "message" in params:
            normalized_params = dict(params)
            message_for_send = cast(str | list[Message] | Message, normalized_params["message"])
            normalized_params["message"] = self._normalize_message_for_send(message_for_send)
            params = normalized_params

        resp = await self.send({"action": action, "params": params})
        if resp.get("status") != "ok" and resp.get("retcode") != 0:
            raise RuntimeError(f"API call failed: {resp}")
        return resp.get("data", None)

    @staticmethod
    def _normalize_message_for_send(message: str | list[Message] | Message) -> str | list[dict[str, Any]] | dict[str, Any]:
        if isinstance(message, str):
            return message
        if isinstance(message, list):
            return [dict(segment) for segment in message]
        return dict(message)

    async def send_private_msg(self, user_id: int, message: str | list[Message] | Message) -> int:
        """
        发送私聊消息，返回消息 ID
        """
        resp = await self.api.send_private_msg(
            user_id=str(user_id),
            message=message
        )
        return resp["message_id"]

    async def send_group_msg(self, group_id: int, message: str | list[Message] | Message) -> int:
        """
        发送群消息，返回消息 ID
        """
        resp = await self.api.send_group_msg(
            group_id=str(group_id),
            message=message
        )
        return resp["message_id"]


    # --- 黑魔法区域 ---

    def __getattr__(self, item: str):
        if item.startswith("_"):
            raise AttributeError(item)

        async def dynamic_api_call(**kwargs: Any) -> Mapping[str, Any] | None:
            return await self.call_action(item, kwargs)

        return dynamic_api_call
