"""
实例配置管理

提供 InstanceConfig 类，管理单个机器人实例的配置文件、目录和运行时文件。
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import tomli_w
from typing_extensions import TypedDict


class ConnectionConfig(TypedDict):
    """连接配置"""

    ws_url: str
    token: str


class GatewayConfig(TypedDict):
    """Gateway 配置"""

    log_level: str


class WebhookConfig(TypedDict, total=False):
    """Webhook 配置"""

    url: str
    events: list[str]
    secret: str


class InstanceConfigDict(TypedDict):
    """完整的实例配置"""

    connection: ConnectionConfig
    gateway: GatewayConfig
    webhooks: list[WebhookConfig]


@dataclass
class InstanceConfig:
    """
    管理单个实例的配置和路径

    目录结构:
    ~/.napcat/<instance_name>/
    ├── config.toml      # 配置文件
    ├── gateway.pid      # PID 文件 (运行时)
    ├── gateway.sock     # Unix Socket (运行时)
    └── gateway.log      # 日志文件 (运行时)
    """

    BASE_DIR = Path.home() / ".napcat"

    name: str
    _config: InstanceConfigDict | None = field(default=None, repr=False)

    @property
    def instance_dir(self) -> Path:
        """实例目录"""
        return self.BASE_DIR / self.name

    @property
    def config_file(self) -> Path:
        """配置文件路径"""
        return self.instance_dir / "config.toml"

    @property
    def pid_file(self) -> Path:
        """PID 文件路径"""
        return self.instance_dir / "gateway.pid"

    @property
    def socket_file(self) -> Path:
        """Unix Socket 路径"""
        return self.instance_dir / "gateway.sock"

    @property
    def log_file(self) -> Path:
        """日志文件路径"""
        return self.instance_dir / "gateway.log"

    def exists(self) -> bool:
        """检查实例配置是否存在"""
        return self.config_file.exists()

    def is_running(self) -> bool:
        """检查实例是否正在运行"""
        if not self.pid_file.exists():
            return False
        try:
            pid = int(self.pid_file.read_text().strip())
            # 发送信号 0 检查进程是否存在
            os.kill(pid, 0)
            return True
        except (ValueError, ProcessLookupError, PermissionError, OSError):
            # PID 文件无效或进程不存在，清理 PID 文件
            try:
                self.pid_file.unlink()
            except OSError:
                pass
            return False

    def get_pid(self) -> int | None:
        """获取运行中的 PID，如果未运行返回 None"""
        if not self.is_running():
            return None
        try:
            return int(self.pid_file.read_text().strip())
        except (ValueError, OSError):
            return None

    def _default_config(self) -> InstanceConfigDict:
        """返回默认配置"""
        return InstanceConfigDict(
            connection=ConnectionConfig(ws_url="", token=""),
            gateway=GatewayConfig(log_level="INFO"),
            webhooks=[],
        )

    def load(self) -> InstanceConfigDict:
        """加载配置文件"""
        if not self.exists():
            return self._default_config()

        # Python 3.11+ 内置 tomllib
        import tomllib

        with open(self.config_file, "rb") as f:
            data = tomllib.load(f)

        # 确保所有字段存在
        config = self._default_config()
        if "connection" in data:
            config["connection"] = ConnectionConfig(**data["connection"])
        if "gateway" in data:
            config["gateway"] = GatewayConfig(**data["gateway"])
        if "webhooks" in data:
            config["webhooks"] = [
                WebhookConfig(**wh) for wh in data["webhooks"]
            ]

        self._config = config
        return config

    def save(self, config: InstanceConfigDict | None = None) -> None:
        """保存配置文件"""
        if config is not None:
            self._config = config
        elif self._config is None:
            self._config = self._default_config()

        # 确保目录存在
        self.instance_dir.mkdir(parents=True, exist_ok=True)

        # 使用 tomli_w 写入 TOML
        with open(self.config_file, "wb") as f:
            tomli_w.dump(self._config, f)  # type: ignore[arg-type]

    def update(
        self,
        ws_url: str | None = None,
        token: str | None = None,
        log_level: str | None = None,
    ) -> InstanceConfigDict:
        """更新配置并保存"""
        config = self.load()

        if ws_url is not None:
            config["connection"]["ws_url"] = ws_url
        if token is not None:
            config["connection"]["token"] = token
        if log_level is not None:
            config["gateway"]["log_level"] = log_level

        self.save(config)
        return config

    def add_webhook(
        self,
        url: str,
        events: list[str] | None = None,
        secret: str | None = None,
    ) -> InstanceConfigDict:
        """添加 Webhook"""
        config = self.load()

        webhook = WebhookConfig(url=url)
        if events:
            webhook["events"] = events
        if secret:
            webhook["secret"] = secret

        config["webhooks"].append(webhook)
        self.save(config)
        return config

    def remove_webhook(self, url_or_index: str | int) -> bool:
        """移除 Webhook，返回是否成功"""
        config = self.load()

        if isinstance(url_or_index, int):
            if 0 <= url_or_index < len(config["webhooks"]):
                config["webhooks"].pop(url_or_index)
                self.save(config)
                return True
            return False

        # 按URL移除
        for i, wh in enumerate(config["webhooks"]):
            if wh.get("url") == url_or_index:
                config["webhooks"].pop(i)
                self.save(config)
                return True
        return False

    def write_pid(self, pid: int) -> None:
        """写入 PID 文件"""
        self.instance_dir.mkdir(parents=True, exist_ok=True)
        self.pid_file.write_text(str(pid))

    def clear_pid(self) -> None:
        """清除 PID 文件"""
        try:
            self.pid_file.unlink()
        except OSError:
            pass

    def clear_socket(self) -> None:
        """清除 Socket 文件"""
        try:
            self.socket_file.unlink()
        except OSError:
            pass

    @classmethod
    def list_all(cls) -> list[InstanceConfig]:
        """列出所有实例"""
        if not cls.BASE_DIR.exists():
            return []

        instances: list[InstanceConfig] = []
        for path in cls.BASE_DIR.iterdir():
            if path.is_dir() and (path / "config.toml").exists():
                instances.append(cls(name=path.name))

        return sorted(instances, key=lambda x: x.name)

    def __str__(self) -> str:
        return f"InstanceConfig({self.name})"
