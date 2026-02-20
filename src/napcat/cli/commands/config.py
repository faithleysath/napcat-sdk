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
    rpc_mode: bool | None = None,
    rpc_host: str | None = None,
    rpc_port: int | None = None,
    rpc_token: str | None = None,
    rpc_public_host: str | None = None,
) -> int:
    """
    查看或修改实例配置

    Args:
        instance_name: 实例名称
        ws_url: WebSocket URL (可选)
        token: 访问令牌 (可选)
        rpc_mode: 是否启用透明 RPC 代理 (可选)
        rpc_host: RPC 监听地址 (可选)
        rpc_port: RPC 监听端口 (可选)
        rpc_token: RPC 鉴权令牌 (可选)
        rpc_public_host: RPC 对外地址 (可选)

    Returns:
        退出码
    """
    config = InstanceConfig(instance_name)

    # 如果没有提供任何参数，显示当前配置
    if (
        ws_url is None
        and token is None
        and rpc_mode is None
        and rpc_host is None
        and rpc_port is None
        and rpc_token is None
        and rpc_public_host is None
    ):
        if not config.exists():
            print_error(f"Instance '{instance_name}' does not exist.")
            print(f"Create it with: napcat-sdk config {instance_name} --ws <URL>")
            return 1

        loaded = config.load()
        gateway_cfg = loaded["gateway"]
        print(f"\n[{instance_name}]")
        print(f"  ws_url = \"{loaded['connection'].get('ws_url', '')}\"")
        print(f"  token = \"{loaded['connection'].get('token', '')}\"")
        print(f"  log_level = \"{gateway_cfg.get('log_level', 'INFO')}\"")
        print(f"  rpc_mode = {gateway_cfg.get('rpc_mode', False)}")
        print(f"  rpc_host = \"{gateway_cfg.get('rpc_host', '0.0.0.0')}\"")
        print(f"  rpc_port = {gateway_cfg.get('rpc_port', 0)}")
        print(f"  rpc_token = \"{gateway_cfg.get('rpc_token', '')}\"")
        print(f"  rpc_public_host = \"{gateway_cfg.get('rpc_public_host', '')}\"")

        if loaded.get("webhooks"):
            print(f"  webhooks = {len(loaded['webhooks'])} configured")

        return 0

    # 更新配置
    try:
        config.update(
            ws_url=ws_url,
            token=token,
            rpc_mode=rpc_mode,
            rpc_host=rpc_host,
            rpc_port=rpc_port,
            rpc_token=rpc_token,
            rpc_public_host=rpc_public_host,
        )
        print_success(f"Configuration updated for '{instance_name}'")

        # 显示更新后的配置
        loaded = config.load()
        gateway_cfg = loaded["gateway"]
        print(f"\n[{instance_name}]")
        print(f"  ws_url = \"{loaded['connection'].get('ws_url', '')}\"")
        print(f"  token = \"{loaded['connection'].get('token', '')}\"")
        print(f"  rpc_mode = {gateway_cfg.get('rpc_mode', False)}")
        print(f"  rpc_host = \"{gateway_cfg.get('rpc_host', '0.0.0.0')}\"")
        print(f"  rpc_port = {gateway_cfg.get('rpc_port', 0)}")
        print(f"  rpc_token = \"{gateway_cfg.get('rpc_token', '')}\"")
        print(f"  rpc_public_host = \"{gateway_cfg.get('rpc_public_host', '')}\"")

        return 0
    except Exception as e:
        print_error(f"Failed to update configuration: {e}")
        return 1
