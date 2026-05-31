"""
WebSocket 连接管理

Connection 类封装了底层的 WebSocket 连接，处理消息收发、请求响应匹配 (Echo 机制) 和事件分发。
"""

import asyncio
import logging
import uuid
from asyncio import Future, Queue, Task
from collections.abc import AsyncGenerator
from types import TracebackType
from typing import Any, cast

import orjson
from websockets.asyncio.client import ClientConnection
from websockets.asyncio.server import ServerConnection

from .exceptions import NapCatStateError

logger = logging.getLogger("napcat.connection")
_STOP = object()


class Connection:
    def __init__(self, ws: ClientConnection | ServerConnection):
        self.ws = ws
        self._futures: dict[str, Future[dict[str, Any]]] = {}

        # event_queues: 仅存储 OneBot 事件 (给 Python Client 用)
        self._event_queues: set[Queue[dict[str, Any] | object]] = set()

        self._task: Task[None] | None = None
        self._closed = asyncio.Event()

    async def __aenter__(self):
        # 幂等保护：如果已经在运行，直接返回
        if self._task is not None and not self._task.done():
            return self
        # 重置 _closed 事件（支持重复进入）
        self._closed.clear()
        self._task = asyncio.create_task(self._loop())
        return self

    @property
    def is_running(self) -> bool:
        return self._task is not None and not self._task.done()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        await self.close()

    async def close(self):
        # 如果 _loop 从未启动，直接设置 _closed 并返回
        if self._task is None:
            self._closed.set()
            try:
                await self.ws.close()
            except Exception:
                pass
            return

        # 正常关闭路径
        task = self._task
        if not task.done():
            task.cancel()
        try:
            await self.ws.close()
        except Exception:
            pass
        if task is not asyncio.current_task():
            try:
                await task
            except asyncio.CancelledError:
                pass
        if not self._closed.is_set():
            await self._cleanup()

    async def send(self, data: dict[str, Any], timeout: float = 10.0) -> dict[str, Any]:
        """Python 内部调用：自动挂载 UUID echo 并等待结果。"""
        if not self._task or self._task.done():
            raise NapCatStateError("Connection closed")
        echo = f"py-{uuid.uuid4()}"
        data = data | {"echo": echo}
        fut: Future[dict[str, Any]] = asyncio.get_running_loop().create_future()
        self._futures[echo] = fut
        try:
            async with asyncio.timeout(timeout):
                await self.ws.send(orjson.dumps(data))
                return await fut
        finally:
            self._futures.pop(echo, None)

    async def events(self) -> AsyncGenerator[dict[str, Any], None]:
        """仅产出 OneBot 事件 (给 Python Client)，过滤所有 API 响应。"""
        q: Queue[dict[str, Any] | object] = Queue(maxsize=500)
        self._event_queues.add(q)
        try:
            while True:
                data = await q.get()
                if data is _STOP:
                    break
                if isinstance(data, dict):
                    yield data
        finally:
            self._event_queues.discard(q)

    async def _loop(self) -> None:
        cancelled = False
        try:
            async for msg in self.ws:
                try:
                    data = orjson.loads(msg)
                    if not isinstance(data, dict) or not data:
                        continue
                    data = cast(dict[str, Any], data)
                except orjson.JSONDecodeError:
                    continue

                echo = data.get("echo")

                if echo:
                    if fut := self._futures.get(echo):
                        if not fut.done():
                            fut.set_result(data)
                    continue
                else:
                    self._dispatch(self._event_queues, data)

        except asyncio.CancelledError:
            cancelled = True
        except Exception as e:
            logger.error("Connection loop error: %s", e)
        finally:
            await self._cleanup()
            if cancelled:
                raise asyncio.CancelledError()

    async def _cleanup(self):
        for f in self._futures.values():
            if not f.done():
                f.set_exception(NapCatStateError("Connection closed"))
        self._futures.clear()

        self._dispatch(self._event_queues, _STOP)
        self._event_queues.clear()
        self._closed.set()

    def _dispatch(self, queues: set[Queue[dict[str, Any] | object]], item: dict[str, Any] | object) -> None:
        """向一组队列广播消息，满队列时丢弃最旧消息。"""
        for q in list(queues):
            if q.full():
                try:
                    q.get_nowait()
                    logger.debug("Queue full, dropped oldest message")
                except asyncio.QueueEmpty:
                    pass
            try:
                q.put_nowait(item)
            except Exception:
                pass
