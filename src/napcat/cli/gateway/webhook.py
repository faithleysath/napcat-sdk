"""
Webhook 分发器

处理事件到 Webhook 的分发。
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import logging
from typing import Any

import aiohttp

logger = logging.getLogger("napcat.webhook")


class WebhookDispatcher:
    """
    Webhook 分发器

    管理多个 Webhook 端点，将事件分发到订阅的 Webhook。
    """

    def __init__(self, timeout: float = 5.0):
        self._webhooks: list[dict[str, Any]] = []
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建 HTTP 会话"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self._timeout)
        return self._session

    async def close(self) -> None:
        """关闭 HTTP 会话"""
        if self._session and not self._session.closed:
            await self._session.close()

    def add_webhook(
        self,
        url: str,
        events: list[str] | None = None,
        secret: str | None = None,
    ) -> int:
        """
        添加 Webhook

        Args:
            url: Webhook URL
            events: 订阅的事件类型列表 (None 或 ["*"] 表示所有事件)
            secret: HMAC 签名密钥

        Returns:
            Webhook 索引
        """
        webhook: dict[str, Any] = {
            "url": url,
            "events": events or ["*"],
        }
        if secret:
            webhook["secret"] = secret

        self._webhooks.append(webhook)
        return len(self._webhooks) - 1

    def remove_webhook_by_url(self, url: str) -> bool:
        """按 URL 移除 Webhook"""
        for i, wh in enumerate(self._webhooks):
            if wh.get("url") == url:
                self._webhooks.pop(i)
                return True
        return False

    def remove_webhook_by_index(self, index: int) -> bool:
        """按索引移除 Webhook"""
        if 0 <= index < len(self._webhooks):
            self._webhooks.pop(index)
            return True
        return False

    def list_webhooks(self) -> list[dict[str, Any]]:
        """列出所有 Webhook"""
        return list(self._webhooks)

    def _should_send(self, event: dict[str, Any], subscribed_events: list[str]) -> bool:
        """
        检查事件是否应该发送到 Webhook

        Args:
            event: OneBot 事件
            subscribed_events: 订阅的事件类型

        Returns:
            是否应该发送
        """
        if "*" in subscribed_events:
            return True

        # OneBot 事件类型判断
        post_type = event.get("post_type", "")

        # 映射 post_type 到事件类别
        type_mapping = {
            "message": "message",
            "notice": "notice",
            "request": "request",
            "meta_event": "meta",
        }

        event_category = type_mapping.get(post_type, post_type)

        return event_category in subscribed_events

    def _compute_signature(self, secret: str, payload: bytes) -> str:
        """计算 HMAC-SHA256 签名"""
        return hmac.new(
            secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()

    async def dispatch(self, event: dict[str, Any]) -> None:
        """
        分发事件到所有订阅的 Webhook

        Args:
            event: OneBot 事件
        """
        if not self._webhooks:
            return

        session = await self._get_session()

        # 准备请求体
        import orjson
        payload = orjson.dumps(event)

        # 并发发送到所有 Webhook
        tasks = [
            self._send_to_webhook(session, wh, payload)
            for wh in self._webhooks
            if self._should_send(event, wh.get("events", ["*"]))
        ]

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_to_webhook(
        self,
        session: aiohttp.ClientSession,
        webhook: dict[str, Any],
        payload: bytes,
    ) -> None:
        """发送事件到单个 Webhook"""
        url = webhook.get("url", "")
        secret = webhook.get("secret")

        headers = {"Content-Type": "application/json"}

        # 添加签名
        if secret:
            signature = self._compute_signature(secret, payload)
            headers["X-Signature"] = f"sha256={signature}"

        try:
            async with session.post(url, data=payload, headers=headers) as resp:
                if resp.status >= 400:
                    logger.warning(
                        "Webhook %s returned status %d",
                        url,
                        resp.status,
                    )
                else:
                    logger.debug("Webhook %s success", url)
        except TimeoutError:
            logger.warning("Webhook %s timeout", url)
        except aiohttp.ClientError as e:
            logger.warning("Webhook %s error: %s", url, e)
        except Exception as e:
            logger.error("Webhook %s unexpected error: %s", url, e)
