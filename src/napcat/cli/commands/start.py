"""
start 命令

启动 Gateway 守护进程。
"""

from __future__ import annotations

import asyncio
import os
import sys

from ..config import InstanceConfig, InstanceConfigDict
from ..gateway.daemon import setup_signal_handlers
from ..gateway.server import Gateway
from ..utils import print_error, print_success


def cmd_start(
    instance_name: str,
    ws_url: str | None = None,
    token: str | None = None,
    foreground: bool = False,
) -> int:
    """
    启动实例的 Gateway 守护进程

    Args:
        instance_name: 实例名称
        ws_url: WebSocket URL (可选，用于更新配置)
        token: 访问令牌 (可选)
        foreground: 是否前台运行

    Returns:
        退出码
    """
    config = InstanceConfig(instance_name)

    # 如果提供了配置参数，先更新配置
    if ws_url or token:
        config.update(ws_url=ws_url, token=token)

    # 检查配置是否存在
    if not config.exists():
        print_error(f"Instance '{instance_name}' does not exist.")
        print(f"Create it with: napcat-sdk config {instance_name} --ws <URL>")
        return 1

    # 加载配置
    loaded = config.load()
    cfg_ws_url = loaded["connection"].get("ws_url", "")
    cfg_token = loaded["connection"].get("token") or None
    cfg_log_level = loaded["gateway"].get("log_level", "INFO")

    if not cfg_ws_url:
        print_error("WebSocket URL not configured.")
        print(f"Set it with: napcat-sdk config {instance_name} --ws <URL>")
        return 1

    # 检查是否已运行
    if config.is_running():
        print_error(f"Instance '{instance_name}' is already running.")
        print(f"PID: {config.get_pid()}")
        return 1

    if foreground:
        # 前台运行
        return _run_foreground(config, cfg_ws_url, cfg_token, cfg_log_level, loaded)
    else:
        # 后台守护进程
        return _run_daemon(config, cfg_ws_url, cfg_token, cfg_log_level, loaded)


def _run_foreground(
    config: InstanceConfig,
    ws_url: str,
    token: str | None,
    log_level: str,
    loaded_config: InstanceConfigDict,
) -> int:
    """前台运行 Gateway"""
    print(f"Starting Gateway '{config.name}' in foreground...")

    # 清理旧的 socket 文件
    config.clear_socket()

    gateway = Gateway(
        instance_name=config.name,
        ws_url=ws_url,
        token=token,
        socket_path=config.socket_file,
        log_level=log_level,
    )

    # 加载 Webhook
    if loaded_config.get("webhooks"):
        gateway.load_webhooks(loaded_config["webhooks"])

    # 设置信号处理
    shutdown_event = asyncio.Event()

    def on_shutdown():
        shutdown_event.set()

    setup_signal_handlers(on_shutdown)

    # 写入 PID 文件
    config.write_pid(os.getpid())

    try:
        async def run():
            # 启动一个任务来等待关闭信号
            async def wait_shutdown():
                while not shutdown_event.is_set():
                    await asyncio.sleep(0.5)

            # 并行运行 Gateway 和等待关闭信号
            gateway_task = asyncio.create_task(gateway.start())
            shutdown_task = asyncio.create_task(wait_shutdown())

            # 任一完成就退出
            done, _ = await asyncio.wait(
                [gateway_task, shutdown_task],
                return_when=asyncio.FIRST_COMPLETED,
            )

            # 如果是关闭信号触发的，取消 gateway 任务
            if shutdown_task in done:
                gateway_task.cancel()
                try:
                    await gateway_task
                except asyncio.CancelledError:
                    pass

        asyncio.run(run())
        print_success("Gateway stopped.")
        return 0
    except KeyboardInterrupt:
        print("\nGateway stopped.")
        return 0
    except Exception as e:
        print_error(f"Gateway error: {e}")
        return 1
    finally:
        config.clear_pid()
        config.clear_socket()


def _run_daemon(
    config: InstanceConfig,
    ws_url: str,
    token: str | None,
    log_level: str,
    loaded_config: InstanceConfigDict,
) -> int:
    """以守护进程方式运行 Gateway"""
    # 检查平台
    if sys.platform == "win32":
        print_error("Daemon mode is not supported on Windows.")
        print("Use --foreground to run in foreground mode.")
        return 1

    print(f"Starting Gateway '{config.name}' as daemon...")

    # 第一次 fork，父进程退出
    pid = os.fork()
    if pid > 0:
        # 父进程等待一下确保子进程启动
        import time
        time.sleep(0.5)

        # 检查是否成功启动
        if config.is_running():
            print_success(f"Gateway '{config.name}' started (PID: {config.get_pid()})")
            return 0
        else:
            print_error("Failed to start Gateway. Check logs at:")
            print(f"  {config.log_file}")
            return 1

    # 子进程继续
    os.setsid()

    # 第二次 fork
    pid = os.fork()
    if pid > 0:
        sys.exit(0)

    # 孙进程成为守护进程
    # 重定向标准流
    sys.stdout.flush()
    sys.stderr.flush()

    config.instance_dir.mkdir(parents=True, exist_ok=True)

    # 打开日志文件
    log_fd = os.open(config.log_file, os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o644)
    os.dup2(log_fd, sys.stdout.fileno())
    os.dup2(log_fd, sys.stderr.fileno())

    # 关闭 stdin
    devnull = os.open(os.devnull, os.O_RDWR)
    os.dup2(devnull, sys.stdin.fileno())

    # 写入 PID
    config.write_pid(os.getpid())

    # 清理旧的 socket 文件
    config.clear_socket()

    # 设置信号处理
    shutdown_event = asyncio.Event()

    def on_shutdown():
        shutdown_event.set()

    setup_signal_handlers(on_shutdown)

    # 运行 Gateway
    gateway = Gateway(
        instance_name=config.name,
        ws_url=ws_url,
        token=token,
        socket_path=config.socket_file,
        log_level=log_level,
    )

    # 加载 Webhook
    if loaded_config.get("webhooks"):
        gateway.load_webhooks(loaded_config["webhooks"])

    try:
        async def run():
            async def wait_shutdown():
                while not shutdown_event.is_set():
                    await asyncio.sleep(0.5)

            gateway_task = asyncio.create_task(gateway.start())
            shutdown_task = asyncio.create_task(wait_shutdown())

            done, _ = await asyncio.wait(
                [gateway_task, shutdown_task],
                return_when=asyncio.FIRST_COMPLETED,
            )

            if shutdown_task in done:
                gateway_task.cancel()
                try:
                    await gateway_task
                except asyncio.CancelledError:
                    pass

        asyncio.run(run())
    except Exception as e:
        print(f"Gateway error: {e}", file=sys.stderr)
    finally:
        config.clear_pid()
        config.clear_socket()

    sys.exit(0)
    return 0  # 不会执行到这里
