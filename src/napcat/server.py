import asyncio
import logging
from types import TracebackType
from typing import Awaitable, Callable

from websockets.asyncio.server import ServerConnection, serve

from .client import NapCatClient
from .connection import Connection

logger = logging.getLogger("napcat.server")

# 定义回调函数的类型：接收一个 NapCatClient，返回 Awaitable[None]
HandlerType = Callable[[NapCatClient], Awaitable[None]]


class ReverseWebSocketServer:
    def __init__(
        self,
        handler: HandlerType,
        host: str = "0.0.0.0",
        port: int = 8080,
        token: str | None = None,
    ):
        """
        :param handler: 一个异步函数，形式为 async def my_handler(client: NapCatClient): ...
        :param host: 监听地址
        :param port: 监听端口
        :param token: 鉴权 Token
        """
        self.handler = handler
        self.host = host
        self.port = port
        self.token = token
        self._server = None

    async def _handle_connection(self, ws: ServerConnection):
        # 1. 鉴权逻辑
        if ws.request is not None:
            req_token = ws.request.headers.get("Authorization", "").removeprefix(
                "Bearer "
            )
            if self.token and req_token != self.token:
                await ws.close(code=4001, reason="Auth Failed")
                logger.warning(f"Auth failed from {ws.remote_address}")
                return
        else:
            logger.warning(f"No request header from {ws.remote_address}")
            return

        # 2. 创建连接对象
        conn = Connection(ws)
        client = NapCatClient(_existing_conn=conn)

        try:
            async with client:
                await self.handler(client)
        except Exception as e:
            logger.error(f"Error in handler for {ws.remote_address}: {e}")
        finally:
            logger.info(f"Connection disconnected: {ws.remote_address}")

    async def __aenter__(self):
        logger.info(f"NapCat Server listening on {self.host}:{self.port}")
        self._server = await serve(self._handle_connection, self.host, self.port)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        await self.close()

    async def close(self):
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            logger.info("Server closed")

    async def run_forever(self):
        """辅助方法：如果用户不想写 async with server，可以直接调这个"""
        async with self:
            # 保持主协程不退出，直到收到停止信号
            await asyncio.get_running_loop().create_future()
