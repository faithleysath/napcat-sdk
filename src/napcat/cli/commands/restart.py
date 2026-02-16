"""
restart 命令

重启 Gateway 守护进程。
"""

from __future__ import annotations

from ..utils import print_error, print_success
from .start import cmd_start
from .stop import cmd_stop


def cmd_restart(
    instance_name: str,
    foreground: bool = False,
) -> int:
    """
    重启实例的 Gateway 守护进程

    Args:
        instance_name: 实例名称
        foreground: 是否前台运行

    Returns:
        退出码
    """
    print(f"Restarting Gateway '{instance_name}'...")

    # 停止
    stop_result = cmd_stop(instance_name)

    # 如果 stop 返回非零且不是因为实例未运行，则失败
    if stop_result != 0:
        from ..config import InstanceConfig
        config = InstanceConfig(instance_name)
        if config.is_running():
            print_error("Failed to stop Gateway.")
            return stop_result

    # 启动
    start_result = cmd_start(instance_name, foreground=foreground)

    if start_result == 0:
        print_success(f"Gateway '{instance_name}' restarted.")
    return start_result
