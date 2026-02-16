"""
webhook 命令

管理 Webhook 配置。
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from typing import Any

from ..config import InstanceConfig
from ..gateway.client import GatewayClient
from ..gateway.protocol import GatewayError
from ..utils import print_error, print_success


def cmd_webhook(
    instance_name: str,
    subcommand: str,
    url: str | None = None,
    events: list[str] | None = None,
    secret: str | None = None,
    index: int | None = None,
) -> int:
    """
    管理 Webhook

    Args:
        instance_name: 实例名称
        subcommand: 子命令 (add/list/rm)
        url: Webhook URL
        events: 订阅的事件类型
        secret: HMAC 签名密钥
        index: 要删除的 Webhook 索引

    Returns:
        退出码
    """
    config = InstanceConfig(instance_name)

    if not config.exists():
        print_error(f"Instance '{instance_name}' does not exist.")
        return 1

    match subcommand:
        case "add":
            return _cmd_webhook_add(config, url, events, secret)
        case "list":
            return _cmd_webhook_list(config)
        case "rm" | "remove":
            return _cmd_webhook_remove(config, url, index)
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


def _cmd_webhook_list(config: InstanceConfig) -> int:
    """列出 Webhook"""
    # 如果实例正在运行，通过 Gateway API 获取
    if config.is_running():
        return _list_webhooks_online(config)
    else:
        # 否则从配置文件读取
        return _list_webhooks_offline(config)


def _list_webhooks_online(config: InstanceConfig) -> int:
    """通过 Gateway API 列出 Webhook"""
    client = GatewayClient(config.socket_file)

    async def do_list():
        try:
            webhooks = await client.list_webhooks()
            return webhooks
        except GatewayError as e:
            print_error(f"Gateway error: {e}")
            return None
        except Exception as e:
            print_error(f"Error: {e}")
            return None

    try:
        webhooks = asyncio.run(do_list())
        if webhooks is None:
            return 1

        _print_webhooks(webhooks)
        return 0
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return 1


def _list_webhooks_offline(config: InstanceConfig) -> int:
    """从配置文件列出 Webhook"""
    loaded = config.load()
    webhooks = loaded.get("webhooks", [])

    _print_webhooks(webhooks)  # type: ignore[arg-type]
    return 0


def _print_webhooks(webhooks: Sequence[dict[str, Any]]) -> None:
    """打印 Webhook 列表"""
    if not webhooks:
        print("No webhooks configured.")
        return

    print(f"{'#':<4} {'URL':<40} {'EVENTS'}")
    print("-" * 70)

    for i, wh in enumerate(webhooks):
        url = wh.get("url", "")
        events = wh.get("events", ["*"])
        events_str = ",".join(events) if events else "*"
        print(f"{i:<4} {url:<40} {events_str}")


def _cmd_webhook_remove(
    config: InstanceConfig,
    url: str | None,
    index: int | None,
) -> int:
    """移除 Webhook"""
    if not url and index is None:
        print_error("URL or index is required.")
        print("Usage: napcat-sdk webhook <NAME> rm <URL>")
        print("       napcat-sdk webhook <NAME> rm --index <NUM>")
        return 1

    # 如果实例正在运行，通过 Gateway API 移除
    if config.is_running():
        return _remove_webhook_online(config, url, index)
    else:
        # 否则直接修改配置文件
        return _remove_webhook_offline(config, url, index)


def _remove_webhook_online(
    config: InstanceConfig,
    url: str | None,
    index: int | None,
) -> int:
    """通过 Gateway API 移除 Webhook"""
    client = GatewayClient(config.socket_file)

    async def do_remove():
        try:
            success = await client.remove_webhook(url=url, index=index)
            return success
        except GatewayError as e:
            print_error(f"Gateway error: {e}")
            return False
        except Exception as e:
            print_error(f"Error: {e}")
            return False

    try:
        success = asyncio.run(do_remove())
        if success:
            target = url if url else f"index {index}"
            print_success(f"Webhook removed: {target}")
            return 0
        print_error("Webhook not found.")
        return 1
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return 1


def _remove_webhook_offline(
    config: InstanceConfig,
    url: str | None,
    index: int | None,
) -> int:
    """通过修改配置文件移除 Webhook"""
    try:
        if url:
            success = config.remove_webhook(url)
        elif index is not None:
            success = config.remove_webhook(index)
        else:
            success = False

        if success:
            target = url if url else f"index {index}"
            print_success(f"Webhook removed from config: {target}")
            print("Note: Changes will take effect on next start.")
            return 0
        print_error("Webhook not found.")
        return 1
    except Exception as e:
        print_error(f"Failed to update config: {e}")
        return 1
