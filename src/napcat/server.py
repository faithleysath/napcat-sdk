import logging
from asyncio import Queue
from typing import AsyncGenerator

from websockets.asyncio.server import ServerConnection, serve

from .client import NapCatClient
from .connection import Connection

logger = logging.getLogger("napcat.server")


class ReverseWebSocketServer:
    def __init__(
        self, host: str = "0.0.0.0", port: int = 8080, token: str | None = None
    ):
        self.host = host
        self.port = port
        self.token = token
        self._server = None
        self._new_clients: Queue[NapCatClient] = Queue()

    async def _handle_connection(self, ws: ServerConnection):
        if ws.request is not None:
            req_token = ws.request.headers.get("Authorization", "").replace(
                "Bearer ", ""
            )
            if self.token and req_token != self.token:
                logger.warning("Auth failed for incoming connection")
                return
        else:
            logger.warning("No request found for incoming connection")
            return

        conn = Connection(ws)
        client = NapCatClient(_existing_conn=conn)

        self._new_clients.put_nowait(client)

        await conn._closed.wait()

    async def __aenter__(self):
        logger.info(f"NapCat Server listening on {self.host}:{self.port}")
        self._server = await serve(self._handle_connection, self.host, self.port)
        return self

    async def close(self):
        if self._server:
            self._server.close()
            await self._server.wait_closed()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def accept(self) -> AsyncGenerator[NapCatClient, None]:
        """
        异步生成器：不断产出新连接的 Client。
        """
        while True:
            client = await self._new_clients.get()
            yield client
