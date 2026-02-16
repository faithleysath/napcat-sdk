"""
log 命令

查看 Gateway 日志。
"""

from __future__ import annotations

import subprocess

from ..config import InstanceConfig
from ..utils import print_error


def cmd_log(
    instance_name: str,
    follow: bool = False,
    lines: int = 50,
) -> int:
    """
    查看 Gateway 日志

    Args:
        instance_name: 实例名称
        follow: 是否实时追踪 (tail -f)
        lines: 显示最后 N 行

    Returns:
        退出码
    """
    config = InstanceConfig(instance_name)

    if not config.exists():
        print_error(f"Instance '{instance_name}' does not exist.")
        return 1

    if not config.log_file.exists():
        print(f"No log file found for '{instance_name}'.")
        print("The instance may not have been started yet.")
        return 0

    try:
        if follow:
            # 使用 tail -f 实时追踪
            subprocess.run(
                ["tail", "-f", "-n", str(lines), str(config.log_file)],
            )
        else:
            # 显示最后 N 行
            with open(config.log_file) as f:
                all_lines = f.readlines()
                for line in all_lines[-lines:]:
                    print(line, end="")

        return 0
    except FileNotFoundError:
        print_error("tail command not found.")
        return 1
    except KeyboardInterrupt:
        # 用户按 Ctrl+C 退出
        return 0
    except Exception as e:
        print_error(f"Failed to read log: {e}")
        return 1
