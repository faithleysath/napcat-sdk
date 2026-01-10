import asyncio
import itertools
import json
import logging
from asyncio import Future, Queue, Task
from typing import Any, AsyncGenerator

from websockets.asyncio.client import ClientConnection
from websockets.asyncio.server import ServerConnection
from websockets.exceptions import ConnectionClosed

type WSConnection = ClientConnection | ServerConnection
type JsonData = dict[str, Any]

logger = logging.getLogger("napcat.connection")

_STOP_SIGNAL = object()


class Connection:
    def __init__(self, ws: WSConnection, self_id: int):
        self.ws = ws
        self.self_id = self_id
        self._futures: dict[str, Future[JsonData]] = {}
        self._subscribers: set[Queue[JsonData | object]] = set()

        self._stop_requested = asyncio.Event()
        self._closed_complete = asyncio.Event()
        self._listen_task: Task | None = None
        self._echo_counter = itertools.count()

    def start(self):
        if self._stop_requested.is_set():
            raise RuntimeError("Connection cannot be restarted")
        if not self._listen_task or self._listen_task.done():
            self._listen_task = asyncio.create_task(
                self._loop(), name=f"Conn-{self.self_id}-Loop"
            )

    async def wait_closed(self):
        if not self._listen_task:
            return
        await self._closed_complete.wait()

    async def _cleanup(self):
        self._stop_requested.set()

        for future in list(self._futures.values()):
            if not future.done():
                future.set_exception(ConnectionError("Connection closed"))
        self._futures.clear()

        for q in list(self._subscribers):
            self._push_to_specific_queue(q, _STOP_SIGNAL)

        self._subscribers.clear()

        self._closed_complete.set()

    async def close(self):
        if self._stop_requested.is_set():
            await self.wait_closed()
            return

        self._stop_requested.set()

        try:
            async with asyncio.timeout(2.0):
                await self.ws.close()
        except Exception:
            if self._listen_task:
                self._listen_task.cancel()
        finally:
            if self._listen_task and not self._listen_task.done():
                self._listen_task.cancel()

        if self._listen_task:
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
        else:
            await self._cleanup()

        await self.wait_closed()

    async def send(self, data: JsonData, timeout: float = 10.0) -> JsonData:
        if not self._listen_task or self._listen_task.done():
            raise RuntimeError("Connection is not running")
        data = data.copy()
        if self._stop_requested.is_set():
            raise ConnectionError("Connection is closing/closed")
        data["echo"] = f"seq-{next(self._echo_counter)}"
        echo_id = data["echo"]
        loop = asyncio.get_running_loop()
        future: Future[JsonData] = loop.create_future()
        self._futures[echo_id] = future
        try:
            payload = json.dumps(data)
            async with asyncio.timeout(timeout):
                await self.ws.send(payload)
                return await future
        except Exception:
            raise
        finally:
            self._futures.pop(echo_id, None)

    async def events(self) -> AsyncGenerator[JsonData, None]:
        local_queue: Queue[JsonData | object] = Queue(maxsize=1000)
        self._subscribers.add(local_queue)

        try:
            while True:
                if self._stop_requested.is_set() and local_queue.empty():
                    break

                try:
                    data = await local_queue.get()
                except asyncio.CancelledError:
                    break

                if data is _STOP_SIGNAL:
                    break

                if isinstance(data, dict):
                    yield data
        finally:
            self._subscribers.discard(local_queue)
            while not local_queue.empty():
                try:
                    local_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

    async def _loop(self):
        logger.info(f"Connection {self.self_id} started listening.")
        try:
            async for message in self.ws:
                if self._stop_requested.is_set():
                    break

                data = await self._parse_message(message)
                if data is None:
                    logger.warning("Received no data")
                    continue
                if not isinstance(data, dict):
                    logger.warning(f"Received invalid JSON content: {data}")
                    continue
                if "echo" in data:
                    echo_id = data["echo"]
                    if future := self._futures.pop(echo_id, None):
                        if not future.done():
                            future.set_result(data)
                    else:
                        logger.debug(f"Dropped late or unknown response: {echo_id}")
                else:
                    for q in list(self._subscribers):
                        self._push_to_specific_queue(q, data)

        except (OSError, asyncio.CancelledError, ConnectionClosed) as e:
            if not self._stop_requested.is_set():
                logger.debug(f"Connection loop stopped: {e}")
        except Exception as e:
            logger.error(f"Connection loop unexpected error: {e}", exc_info=True)
        finally:
            await self._cleanup()

    def _push_to_specific_queue(self, q: Queue, item: Any):
        try:
            q.put_nowait(item)
        except asyncio.QueueFull:
            logger.warning(
                f"Consumer queue full, dropping oldest event to make room. qsize={q.qsize()}"
            )
            try:
                q.get_nowait()
            except asyncio.QueueEmpty:
                pass

            try:
                q.put_nowait(item)
            except asyncio.QueueFull:
                logger.warning("Consumer too slow: Event queue overflow, item dropped.")

    async def _parse_message(self, message: str | bytes) -> JsonData | None:
        try:
            return json.loads(message)
        except json.JSONDecodeError:
            logger.warning("Received invalid JSON content")
            return None
        except Exception as e:
            logger.error(f"Message parsing failed: {e}")
            return None

    async def __aenter__(self):
        self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
