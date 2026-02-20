"""
Gateway Unix Socket 服务器

提供 Gateway 守护进程的核心服务，处理 CLI 请求并管理 NapCat 连接。
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any

from websockets.asyncio.server import ServerConnection, serve

from napcat.client import NapCatClient

from .protocol import GatewayError, GatewayRequest, GatewayResponse
from .webhook import WebhookDispatcher

if TYPE_CHECKING:
    from ..config import WebhookConfig

logger = logging.getLogger("napcat.gateway")


class Gateway:
    """
    Gateway 守护进程服务

    负责:
    1. 连接 NapCat WebSocket
    2. 监听 Unix Socket 处理 CLI 请求
    3. 分发事件到 Webhook
    """

    def __init__(
        self,
        instance_name: str,
        ws_url: str,
        token: str | None = None,
        socket_path: Path | None = None,
        log_level: str = "INFO",
    ):
        self.instance_name = instance_name
        self.ws_url = ws_url
        self.token = token
        self.socket_path = socket_path or Path.home() / ".napcat" / instance_name / "gateway.sock"
        self.log_level = log_level

        self._client: NapCatClient | None = None
        self._webhooks: WebhookDispatcher = WebhookDispatcher()
        self._running = False
        self._server_task: asyncio.Task[None] | None = None

        # 配置日志
        logging.basicConfig(
            level=getattr(logging, log_level.upper(), logging.INFO),
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )

    async def start(self) -> None:
        """启动 Gateway"""
        logger.info("Starting Gateway for instance: %s", self.instance_name)
        logger.info("Connecting to NapCat at: %s", self.ws_url)

        self._running = True

        # 创建 NapCat 客户端
        self._client = NapCatClient(
            ws_url=self.ws_url,
            token=self.token,
        )

        try:
            async with self._client:
                # 启动事件处理协程
                asyncio.create_task(self._event_handler())

                # 启动 Unix Socket 服务器
                await self._run_socket_server()
        except Exception as e:
            logger.error("Gateway error: %s", e)
            raise

    async def _run_socket_server(self) -> None:
        """运行 Unix Socket 服务器"""
        # 确保目录存在
        self.socket_path.parent.mkdir(parents=True, exist_ok=True)

        # 删除已存在的 socket 文件
        if self.socket_path.exists():
            self.socket_path.unlink()

        async with serve(
            self._handle_cli_connection,
            unix=True,
            path=str(self.socket_path),
        ) as server:
            # 设置 socket 权限
            self.socket_path.chmod(0o600)

            logger.info("Gateway listening on %s", self.socket_path)

            try:
                while self._running:
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                pass
            finally:
                logger.info("Gateway shutting down...")
                server.close()
                await server.wait_closed()

    async def _handle_cli_connection(self, ws: ServerConnection) -> None:
        """处理 CLI 连接"""
        logger.debug("CLI connected from %s", ws.remote_address)

        try:
            async for message in ws:
                try:
                    req = GatewayRequest.from_json(message)
                    resp = await self._handle_request(req)
                    await ws.send(resp.to_json())
                except GatewayError as e:
                    error_resp = GatewayResponse.error_response(
                        code=e.code,
                        message=str(e),
                        data=e.data,
                    )
                    await ws.send(error_resp.to_json())
                except Exception as e:
                    logger.error("Error handling request: %s", e)
                    error_resp = GatewayResponse.error_response(
                        code=GatewayResponse.INTERNAL_ERROR,
                        message=str(e),
                    )
                    await ws.send(error_resp.to_json())
        except Exception as e:
            logger.debug("CLI connection closed: %s", e)

    async def _handle_request(self, req: GatewayRequest) -> GatewayResponse:
        """处理 CLI 请求"""
        method = req.method

        match method:
            case "ping":
                return GatewayResponse.success({"status": "ok"}, req.id)

            case "call_api":
                return await self._handle_call_api(req)

            case "get_status":
                return self._handle_get_status(req)

            case "shutdown":
                self._running = False
                return GatewayResponse.success(
                    {"shutting_down": True},
                    req.id,
                )

            case "list_webhooks":
                return GatewayResponse.success(
                    self._webhooks.list_webhooks(),
                    req.id,
                )

            case "add_webhook":
                return self._handle_add_webhook(req)

            case "remove_webhook":
                return self._handle_remove_webhook(req)

            case _:
                return GatewayResponse.error_response(
                    code=GatewayResponse.METHOD_NOT_FOUND,
                    message=f"Method not found: {method}",
                    request_id=req.id,
                )

    async def _handle_call_api(self, req: GatewayRequest) -> GatewayResponse:
        """处理 API 调用请求"""
        if not self._client or not self._client.is_running:
            return GatewayResponse.error_response(
                code=GatewayResponse.CLIENT_NOT_CONNECTED,
                message="NapCat client not connected",
                request_id=req.id,
            )

        action = req.params.get("action")
        params = req.params.get("params", {})

        if not action:
            return GatewayResponse.error_response(
                code=GatewayResponse.INVALID_PARAMS,
                message="Missing 'action' parameter",
                request_id=req.id,
            )

        try:
            result = await self._client.call_action(action, params)
            return GatewayResponse.success(result, req.id)
        except Exception as e:
            return GatewayResponse.error_response(
                code=GatewayResponse.INTERNAL_ERROR,
                message=str(e),
                request_id=req.id,
            )

    def _handle_get_status(self, req: GatewayRequest) -> GatewayResponse:
        """处理状态查询"""
        status = {
            "instance": self.instance_name,
            "running": self._client is not None and self._client.is_running,
            "ws_url": self.ws_url,
            "webhooks_count": len(self._webhooks.list_webhooks()),
        }
        return GatewayResponse.success(status, req.id)

    def _handle_add_webhook(self, req: GatewayRequest) -> GatewayResponse:
        """添加 Webhook"""
        url = req.params.get("url")
        if not url:
            return GatewayResponse.error_response(
                code=GatewayResponse.INVALID_PARAMS,
                message="Missing 'url' parameter",
                request_id=req.id,
            )

        events = req.params.get("events")
        secret = req.params.get("secret")

        self._webhooks.add_webhook(url, events, secret)
        return GatewayResponse.success({"added": url}, req.id)

    def _handle_remove_webhook(self, req: GatewayRequest) -> GatewayResponse:
        """移除 Webhook"""
        url = req.params.get("url")
        index = req.params.get("index")

        if url:
            removed = self._webhooks.remove_webhook_by_url(url)
        elif index is not None:
            if isinstance(index, bool):
                return GatewayResponse.error_response(
                    code=GatewayResponse.INVALID_PARAMS,
                    message="Parameter 'index' must be an integer",
                    request_id=req.id,
                )

            try:
                parsed_index = int(index)
            except (TypeError, ValueError):
                return GatewayResponse.error_response(
                    code=GatewayResponse.INVALID_PARAMS,
                    message="Parameter 'index' must be an integer",
                    request_id=req.id,
                )

            removed = self._webhooks.remove_webhook_by_index(parsed_index)
        else:
            return GatewayResponse.error_response(
                code=GatewayResponse.INVALID_PARAMS,
                message="Missing 'url' or 'index' parameter",
                request_id=req.id,
            )

        if removed:
            return GatewayResponse.success({"removed": True}, req.id)
        return GatewayResponse.error_response(
            code=GatewayResponse.INVALID_PARAMS,
            message="Webhook not found",
            request_id=req.id,
        )

    async def _event_handler(self) -> None:
        """处理 NapCat 事件并分发到 Webhook"""
        if not self._client:
            return

        logger.info("Event handler started")
        try:
            async for event in self._client:
                if not self._running:
                    break

                # 转换为字典 - NapCatEvent 有 to_dict 方法
                event_dict: dict[str, Any]
                if hasattr(event, "to_dict"):
                    event_dict = event.to_dict()
                elif hasattr(event, "__iter__"):
                    event_dict = dict(event)  # type: ignore[call-overload]
                else:
                    event_dict = {"raw": str(event)}

                # 分发到 Webhook
                await self._webhooks.dispatch(event_dict)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error("Event handler error: %s", e)

    def load_webhooks(self, webhooks: Sequence[WebhookConfig]) -> None:
        """从配置加载 Webhook"""
        for wh in webhooks:
            self._webhooks.add_webhook(
                url=wh.get("url", ""),
                events=wh.get("events"),
                secret=wh.get("secret"),
            )
