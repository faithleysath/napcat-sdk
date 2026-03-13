from __future__ import annotations

from pathlib import Path

import pytest

import napcat.cli as cli_module
from napcat.cli.commands.restart import cmd_restart
from napcat.cli.config import InstanceConfig


def _assert_help_exit(exc_info: pytest.ExceptionInfo[SystemExit]) -> None:
    assert exc_info.value.code == 0


def test_config_help_mentions_remove_syntax(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli_module.main(["config", "--help"])

    _assert_help_exit(exc_info)
    captured = capsys.readouterr()

    assert "napcat-sdk config rm <NAME>" in captured.out
    assert "napcat-sdk config mybot --ws ws://127.0.0.1:3001 --token <TOKEN>" in captured.out


def test_config_rm_help_has_dedicated_usage(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = cli_module.main(["config", "rm", "--help"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "usage: napcat-sdk config rm [-h] NAME" in captured.out
    assert "Instance name to remove (must be stopped first)" in captured.out


def test_call_help_includes_examples(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli_module.main(["call", "--help"])

    _assert_help_exit(exc_info)
    captured = capsys.readouterr()

    assert "napcat-sdk call mybot get_login_info" in captured.out
    assert "send_private_msg" in captured.out


def test_doc_help_includes_examples(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli_module.main(["doc", "--help"])

    _assert_help_exit(exc_info)
    captured = capsys.readouterr()

    assert "napcat-sdk doc apis" in captured.out
    assert "napcat-sdk doc class NapCatClient" in captured.out


def test_mcp_help_includes_stdio_guidance(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli_module.main(["mcp", "--help"])

    _assert_help_exit(exc_info)
    captured = capsys.readouterr()

    assert "Run MCP-related commands for NapCat SDK" in captured.out
    assert "stdio MCP server" in captured.out
    assert "napcat-sdk mcp doc" in captured.out


def test_mcp_doc_help_includes_description(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli_module.main(["mcp", "doc", "--help"])

    _assert_help_exit(exc_info)
    captured = capsys.readouterr()

    assert "Start the NapCat docs MCP server over stdio" in captured.out
    assert "source indexes" in captured.out


def test_mcp_without_subcommand_prints_help_and_returns_zero(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = cli_module.main(["mcp"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Run MCP-related commands for NapCat SDK" in captured.out
    assert "napcat-sdk mcp doc" in captured.out


def test_webhook_help_mentions_live_and_config_modes(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli_module.main(["webhook", "demo", "--help"])

    _assert_help_exit(exc_info)
    captured = capsys.readouterr()

    assert "live Gateway state" in captured.out
    assert "local config" in captured.out


def test_webhook_add_help_describes_online_and_offline_behavior(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli_module.main(["webhook", "demo", "add", "--help"])

    _assert_help_exit(exc_info)
    captured = capsys.readouterr()

    assert "live Gateway is updated immediately" in captured.out
    assert "applied on the next start" in captured.out


def test_call_missing_instance_prints_create_hint(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(InstanceConfig, "BASE_DIR", tmp_path)

    exit_code = cli_module.main(["call", "demo", "get_login_info"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Instance 'demo' does not exist." in captured.err
    assert "Create it with: napcat-sdk config demo --ws <URL>" in captured.out


def test_webhook_missing_instance_prints_create_hint(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(InstanceConfig, "BASE_DIR", tmp_path)

    exit_code = cli_module.main(["webhook", "demo", "list"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Instance 'demo' does not exist." in captured.err
    assert "Create it with: napcat-sdk config demo --ws <URL>" in captured.out


def test_restart_missing_instance_avoids_restart_banner(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(InstanceConfig, "BASE_DIR", tmp_path)

    exit_code = cmd_restart("demo")
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Restarting Gateway 'demo'..." not in captured.out
    assert "Instance 'demo' does not exist." in captured.err
    assert "Create it with: napcat-sdk config demo --ws <URL>" in captured.out
