import asyncio
import itertools
import logging
from asyncio import Future, Queue, Task
from typing import AsyncGenerator

import orjson
from websockets.asyncio.client import ClientConnection
from websockets.asyncio.server import ServerConnection

logger = logging.getLogger("napcat.connection")
_STOP = object()


class Connection:
    def __init__(self, ws: ClientConnection | ServerConnection, self_id: int):
        self.ws = ws
        self.self_id = self_id
        self._futures: dict[str, Future] = {}
        self._queues: set[Queue] = set()
        self._task: Task | None = None
        self._counter = itertools.count()
        self._closed = asyncio.Event()

    async def __aenter__(self):
        self._task = asyncio.create_task(self._loop(), name=f"Conn-{self.self_id}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        if self._task and not self._task.done():
            self._task.cancel()
        try:
            await self.ws.close()
        except Exception:
            pass
        await self._closed.wait()

    async def send(self, data: dict, timeout: float = 10.0) -> dict:
        if not self._task or self._task.done():
            raise ConnectionError("Connection closed")
        echo = f"seq-{next(self._counter)}"
        data = data | {"echo": echo}
        fut = asyncio.get_running_loop().create_future()
        self._futures[echo] = fut
        try:
            await self.ws.send(orjson.dumps(data))
            async with asyncio.timeout(timeout):
                return await fut
        finally:
            self._futures.pop(echo, None)

    async def events(self) -> AsyncGenerator[dict, None]:
        q = Queue(maxsize=500)
        self._queues.add(q)
        try:
            while True:
                data = await q.get()
                if data is _STOP:
                    break
                yield data
        finally:
            self._queues.discard(q)

    async def _loop(self):
        logger.info(f"Conn {self.self_id} start.")
        try:
            async for msg in self.ws:
                try:
                    data = orjson.loads(msg)
                except orjson.JSONDecodeError:
                    continue
                if echo := data.get("echo"):
                    if fut := self._futures.get(echo):
                        if not fut.done():
                            fut.set_result(data)
                else:
                    self._broadcast(data)
        except (asyncio.CancelledError, Exception):
            pass
        finally:
            await self._cleanup()

    async def _cleanup(self):
        for f in self._futures.values():
            if not f.done():
                f.set_exception(ConnectionError("Conn closed"))
        self._futures.clear()
        self._broadcast(_STOP)
        self._queues.clear()
        self._closed.set()
        logger.info(f"Conn {self.self_id} closed.")

    def _broadcast(self, item):
        for q in list(self._queues):
            if q.full():
                q.get_nowait()
            try:
                q.put_nowait(item)
            except Exception:
                pass
