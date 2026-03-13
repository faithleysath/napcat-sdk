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
from ..utils import print_error, print_instance_create_hint, print_success


def cmd_start(
    instance_name: str,
    ws_url: str | None = None,
    token: str | None = None,
    rpc_mode: bool | None = None,
    rpc_host: str | None = None,
    rpc_port: int | None = None,
    rpc_token: str | None = None,
    rpc_public_host: str | None = None,
    foreground: bool = False,
) -> int:
    """
    启动实例的 Gateway 守护进程

    Args:
        instance_name: 实例名称
        ws_url: WebSocket URL (可选，用于更新配置)
        token: 访问令牌 (可选)
        rpc_mode: 是否启用透明 RPC 代理 (可选，用于更新配置)
        rpc_host: RPC 监听地址 (可选，用于更新配置)
        rpc_port: RPC 监听端口 (可选，用于更新配置)
        rpc_token: RPC 鉴权令牌 (可选，用于更新配置)
        rpc_public_host: RPC 对外地址 (可选，用于更新配置)
        foreground: 是否前台运行

    Returns:
        退出码
    """
    config = InstanceConfig(instance_name)

    # 如果提供了配置参数，先更新配置
    if (
        ws_url is not None
        or token is not None
        or rpc_mode is not None
        or rpc_host is not None
        or rpc_port is not None
        or rpc_token is not None
        or rpc_public_host is not None
    ):
        config.update(
            ws_url=ws_url,
            token=token,
            rpc_mode=rpc_mode,
            rpc_host=rpc_host,
            rpc_port=rpc_port,
            rpc_token=rpc_token,
            rpc_public_host=rpc_public_host,
        )

    # 检查配置是否存在
    if not config.exists():
        print_error(f"Instance '{instance_name}' does not exist.")
        print_instance_create_hint(instance_name)
        return 1

    # 加载配置
    loaded = config.load()
    cfg_ws_url = loaded["connection"].get("ws_url", "")
    cfg_token = loaded["connection"].get("token") or None
    cfg_log_level = loaded["gateway"].get("log_level", "INFO")
    cfg_rpc_mode = _parse_rpc_mode_value(loaded["gateway"].get("rpc_mode", False))
    cfg_rpc_host = str(loaded["gateway"].get("rpc_host", "0.0.0.0"))
    cfg_rpc_port = _parse_rpc_port(loaded["gateway"].get("rpc_port", 0))
    cfg_rpc_token = _parse_optional_str(loaded["gateway"].get("rpc_token"))
    cfg_rpc_public_host = _parse_optional_str(loaded["gateway"].get("rpc_public_host"))

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
        return _run_foreground(
            config,
            cfg_ws_url,
            cfg_token,
            cfg_log_level,
            cfg_rpc_mode,
            cfg_rpc_host,
            cfg_rpc_port,
            cfg_rpc_token,
            cfg_rpc_public_host,
            loaded,
        )
    else:
        # 后台守护进程
        return _run_daemon(
            config,
            cfg_ws_url,
            cfg_token,
            cfg_log_level,
            cfg_rpc_mode,
            cfg_rpc_host,
            cfg_rpc_port,
            cfg_rpc_token,
            cfg_rpc_public_host,
            loaded,
        )


def _parse_optional_str(value: object) -> str | None:
    """从配置值中解析可选字符串。"""
    if isinstance(value, str):
        return value
    return None


def _parse_rpc_mode_value(value: object) -> bool:
    """从配置值中解析 RPC 开关。"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    return bool(value)


def _parse_rpc_port(value: object) -> int:
    """从配置值中解析 RPC 端口，非法值回落到 0。"""
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value if value >= 0 else 0

    try:
        parsed = int(str(value))
        return parsed if parsed >= 0 else 0
    except (TypeError, ValueError):
        return 0


async def _run_gateway_until_shutdown(
    gateway: Gateway,
    shutdown_event: asyncio.Event,
) -> None:
    """运行 Gateway，直到收到关闭信号或 Gateway 异常退出。"""

    async def wait_shutdown() -> None:
        while not shutdown_event.is_set():
            await asyncio.sleep(0.5)

    gateway_task = asyncio.create_task(gateway.start())
    shutdown_task = asyncio.create_task(wait_shutdown())

    done, _ = await asyncio.wait(
        [gateway_task, shutdown_task],
        return_when=asyncio.FIRST_COMPLETED,
    )

    if gateway_task in done:
        shutdown_task.cancel()
        try:
            await shutdown_task
        except asyncio.CancelledError:
            pass

        # 传播 Gateway 启动/运行异常，避免错误返回成功状态码。
        await gateway_task
        return

    gateway_task.cancel()
    try:
        await gateway_task
    except asyncio.CancelledError:
        pass


def _run_foreground(
    config: InstanceConfig,
    ws_url: str,
    token: str | None,
    log_level: str,
    rpc_mode: bool,
    rpc_host: str,
    rpc_port: int,
    rpc_token: str | None,
    rpc_public_host: str | None,
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
        rpc_mode=rpc_mode,
        rpc_host=rpc_host,
        rpc_port=rpc_port,
        rpc_token=rpc_token,
        rpc_public_host=rpc_public_host,
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
        asyncio.run(_run_gateway_until_shutdown(gateway, shutdown_event))
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
    rpc_mode: bool,
    rpc_host: str,
    rpc_port: int,
    rpc_token: str | None,
    rpc_public_host: str | None,
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
        rpc_mode=rpc_mode,
        rpc_host=rpc_host,
        rpc_port=rpc_port,
        rpc_token=rpc_token,
        rpc_public_host=rpc_public_host,
    )

    # 加载 Webhook
    if loaded_config.get("webhooks"):
        gateway.load_webhooks(loaded_config["webhooks"])

    try:
        asyncio.run(_run_gateway_until_shutdown(gateway, shutdown_event))
    except Exception as e:
        print(f"Gateway error: {e}", file=sys.stderr)
    finally:
        config.clear_pid()
        config.clear_socket()

    sys.exit(0)
    return 0  # 不会执行到这里
