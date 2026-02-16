"""
config 命令

管理实例配置。
"""

from __future__ import annotations

from ..config import InstanceConfig
from ..utils import print_error, print_success


def cmd_config(
    instance_name: str,
    ws_url: str | None = None,
    token: str | None = None,
) -> int:
    """
    查看或修改实例配置

    Args:
        instance_name: 实例名称
        ws_url: WebSocket URL (可选)
        token: 访问令牌 (可选)

    Returns:
        退出码
    """
    config = InstanceConfig(instance_name)

    # 如果没有提供任何参数，显示当前配置
    if ws_url is None and token is None:
        if not config.exists():
            print_error(f"Instance '{instance_name}' does not exist.")
            print(f"Create it with: napcat-sdk config {instance_name} --ws <URL>")
            return 1

        loaded = config.load()
        print(f"\n[{instance_name}]")
        print(f"  ws_url = \"{loaded['connection'].get('ws_url', '')}\"")
        print(f"  token = \"{loaded['connection'].get('token', '')}\"")
        print(f"  log_level = \"{loaded['gateway'].get('log_level', 'INFO')}\"")

        if loaded.get("webhooks"):
            print(f"  webhooks = {len(loaded['webhooks'])} configured")

        return 0

    # 更新配置
    try:
        config.update(ws_url=ws_url, token=token)
        print_success(f"Configuration updated for '{instance_name}'")

        # 显示更新后的配置
        loaded = config.load()
        print(f"\n[{instance_name}]")
        print(f"  ws_url = \"{loaded['connection'].get('ws_url', '')}\"")
        print(f"  token = \"{loaded['connection'].get('token', '')}\"")

        return 0
    except Exception as e:
        print_error(f"Failed to update configuration: {e}")
        return 1
