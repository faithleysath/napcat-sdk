"""
NapCat 客户端实现

提供 NapCatClient 类，用于与 NapCatQQ 建立连接（正向 WebSocket）或复用现有连接（反向 WebSocket）。
包含事件生成器 (_events) 和 API 调用方法 (call_action)。
支持 RPC Server 模式，可作为透明 WebSocket 网关使用。
"""

import asyncio
import logging
import secrets
from collections.abc import AsyncGenerator, Mapping
from types import TracebackType
from typing import Any, cast
from urllib.parse import parse_qs, urlparse

import orjson
from websockets.asyncio.client import connect as ws_connect
from websockets.asyncio.server import Server as WsServer
from websockets.asyncio.server import ServerConnection
from websockets.asyncio.server import serve as ws_serve

from .client_api import NapCatAPIMixin
from .connection import Connection
from .exceptions import NapCatAPIError, NapCatError, NapCatStateError
from .types import NapCatEvent
from .types.messages import Message

logger = logging.getLogger("napcat.client")


class NapCatClient(NapCatAPIMixin):
    def __init__(
        self,
        ws_url: str | None = None,
        token: str | None = None,
        _existing_conn: Connection | None = None,
        # --- RPC Mode 参数 ---
        rpc_mode: bool = False,
        rpc_host: str = "0.0.0.0",
        rpc_port: int = 0,
        rpc_token: str | None = None,
    ):
        self.ws_url = ws_url
        self.token = token
        self._conn = _existing_conn
        self._has_external_conn = _existing_conn is not None
        self._ws_ctx: ws_connect | None = None
        self._entered = False
        self._context_refs = 0
        self._lifecycle_lock = asyncio.Lock()
        self.self_id: int = -1  # 连接后更新

        # --- RPC 状态 ---
        self.rpc_mode = rpc_mode
        self.rpc_host = rpc_host
        self._rpc_port_config = rpc_port
        self.rpc_port = rpc_port
        # Token: None -> 随机生成; "" -> 无鉴权; "xxx" -> 指定
        if rpc_mode and rpc_token is None:
            self.rpc_token: str | None = secrets.token_urlsafe(16)
        else:
            self.rpc_token = rpc_token
        self._rpc_server: WsServer | None = None
        self._rpc_tasks: list[asyncio.Task[None]] = []
        self._rpc_clients: set[ServerConnection] = set()

    def _connection_running(self) -> bool:
        return bool(self._conn and self._conn.is_running)

    @property
    def is_running(self) -> bool:
        return self._connection_running()

    async def __aenter__(self):
        async with self._lifecycle_lock:
            self._context_refs += 1

            # 已有活跃连接时，仅增加上下文引用计数即可
            # 不依赖引用计数值判断复用，直接以连接运行状态为准
            if self._connection_running():
                self._entered = True
                return self

            # 用于跟踪已打开的资源，便于异常时回滚
            ws_ctx_entered = False
            conn_entered = False

            try:
                # 如果是 Server 模式（_existing_conn 存在），直接启动该连接的循环
                if self._has_external_conn:
                    if not self._conn:
                        raise ValueError("Invalid Client: Missing existing connection")
                    await self._conn.__aenter__()
                    conn_entered = True
                # 如果是 Client 模式（主动连接），建立连接并包装
                elif self.ws_url:
                    headers = (
                        {"Authorization": f"Bearer {self.token}"} if self.token else {}
                    )
                    self._ws_ctx = ws_connect(self.ws_url, additional_headers=headers)
                    ws = await self._ws_ctx.__aenter__()
                    ws_ctx_entered = True
                    self._conn = Connection(ws)
                    await self._conn.__aenter__()
                    conn_entered = True
                else:
                    raise ValueError(
                        "Invalid Client: No URL and no existing connection"
                    )

                self._entered = True
                # 获取自身 ID (增加容错处理)
                try:
                    resp = await self.get_login_info()
                    self.self_id = resp["user_id"]
                except NapCatError as e:
                    logger.warning("Failed to get self_id: %s", e)
                    self.self_id = -1

                # 启动 RPC 服务
                if self.rpc_mode:
                    await self._start_rpc()

                return self
            except Exception:
                # 异常时回滚已打开的资源
                # 注: _start_rpc 内部失败时已自行调用 _stop_rpc，无需重复
                if conn_entered and self._conn:
                    try:
                        await self._conn.__aexit__(None, None, None)
                    except Exception:
                        pass
                if ws_ctx_entered and self._ws_ctx:
                    try:
                        await self._ws_ctx.__aexit__(None, None, None)
                    except Exception:
                        pass
                # 清理状态
                if not self._has_external_conn:
                    self._conn = None
                self._ws_ctx = None
                self._context_refs -= 1
                if self._context_refs == 0:
                    self._entered = False
                raise

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        async with self._lifecycle_lock:
            if self._context_refs == 0:
                return

            self._context_refs -= 1
            if self._context_refs > 0:
                return

            # 关闭 RPC 服务
            if self.rpc_mode:
                await self._stop_rpc()

            # 级联关闭：Client -> Connection -> WebSocket
            conn = self._conn
            ws_ctx = self._ws_ctx
            cleanup_errors: list[BaseException] = []

            try:
                if conn:
                    try:
                        await conn.__aexit__(exc_type, exc_val, exc_tb)
                    except Exception as e:
                        cleanup_errors.append(e)
                # 仅在 Client 模式下关闭 ws_ctx（Server 模式由外部管理）
                if ws_ctx and not self._has_external_conn:
                    try:
                        await ws_ctx.__aexit__(exc_type, exc_val, exc_tb)
                    except Exception as e:
                        cleanup_errors.append(e)
            finally:
                self._entered = False
                if not self._has_external_conn:
                    self._conn = None
                self._ws_ctx = None

            if cleanup_errors:
                for err in cleanup_errors:
                    logger.warning("Cleanup error: %s", err)
                if exc_type is None:
                    raise cleanup_errors[0]

    async def _events(self) -> AsyncGenerator[NapCatEvent, None]:
        if not self._conn:
            raise NapCatStateError("Client not connected")
        if not self._connection_running():
            raise NapCatStateError("Client not connected or already closed")

        async for event in self._conn.events():
            event = NapCatEvent.from_dict(event)
            object.__setattr__(event, "_client", self)
            yield event

    def __aiter__(self) -> AsyncGenerator[NapCatEvent, None]:
        async def _iter() -> AsyncGenerator[NapCatEvent, None]:
            if self._has_external_conn:
                async for event in self._events():
                    yield event
                return

            async with self:
                async for event in self._events():
                    yield event

        return _iter()

    async def send(self, data: dict[str, Any], timeout: float = 10.0) -> dict[str, Any]:
        if not self._conn:
            raise NapCatStateError("Client not connected")
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

        if action in {"send_private_msg", "send_group_msg", "send_msg"} and "message" in params:
            normalized_params = dict(params)
            message_for_send = cast(
                str | list[Message] | Message, normalized_params["message"]
            )
            normalized_params["message"] = self._normalize_message_for_send(
                message_for_send
            )
            params = normalized_params

        resp = await self.send({"action": action, "params": params})
        if resp.get("status") != "ok" or resp.get("retcode") != 0:
            raise NapCatAPIError(
                f"API call failed: {resp}",
                action=action,
                retcode=resp.get("retcode"),
                response=resp,
            )
        return resp.get("data", None)

    @staticmethod
    def _normalize_message_for_send(
        message: str | list[Message] | Message,
    ) -> str | list[dict[str, Any]] | dict[str, Any]:
        if isinstance(message, str):
            return message
        if isinstance(message, list):
            return [dict(segment) for segment in message]
        return dict(message)

    # --- 黑魔法区域 ---

    def __getattr__(self, item: str):
        if item.startswith("_"):
            raise AttributeError(item)

        async def dynamic_api_call(**kwargs: Any) -> Mapping[str, Any] | None:
            return await self.call_action(item, kwargs)

        return dynamic_api_call

    # === RPC 实现 ===

    async def _rpc_client_handler(self, websocket: ServerConnection) -> None:
        """处理单个 RPC 客户端连接：鉴权 → 注册 → 透传消息。"""
        # 鉴权
        if self.rpc_token:
            request = websocket.request
            if request is None:
                try:
                    await websocket.close(code=4000, reason="No request")
                except Exception:
                    pass
                return
            auth_header = request.headers.get("Authorization", "")
            parsed = urlparse(request.path)
            token_in_url = secrets.compare_digest(
                parse_qs(parsed.query).get("token", [""])[0], self.rpc_token
            )
            bearer_valid = secrets.compare_digest(
                auth_header, f"Bearer {self.rpc_token}"
            )

            if not (bearer_valid or token_in_url):
                logger.warning("RPC client %s auth failed", websocket.remote_address)
                try:
                    await websocket.close(code=4001, reason="Unauthorized")
                except Exception:
                    pass
                return

        self._rpc_clients.add(websocket)
        try:
            async for message in websocket:
                if not self._connection_running():
                    break
                try:
                    data = orjson.loads(message)
                    if not isinstance(data, dict):
                        continue
                    data = cast(dict[str, Any], data)
                    if self._conn:
                        await self._conn.send_raw(data)
                except (orjson.JSONDecodeError, OSError, NapCatStateError):
                    continue
        except Exception as e:
            logger.debug("RPC client %s disconnected: %s", websocket.remote_address, e)
        finally:
            self._rpc_clients.discard(websocket)

    async def _rpc_broadcaster(self) -> None:
        """将 proxy_stream 广播给所有 RPC 客户端。"""
        if not self._conn:
            return

        async for data in self._conn.proxy_stream():
            if not self._rpc_clients:
                continue

            msg_bytes = orjson.dumps(data)
            clients = list(self._rpc_clients)
            results = await asyncio.gather(
                *[ws.send(msg_bytes) for ws in clients],
                return_exceptions=True,
            )
            for client, result in zip(clients, results, strict=True):
                if isinstance(result, Exception):
                    self._rpc_clients.discard(client)
                    try:
                        await client.close()
                    except Exception:
                        pass

    async def _start_rpc(self) -> None:
        """启动 RPC WebSocket 服务器。"""
        if not self.rpc_mode:
            return

        logger.info("Starting RPC server on %s:%d...", self.rpc_host, self._rpc_port_config)
        try:
            self._rpc_server = await ws_serve(
                self._rpc_client_handler,
                self.rpc_host,
                self._rpc_port_config,
                ping_interval=20,
                ping_timeout=20,
            )
            for sock in self._rpc_server.sockets:
                self.rpc_port = sock.getsockname()[1]
                break

            logger.info("RPC server running at ws://%s:%d", self.rpc_host, self.rpc_port)
            if self.rpc_token:
                logger.debug("RPC token: %s...", self.rpc_token[:6])

            self._rpc_tasks.append(asyncio.create_task(self._rpc_broadcaster()))
        except Exception:
            await self._stop_rpc()
            raise

    async def _stop_rpc(self) -> None:
        """停止 RPC 服务。"""
        for task in self._rpc_tasks:
            task.cancel()
        if self._rpc_tasks:
            await asyncio.wait(self._rpc_tasks, timeout=2)
        self._rpc_tasks.clear()

        if self._rpc_clients:
            await asyncio.gather(
                *[ws.close() for ws in self._rpc_clients],
                return_exceptions=True,
            )
            self._rpc_clients.clear()

        if self._rpc_server:
            self._rpc_server.close()
            await self._rpc_server.wait_closed()
            self._rpc_server = None
