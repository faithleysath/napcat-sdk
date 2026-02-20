"""
list 命令

列出所有实例及其状态。
"""

from __future__ import annotations

from ..config import GatewayConfig, InstanceConfig
from ..utils import format_status, truncate


def _parse_bool(value: object) -> bool:
    """解析布尔配置值。"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    return bool(value)


def _parse_non_negative_int(value: object, default: int = 0) -> int:
    """解析非负整数，非法时返回默认值。"""
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value if value >= 0 else default
    try:
        parsed = int(str(value))
        return parsed if parsed >= 0 else default
    except (TypeError, ValueError):
        return default


def _format_rpc_summary(gateway_cfg: GatewayConfig) -> str:
    """格式化 RPC 配置摘要。"""
    rpc_mode_raw: object = gateway_cfg["rpc_mode"] if "rpc_mode" in gateway_cfg else False
    if not _parse_bool(rpc_mode_raw):
        return "off"

    rpc_public_host_raw: object = (
        gateway_cfg["rpc_public_host"] if "rpc_public_host" in gateway_cfg else None
    )
    rpc_host_raw: object = gateway_cfg["rpc_host"] if "rpc_host" in gateway_cfg else "0.0.0.0"
    host = (
        rpc_public_host_raw
        if isinstance(rpc_public_host_raw, str) and rpc_public_host_raw
        else rpc_host_raw
    )
    host_str = host or "127.0.0.1"
    rpc_port_raw: object = gateway_cfg["rpc_port"] if "rpc_port" in gateway_cfg else 0
    port = _parse_non_negative_int(rpc_port_raw)

    if port > 0:
        return f"ws://{host_str}:{port}"
    return f"ws://{host_str}:auto"


def cmd_list() -> int:
    """
    列出所有实例

    Returns:
        退出码
    """
    instances = InstanceConfig.list_all()

    if not instances:
        print("No instances found.")
        print("\nCreate one with: napcat-sdk config <NAME> --ws <URL>")
        return 0

    # 表头
    print(f"{'NAME':<15} {'PID':<8} {'STATUS':<12} {'RPC':<30} {'WS_URL'}")
    print("-" * 100)

    has_error = False
    for instance in instances:
        try:
            config = instance.load()
            running = instance.is_running()
            pid = instance.get_pid()
            ws_url = truncate(config["connection"].get("ws_url", "") or "not set", 40)
            rpc_summary = truncate(_format_rpc_summary(config["gateway"]), 30)
            status = format_status(running)
            pid_str = str(pid) if pid else "-"
        except Exception as e:
            has_error = True
            pid_str = "-"
            status = "\033[31mError\033[0m"
            rpc_summary = "-"
            ws_url = truncate(f"invalid config: {e}", 40)

        print(f"{instance.name:<15} {pid_str:<8} {status:<20} {rpc_summary:<30} {ws_url}")

    return 1 if has_error else 0
