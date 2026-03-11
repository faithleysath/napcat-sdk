from __future__ import annotations

import json
import os
from collections.abc import Callable
from pathlib import Path

import pytest

from napcat.cli.commands.list import cmd_list
from napcat.cli.commands.start import cmd_start
from napcat.cli.config import InstanceConfig
from napcat.cli.doc.service import DocService
from napcat.cli.gateway import daemon as daemon_module


def test_start_foreground_returns_error_when_gateway_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(InstanceConfig, "BASE_DIR", tmp_path)

    config = InstanceConfig("broken")
    config.update(ws_url="ws://127.0.0.1:3001")

    class FakeGateway:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            pass

        async def start(self) -> None:
            raise RuntimeError("startup failed")

    import napcat.cli.commands.start as start_module

    def fake_setup_signal_handlers(_cb: Callable[[], None]) -> None:
        return None

    monkeypatch.setattr(start_module, "Gateway", FakeGateway)
    monkeypatch.setattr(start_module, "setup_signal_handlers", fake_setup_signal_handlers)

    exit_code = cmd_start("broken", foreground=True)
    assert exit_code == 1


def test_doc_server_can_read_main_client_file() -> None:
    result = DocService().get_code_files(["client.py"])
    assert result.ok is True
    assert "class NapCatClient" in (result.items[0].content or "")


def test_instance_is_running_rejects_stale_pid_metadata(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(InstanceConfig, "BASE_DIR", tmp_path)
    config = InstanceConfig("stale")
    config.instance_dir.mkdir(parents=True, exist_ok=True)
    config.pid_file.write_text(
        json.dumps(
            {
                "pid": os.getpid(),
                "started": "Thu Jan  1 00:00:00 1970",
            }
        )
    )

    assert config.is_running() is False
    assert config.pid_file.exists() is False


def test_instance_is_running_rejects_legacy_plain_pid_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(InstanceConfig, "BASE_DIR", tmp_path)
    config = InstanceConfig("legacy")
    config.instance_dir.mkdir(parents=True, exist_ok=True)
    config.pid_file.write_text(str(os.getpid()))

    assert config.is_running() is False
    assert config.pid_file.exists() is False


def test_stop_daemon_rejects_stale_pid_metadata(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    pid_file = tmp_path / "gateway.pid"
    pid_file.write_text(
        json.dumps(
            {
                "pid": 24680,
                "started": "Thu Jan  1 00:00:00 1970",
            }
        )
    )

    kill_calls: list[tuple[int, int]] = []

    def fake_kill(pid: int, sig: int) -> None:
        kill_calls.append((pid, sig))
        if sig == 0:
            return
        raise AssertionError("stale PID should not receive termination signal")

    monkeypatch.setattr(daemon_module.os, "kill", fake_kill)

    def fake_get_process_start_time(_pid: int) -> str:
        return "Fri Feb 20 10:00:00 2026"

    monkeypatch.setattr(
        daemon_module,
        "_get_process_start_time",
        fake_get_process_start_time,
    )

    with pytest.raises(ProcessLookupError, match="Stale PID file"):
        daemon_module.stop_daemon(pid_file)

    assert kill_calls == [(24680, 0)]
    assert pid_file.exists() is False


def test_stop_daemon_rejects_legacy_plain_pid_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    pid_file = tmp_path / "gateway.pid"
    pid_file.write_text("24680")

    kill_calls: list[tuple[int, int]] = []

    def fake_kill(pid: int, sig: int) -> None:
        kill_calls.append((pid, sig))

    monkeypatch.setattr(daemon_module.os, "kill", fake_kill)

    with pytest.raises(ProcessLookupError, match="Invalid PID file format"):
        daemon_module.stop_daemon(pid_file)

    assert kill_calls == []


def test_list_handles_invalid_config_without_crashing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(InstanceConfig, "BASE_DIR", tmp_path)

    valid = InstanceConfig("valid")
    valid.update(ws_url="ws://127.0.0.1:3001")

    broken_dir = tmp_path / "broken"
    broken_dir.mkdir(parents=True, exist_ok=True)
    (broken_dir / "config.toml").write_text("not = [valid", encoding="utf-8")

    exit_code = cmd_list()
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "valid" in captured.out
    assert "broken" in captured.out
    assert "invalid config" in captured.out


def test_start_foreground_reads_rpc_settings_from_config(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(InstanceConfig, "BASE_DIR", tmp_path)

    config = InstanceConfig("rpc")
    config.update(
        ws_url="ws://127.0.0.1:3001",
        rpc_mode=True,
        rpc_host="127.0.0.1",
        rpc_port=18080,
        rpc_token="secret-token",
        rpc_public_host="proxy.example.com",
    )

    captured: dict[str, object] = {}

    class FakeGateway:
        def __init__(self, *_args: object, **kwargs: object) -> None:
            captured.update(kwargs)

        async def start(self) -> None:
            return None

    import napcat.cli.commands.start as start_module

    def fake_setup_signal_handlers(_cb: Callable[[], None]) -> None:
        return None

    monkeypatch.setattr(start_module, "Gateway", FakeGateway)
    monkeypatch.setattr(start_module, "setup_signal_handlers", fake_setup_signal_handlers)

    exit_code = cmd_start("rpc", foreground=True)

    assert exit_code == 0
    assert captured["rpc_mode"] is True
    assert captured["rpc_host"] == "127.0.0.1"
    assert captured["rpc_port"] == 18080
    assert captured["rpc_token"] == "secret-token"
    assert captured["rpc_public_host"] == "proxy.example.com"


def test_list_displays_rpc_summary(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(InstanceConfig, "BASE_DIR", tmp_path)

    config = InstanceConfig("rpc-list")
    config.update(
        ws_url="ws://127.0.0.1:3001",
        rpc_mode=True,
        rpc_host="0.0.0.0",
        rpc_port=18080,
        rpc_public_host="rpc.example.com",
    )

    exit_code = cmd_list()
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "RPC" in captured.out
    assert "ws://rpc.example.com:18080" in captured.out


def test_list_displays_qq_column_from_gateway_status(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(InstanceConfig, "BASE_DIR", tmp_path)
    config = InstanceConfig("qq-bot")
    config.update(ws_url="ws://127.0.0.1:3001")

    def always_running(_self: InstanceConfig) -> bool:
        return True

    monkeypatch.setattr(InstanceConfig, "is_running", always_running)

    class FakeGatewayClient:
        def __init__(self, _socket_path: Path, timeout: float = 30.0):
            self.timeout = timeout

        async def get_status(self) -> dict[str, object]:
            return {"qq": 123456789}

    import napcat.cli.commands.list as list_module

    monkeypatch.setattr(list_module, "GatewayClient", FakeGatewayClient)

    exit_code = cmd_list()
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "QQ" in captured.out
    assert "123456789" in captured.out
