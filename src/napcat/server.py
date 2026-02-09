import asyncio
import logging
from collections.abc import Awaitable, Callable
from types import TracebackType

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
        shutdown_timeout: float = 5.0,
    ):
        """
        :param handler: 一个异步函数，形式为 async def my_handler(client: NapCatClient): ...
        :param host: 监听地址
        :param port: 监听端口
        :param token: 鉴权 Token
        :param shutdown_timeout: 关闭时等待连接结束的超时时间（秒）
        """
        self.handler = handler
        self.host = host
        self.port = port
        self.token = token
        self.shutdown_timeout = shutdown_timeout
        self._server = None
        self._active_tasks: set[asyncio.Task[None]] = set()
        self._stop_event = asyncio.Event()

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

        # 2. 创建连接对象并追踪任务
        conn = Connection(ws)
        client = NapCatClient(_existing_conn=conn)
        current_task = asyncio.current_task()
        if current_task:
            self._active_tasks.add(current_task)

        try:
            async with client:
                await self.handler(client)
        except asyncio.CancelledError:
            logger.info(f"Connection cancelled: {ws.remote_address}")
        except Exception as e:
            logger.error(f"Error in handler for {ws.remote_address}: {e}")
        finally:
            if current_task:
                self._active_tasks.discard(current_task)
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

            # 取消所有活跃连接并等待它们结束
            if self._active_tasks:
                logger.info(f"Cancelling {len(self._active_tasks)} active connections...")
                for task in self._active_tasks:
                    task.cancel()
                # 等待所有任务结束，带超时
                try:
                    await asyncio.wait_for(
                        asyncio.gather(*self._active_tasks, return_exceptions=True),
                        timeout=self.shutdown_timeout
                    )
                except TimeoutError:
                    logger.warning(f"Some connections did not close within {self.shutdown_timeout}s")
                self._active_tasks.clear()

            logger.info("Server closed")

    def stop(self):
        """触发服务器停止，可以从其他协程或信号处理器调用"""
        self._stop_event.set()

    async def run_forever(self):
        """辅助方法：如果用户不想写 async with server，可以直接调这个"""
        async with self:
            # 保持主协程不退出，直到收到停止信号
            await self._stop_event.wait()
