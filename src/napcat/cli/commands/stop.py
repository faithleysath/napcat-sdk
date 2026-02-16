"""
stop 命令

停止 Gateway 守护进程。
"""

from __future__ import annotations

from ..config import InstanceConfig
from ..gateway.daemon import stop_daemon
from ..utils import print_error, print_success


def cmd_stop(
    instance_name: str,
    force: bool = False,
) -> int:
    """
    停止实例的 Gateway 守护进程

    Args:
        instance_name: 实例名称
        force: 是否强制杀死 (SIGKILL)

    Returns:
        退出码
    """
    config = InstanceConfig(instance_name)

    if not config.exists():
        print_error(f"Instance '{instance_name}' does not exist.")
        return 1

    if not config.is_running():
        print(f"Instance '{instance_name}' is not running.")
        # 清理可能残留的 PID 文件
        config.clear_pid()
        return 0

    pid = config.get_pid()
    print(f"Stopping Gateway '{instance_name}' (PID: {pid})...")

    try:
        stop_daemon(config.pid_file, force=force)
        print_success(f"Gateway '{instance_name}' stopped.")
        return 0
    except ProcessLookupError:
        print_error(f"Process {pid} not found.")
        config.clear_pid()
        return 1
    except PermissionError:
        print_error(f"No permission to stop process {pid}.")
        return 1
    except Exception as e:
        print_error(f"Failed to stop Gateway: {e}")
        return 1
