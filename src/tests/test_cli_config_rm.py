from __future__ import annotations

from pathlib import Path

import pytest

import napcat.cli as cli_module
from napcat.cli.config import InstanceConfig


def test_config_rm_removes_instance_directory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(InstanceConfig, "BASE_DIR", tmp_path)
    config = InstanceConfig("demo")
    config.update(ws_url="ws://127.0.0.1:3001")
    config.log_file.write_text("log")

    exit_code = cli_module.main(["config", "rm", "demo"])

    assert exit_code == 0
    assert config.instance_dir.exists() is False


def test_config_rm_refuses_running_instance(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(InstanceConfig, "BASE_DIR", tmp_path)
    config = InstanceConfig("demo")
    config.update(ws_url="ws://127.0.0.1:3001")

    def always_running(_self: InstanceConfig) -> bool:
        return True

    monkeypatch.setattr(InstanceConfig, "is_running", always_running)

    exit_code = cli_module.main(["config", "rm", "demo"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert config.instance_dir.exists()
    assert "Stop it with: napcat-sdk stop demo" in captured.out


def test_config_update_syntax_keeps_backward_compatibility(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(InstanceConfig, "BASE_DIR", tmp_path)

    exit_code = cli_module.main(
        ["config", "demo", "--ws", "ws://127.0.0.1:3001"],
    )

    config = InstanceConfig("demo")
    loaded = config.load()

    assert exit_code == 0
    assert loaded["connection"]["ws_url"] == "ws://127.0.0.1:3001"
