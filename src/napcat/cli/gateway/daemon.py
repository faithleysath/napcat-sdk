"""
守护进程管理

提供进程守护化 (daemonize) 功能，将进程转换为后台守护进程。
"""

from __future__ import annotations

import os
import signal
import sys
from collections.abc import Callable
from pathlib import Path


def daemonize(
    pid_file: Path,
    log_file: Path,
    workdir: Path | None = None,
    umask: int = 0o022,
) -> None:
    """
    将当前进程转换为守护进程

    使用双 fork 技术实现守护进程化：
    1. 第一次 fork 创建子进程，父进程退出
    2. 子进程创建新会话 (setsid)
    3. 第二次 fork 防止获取 TTY
    4. 重定向标准流到日志文件
    5. 写入 PID 文件

    Args:
        pid_file: PID 文件路径
        log_file: 日志文件路径
        workdir: 工作目录 (默认为实例目录)
        umask: 文件权限掩码

    Note:
        此函数仅在 Unix-like 系统上工作。
        调用此函数后，当前进程成为守护进程的孙子进程。
    """
    # 第一次 fork
    pid = os.fork()
    if pid > 0:
        # 父进程退出
        sys.exit(0)

    # 子进程创建新会话
    os.setsid()

    # 第二次 fork
    pid = os.fork()
    if pid > 0:
        # 第一次 fork 的子进程退出
        sys.exit(0)

    # 孙进程成为守护进程

    # 设置工作目录
    if workdir:
        os.chdir(workdir)

    # 设置文件权限掩码
    os.umask(umask)

    # 确保目录存在
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # 重定向标准流
    sys.stdout.flush()
    sys.stderr.flush()

    # 打开日志文件用于 stdout/stderr
    log_fd = os.open(log_file, os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o644)
    os.dup2(log_fd, sys.stdout.fileno())
    os.dup2(log_fd, sys.stderr.fileno())

    # 关闭 stdin
    devnull = os.open(os.devnull, os.O_RDWR)
    os.dup2(devnull, sys.stdin.fileno())

    # 写入 PID 文件
    pid_file.write_text(str(os.getpid()))


def stop_daemon(
    pid_file: Path,
    force: bool = False,
    timeout: float = 10.0,
) -> bool:
    """
    停止守护进程

    Args:
        pid_file: PID 文件路径
        force: 是否强制杀死 (SIGKILL)
        timeout: 等待进程退出的超时时间

    Returns:
        是否成功停止

    Raises:
        ProcessLookupError: 进程不存在
    """
    import time

    if not pid_file.exists():
        raise ProcessLookupError(f"PID file not found: {pid_file}")

    try:
        pid = int(pid_file.read_text().strip())
    except ValueError as e:
        raise ProcessLookupError(f"Invalid PID in file: {pid_file}") from e

    # 检查进程是否存在
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        # 进程不存在，清理 PID 文件
        pid_file.unlink(missing_ok=True)
        raise ProcessLookupError(f"Process {pid} not running") from None
    except PermissionError:
        raise PermissionError(f"No permission to kill process {pid}") from None

    # 发送信号
    sig = signal.SIGKILL if force else signal.SIGTERM
    os.kill(pid, sig)

    # 等待进程退出
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            os.kill(pid, 0)
            time.sleep(0.1)
        except ProcessLookupError:
            # 进程已退出
            pid_file.unlink(missing_ok=True)
            return True

    # 超时后强制杀死
    if not force:
        try:
            os.kill(pid, signal.SIGKILL)
            time.sleep(0.5)
        except ProcessLookupError:
            pass

    pid_file.unlink(missing_ok=True)
    return True


def setup_signal_handlers(
    shutdown_callback: Callable[[], None],
) -> None:
    """
    设置信号处理器

    处理 SIGTERM 和 SIGINT 信号，调用回调函数进行优雅关闭。
    """
    def signal_handler(signum: int, frame: object) -> None:
        sig_name = signal.Signals(signum).name
        sys.stderr.write(f"\nReceived {sig_name}, shutting down...\n")
        shutdown_callback()

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
