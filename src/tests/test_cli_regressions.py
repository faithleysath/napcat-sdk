from __future__ import annotations

import json
import os
from collections.abc import Callable
from pathlib import Path

import pytest

from napcat.cli.commands.list import cmd_list
from napcat.cli.commands.start import cmd_start
from napcat.cli.config import InstanceConfig
from napcat.cli.gateway import daemon as daemon_module
from napcat.cli.mcp import doc_server


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
    content = doc_server.logic_get_code_file("client.py")
    assert "class NapCatClient" in content


def test_doc_server_reads_llms_txt_content() -> None:
    content = doc_server.logic_get_llms_txt()
    assert content.startswith("# napcat-sdk")


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
