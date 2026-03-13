from __future__ import annotations

import pytest

import napcat.cli as cli_module


def test_cli_tldr_outputs_quick_reference(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = cli_module.main(["tldr"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "NapCat CLI TL;DR" in captured.out
    assert "napcat-sdk config <NAME> --ws <URL>" in captured.out
    assert "--event TYPE supports: message, notice, request, meta, *" in captured.out
    assert "napcat-sdk webhook <NAME> rm [URL] [--event TYPE]..." in captured.out
    assert "napcat-sdk doc agent --full" in captured.out
    assert "napcat-sdk doc agent --full --with-code" in captured.out


def test_cli_help_includes_tldr_command() -> None:
    parser = cli_module.build_parser()
    help_text = parser.format_help()

    assert "tldr" in help_text
