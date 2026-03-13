"""
webhook 命令

管理 Webhook 配置。
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from typing import Any, cast

from ..config import InstanceConfig
from ..gateway.client import GatewayClient
from ..gateway.protocol import GatewayError
from ..utils import print_error, print_instance_create_hint, print_success

WebhookRecord = dict[str, Any]
IndexedWebhook = tuple[int, WebhookRecord]


def cmd_webhook(
    instance_name: str,
    subcommand: str,
    url: str | None = None,
    events: list[str] | None = None,
    secret: str | None = None,
) -> int:
    """
    管理 Webhook

    Args:
        instance_name: 实例名称
        subcommand: 子命令 (add/list/rm)
        url: Webhook URL
        events: 事件类型（add 作为订阅类型；list/rm 作为过滤器）
        secret: HMAC 签名密钥

    Returns:
        退出码
    """
    config = InstanceConfig(instance_name)

    if not config.exists():
        print_error(f"Instance '{instance_name}' does not exist.")
        print_instance_create_hint(instance_name)
        return 1

    match subcommand:
        case "add":
            return _cmd_webhook_add(config, url, events, secret)
        case "list":
            return _cmd_webhook_list(config, url, events)
        case "rm" | "remove":
            return _cmd_webhook_remove(config, url, events)
        case _:
            print_error(f"Unknown subcommand: {subcommand}")
            print("Available: add, list, rm")
            return 1


def _cmd_webhook_add(
    config: InstanceConfig,
    url: str | None,
    events: list[str] | None,
    secret: str | None,
) -> int:
    """添加 Webhook"""
    if not url:
        print_error("URL is required.")
        print("Usage: napcat-sdk webhook <NAME> add <URL> [--event TYPE] [--secret STR]")
        return 1

    # 如果实例正在运行，通过 Gateway API 添加
    if config.is_running():
        return _add_webhook_online(config, url, events, secret)
    else:
        # 否则直接修改配置文件
        return _add_webhook_offline(config, url, events, secret)


def _add_webhook_online(
    config: InstanceConfig,
    url: str,
    events: list[str] | None,
    secret: str | None,
) -> int:
    """通过 Gateway API 添加 Webhook"""
    client = GatewayClient(config.socket_file)

    async def do_add():
        try:
            success = await client.add_webhook(url, events, secret)
            return success
        except GatewayError as e:
            print_error(f"Gateway error: {e}")
            return False
        except Exception as e:
            print_error(f"Error: {e}")
            return False

    try:
        success = asyncio.run(do_add())
        if success:
            print_success(f"Webhook added: {url}")
            return 0
        return 1
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return 1


def _add_webhook_offline(
    config: InstanceConfig,
    url: str,
    events: list[str] | None,
    secret: str | None,
) -> int:
    """通过修改配置文件添加 Webhook"""
    try:
        config.add_webhook(url, events, secret)
        print_success(f"Webhook added to config: {url}")
        print("Note: Changes will take effect on next start.")
        return 0
    except Exception as e:
        print_error(f"Failed to update config: {e}")
        return 1


def _cmd_webhook_list(
    config: InstanceConfig,
    url: str | None,
    events: list[str] | None,
) -> int:
    """列出 Webhook（支持过滤）"""
    if config.is_running():
        webhooks = _list_webhooks_online(config)
        if webhooks is None:
            return 1
    else:
        webhooks = _list_webhooks_offline(config)

    if not webhooks:
        print("No webhooks configured.")
        return 0

    matched = _filter_webhooks(webhooks, url=url, events=events)
    if not matched:
        print("No webhooks matched the given filters.")
        return 0

    _print_webhooks(matched)
    return 0


def _list_webhooks_online(config: InstanceConfig) -> list[WebhookRecord] | None:
    """通过 Gateway API 读取当前运行中的 Webhook 列表"""
    client = GatewayClient(config.socket_file)

    async def do_list() -> list[WebhookRecord]:
        return await client.list_webhooks()

    try:
        return asyncio.run(do_list())
    except GatewayError as e:
        print_error(f"Gateway error: {e}")
        return None
    except Exception as e:
        print_error(f"Error: {e}")
        return None


def _list_webhooks_offline(config: InstanceConfig) -> list[WebhookRecord]:
    """从配置文件读取 Webhook 列表"""
    loaded = config.load()
    webhooks = cast(list[WebhookRecord], loaded.get("webhooks", []))
    return webhooks


def _print_webhooks(indexed_webhooks: Sequence[IndexedWebhook]) -> None:
    """打印 Webhook 列表"""
    print(f"{'#':<4} {'URL':<40} {'EVENTS'}")
    print("-" * 70)

    for index, wh in indexed_webhooks:
        webhook_url = str(wh.get("url", ""))
        webhook_events = _normalize_webhook_events(wh)
        events_str = ",".join(webhook_events) if webhook_events else "*"
        print(f"{index:<4} {webhook_url:<40} {events_str}")


def _normalize_event_filters(events: Sequence[str] | None) -> list[str]:
    """规范化事件过滤器"""
    if not events:
        return []

    normalized: list[str] = []
    for event in events:
        event_type = event.strip()
        if event_type:
            normalized.append(event_type)
    return normalized


def _normalize_webhook_events(webhook: WebhookRecord) -> list[str]:
    """规范化单条 Webhook 上的事件类型"""
    raw_events = webhook.get("events")
    if isinstance(raw_events, list):
        normalized: list[str] = []
        for raw_event in cast(list[object], raw_events):
            event_type = str(raw_event).strip()
            if event_type:
                normalized.append(event_type)
        return normalized or ["*"]
    if isinstance(raw_events, str):
        event_type = raw_events.strip()
        return [event_type] if event_type else ["*"]
    return ["*"]


def _match_event_filter(webhook: WebhookRecord, event_filters: Sequence[str]) -> bool:
    """按事件类型过滤 Webhook。"""
    if not event_filters or "*" in event_filters:
        return True

    webhook_events = _normalize_webhook_events(webhook)
    if "*" in webhook_events:
        return True
    return any(event in webhook_events for event in event_filters)


def _filter_webhooks(
    webhooks: Sequence[WebhookRecord],
    url: str | None,
    events: Sequence[str] | None,
) -> list[IndexedWebhook]:
    """
    过滤 Webhook 列表。

    规则：
    - 无过滤参数：返回全部；
    - 仅传 url：按 url 过滤；
    - 仅传 events：按事件类型过滤；
    - 同时传 url 和 events：取交集。
    """
    event_filters = _normalize_event_filters(events)
    matched: list[IndexedWebhook] = []

    for index, webhook in enumerate(webhooks):
        if url and str(webhook.get("url", "")) != url:
            continue

        if not _match_event_filter(webhook, event_filters):
            continue

        matched.append((index, webhook))

    return matched


def _cmd_webhook_remove(
    config: InstanceConfig,
    url: str | None,
    events: list[str] | None,
) -> int:
    """移除 Webhook（支持过滤）"""
    if config.is_running():
        return _remove_webhooks_online(config, url, events)
    return _remove_webhooks_offline(config, url, events)


def _remove_webhooks_online(
    config: InstanceConfig,
    url: str | None,
    events: Sequence[str] | None,
) -> int:
    """通过 Gateway API 批量移除匹配的 Webhook"""
    client = GatewayClient(config.socket_file)
    webhooks = _list_webhooks_online(config)
    if webhooks is None:
        return 1

    if not webhooks:
        print("No webhooks configured.")
        return 0

    matched = _filter_webhooks(webhooks, url=url, events=events)
    if not matched:
        print_error("No webhook matched the given filters.")
        return 1

    indices = [idx for idx, _ in sorted(matched, key=lambda item: item[0], reverse=True)]

    async def do_remove() -> bool:
        try:
            for idx in indices:
                removed = await client.remove_webhook(index=idx)
                if not removed:
                    return False
            return True
        except GatewayError as e:
            print_error(f"Gateway error: {e}")
            return False
        except Exception as e:
            print_error(f"Error: {e}")
            return False

    try:
        success = asyncio.run(do_remove())
        if success:
            print_success(f"Removed {len(indices)} webhook(s).")
            return 0
        print_error("Failed to remove one or more webhooks.")
        return 1
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return 1


def _remove_webhooks_offline(
    config: InstanceConfig,
    url: str | None,
    events: Sequence[str] | None,
) -> int:
    """通过修改配置文件批量移除匹配的 Webhook"""
    try:
        loaded = config.load()
        webhooks = cast(list[WebhookRecord], loaded.get("webhooks", []))

        if not webhooks:
            print("No webhooks configured.")
            return 0

        matched = _filter_webhooks(webhooks, url=url, events=events)
        if not matched:
            print_error("No webhook matched the given filters.")
            return 1

        for idx, _ in sorted(matched, key=lambda item: item[0], reverse=True):
            webhooks.pop(idx)

        config.save(loaded)
        print_success(f"Removed {len(matched)} webhook(s) from config.")
        print("Note: Changes will take effect on next start.")
        return 0
    except Exception as e:
        print_error(f"Failed to update config: {e}")
        return 1
