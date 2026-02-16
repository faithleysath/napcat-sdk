"""
list 命令

列出所有实例及其状态。
"""

from __future__ import annotations

from ..config import InstanceConfig
from ..utils import format_status, truncate


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
    print(f"{'NAME':<15} {'PID':<8} {'STATUS':<12} {'WS_URL'}")
    print("-" * 60)

    for instance in instances:
        config = instance.load()
        running = instance.is_running()
        pid = instance.get_pid()
        ws_url = truncate(config["connection"].get("ws_url", "") or "not set", 40)

        status = format_status(running)
        pid_str = str(pid) if pid else "-"

        print(f"{instance.name:<15} {pid_str:<8} {status:<20} {ws_url}")

    return 0
