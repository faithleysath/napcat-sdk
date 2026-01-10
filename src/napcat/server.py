import asyncio
import logging
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
        # 用于追踪当前活跃的处理任务，以便优雅关闭
        self._active_tasks: set[asyncio.Task] = set()

    async def _handle_connection(self, ws: ServerConnection):
        # 1. 鉴权逻辑
        if ws.request is not None:
            req_token = ws.request.headers.get("Authorization", "").removeprefix(
                "Bearer "
            )
            if self.token and req_token != self.token:
                logger.warning(f"Auth failed from {ws.remote_address}")
                return
        else:
            logger.warning(f"No request header from {ws.remote_address}")
            return

        # 2. 创建连接对象
        conn = Connection(ws)
        client = NapCatClient(_existing_conn=conn)

        # 3. 【关键改动】在这里直接激活生命周期
        # 使用 async with 自动启动 Connection._loop，并在退出时自动关闭连接
        try:
            async with client:
                # 调用用户的回调函数，把“活”的 client 传过去
                # 我们在这个作用域内等待用户逻辑执行完毕
                await self.handler(client)
        except Exception as e:
            logger.error(f"Error in handler for {ws.remote_address}: {e}")
        finally:
            # async with 结束会自动调用 client.__aexit__ -> conn.close()
            # 这里不需要额外操作
            logger.info(f"Connection disconnected: {ws.remote_address}")

    async def __aenter__(self):
        logger.info(f"NapCat Server listening on {self.host}:{self.port}")
        # 启动 WebSocket 服务器
        self._server = await serve(self._handle_connection, self.host, self.port)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
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
