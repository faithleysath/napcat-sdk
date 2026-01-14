from types import TracebackType
from typing import Any, AsyncGenerator, Mapping

from websockets.asyncio.client import connect as ws_connect

from .connection import Connection
from .types import NapCatEvent
from .client_gen import NapCatClientGenerated


class NapCatClient(NapCatClientGenerated):
    def __init__(
        self,
        ws_url: str | None = None,
        token: str | None = None,
        _existing_conn: Connection | None = None,
    ):
        self.ws_url = ws_url
        self.token = token
        self._conn = _existing_conn
        self._ws_ctx: ws_connect | None = None

    async def __aenter__(self):
        # 如果是 Server 模式（_existing_conn 存在），直接启动该连接的循环
        if self._conn:
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
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        # 级联关闭：Client -> Connection -> WebSocket
        if self._conn:
            await self._conn.__aexit__(exc_type, exc_val, exc_tb)
        if self._ws_ctx:
            await self._ws_ctx.__aexit__(exc_type, exc_val, exc_tb)

    async def events(self) -> AsyncGenerator[NapCatEvent, None]:
        if not self._conn:
            raise RuntimeError("Client not connected")
        async for event in self._conn.events():
            yield NapCatEvent.from_dict(event)

    async def send(self, data: dict[str, Any], timeout: float = 10.0) -> dict[str, Any]:
        if not self._conn:
            raise RuntimeError("Client not connected")
        return await self._conn.send(data, timeout)

    async def call_action(
        self,
        action: str,
        params: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        统一调用入口
        """
        if params is None:
            params = {}
        return await self.send({"action": action, "params": params})


    # --- 黑魔法区域 ---

    def __getattr__(self, item: str):
        if item.startswith("_"):
            raise AttributeError(item)

        async def dynamic_api_call(**kwargs: Any) -> dict[str, Any]:
            return await self.call_action(item, kwargs)

        return dynamic_api_call
