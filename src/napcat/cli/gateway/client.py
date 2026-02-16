"""
Gateway Unix Socket 客户端

提供 CLI 与 Gateway 守护进程通信的客户端实现。
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from websockets.asyncio.client import unix_connect

from .protocol import GatewayError, GatewayRequest, GatewayResponse


class GatewayClient:
    """
    Gateway 客户端

    通过 Unix Socket 与 Gateway 守护进程通信。
    """

    def __init__(self, socket_path: Path, timeout: float = 30.0):
        self.socket_path = socket_path
        self.timeout = timeout

    async def call(self, method: str, params: dict[str, Any] | None = None) -> Any:
        """
        调用 Gateway 方法

        Args:
            method: 方法名称
            params: 方法参数

        Returns:
            方法返回结果

        Raises:
            GatewayError: Gateway 返回错误
            asyncio.TimeoutError: 超时
            ConnectionError: 连接失败
        """
        req = GatewayRequest(method=method, params=params or {})

        try:
            async with asyncio.timeout(self.timeout):
                async with unix_connect(str(self.socket_path)) as ws:
                    await ws.send(req.to_json())
                    resp_data = await ws.recv()
                    resp = GatewayResponse.from_json(resp_data)

                    if resp.error:
                        raise GatewayError(
                            message=resp.error.get("message", "Unknown error"),
                            code=resp.error.get("code", GatewayResponse.INTERNAL_ERROR),
                            data=resp.error.get("data"),
                        )

                    return resp.result
        except TimeoutError:
            raise
        except Exception as e:
            if isinstance(e, GatewayError):
                raise
            raise ConnectionError(f"Failed to connect to Gateway: {e}") from e

    async def call_api(self, action: str, params: dict[str, Any] | None = None) -> Any:
        """调用 OneBot API"""
        return await self.call("call_api", {"action": action, "params": params or {}})

    async def ping(self) -> bool:
        """健康检查"""
        try:
            result = await self.call("ping")
            return bool(result.get("status") == "ok")
        except Exception:
            return False

    async def get_status(self) -> dict[str, Any]:
        """获取 Gateway 状态"""
        return await self.call("get_status")

    async def shutdown(self) -> bool:
        """请求 Gateway 关闭"""
        result = await self.call("shutdown")
        return result.get("shutting_down", False)

    async def list_webhooks(self) -> list[dict[str, Any]]:
        """列出 Webhook"""
        return await self.call("list_webhooks")

    async def add_webhook(
        self,
        url: str,
        events: list[str] | None = None,
        secret: str | None = None,
    ) -> bool:
        """添加 Webhook"""
        params: dict[str, Any] = {"url": url}
        if events:
            params["events"] = events
        if secret:
            params["secret"] = secret

        result = await self.call("add_webhook", params)
        return result.get("added") == url

    async def remove_webhook(self, url: str | None = None, index: int | None = None) -> bool:
        """移除 Webhook"""
        params: dict[str, Any] = {}
        if url:
            params["url"] = url
        if index is not None:
            params["index"] = index

        result = await self.call("remove_webhook", params)
        return result.get("removed", False)
