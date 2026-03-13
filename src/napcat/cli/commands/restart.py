"""
restart 命令

重启 Gateway 守护进程。
"""

from __future__ import annotations

from ..config import InstanceConfig
from ..utils import (
    print_error,
    print_instance_create_hint,
    print_success,
    print_warning,
)
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
    config = InstanceConfig(instance_name)
    if not config.exists():
        print_error(f"Instance '{instance_name}' does not exist.")
        print_instance_create_hint(instance_name)
        return 1

    was_running = config.is_running()

    if was_running:
        print(f"Restarting Gateway '{instance_name}'...")
        stop_result = cmd_stop(instance_name)

        # 如果 stop 返回非零且不是因为实例未运行，则失败
        if stop_result != 0 and config.is_running():
            print_error("Failed to stop Gateway.")
            return stop_result
    else:
        print_warning(f"Gateway '{instance_name}' is not running. Starting it instead.")

    # 启动
    start_result = cmd_start(instance_name, foreground=foreground)

    if start_result == 0:
        action = "restarted" if was_running else "started"
        print_success(f"Gateway '{instance_name}' {action}.")
    return start_result
