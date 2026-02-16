from __future__ import annotations

import pytest

from napcat.cli.commands.doc import cmd_doc


def test_doc_code_invalid_path_returns_nonzero_exit(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = cmd_doc(doc_command="code", paths=["../pyproject.toml"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Invalid file path: ../pyproject.toml" in captured.out
