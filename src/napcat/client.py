from websockets.asyncio.client import connect as ws_connect

from .connection import Connection


class NapCatClient:
    def __init__(
        self,
        ws_url: str | None = None,
        token: str | None = None,
        _existing_conn: Connection | None = None,
    ):
        # _existing_conn 是给 Server 模式内部使用的
        self.ws_url = ws_url
        self.token = token
        self._conn = _existing_conn
        self._ws_ctx: ws_connect | None = None

    async def __aenter__(self):
        if self._conn:
            await self._conn.__aenter__()
        elif self.ws_url:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            self._ws_ctx = ws_connect(self.ws_url, additional_headers=headers)
            ws = await self._ws_ctx.__aenter__()
            self._conn = Connection(ws)
            await self._conn.__aenter__()
        else:
            raise ValueError("Invalid Client: No URL and no existing connection")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._conn:
            await self._conn.__aexit__(exc_type, exc_val, exc_tb)
        if self._ws_ctx:
            await self._ws_ctx.__aexit__(exc_type, exc_val, exc_tb)
