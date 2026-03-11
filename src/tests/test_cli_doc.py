from __future__ import annotations

import pytest

from napcat.cli.commands import doc as doc_module


def test_doc_code_invalid_path_returns_nonzero_exit(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = doc_module.cmd_doc(doc_command="code", paths=["../pyproject.toml"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Invalid file path: ../pyproject.toml" in captured.out


def test_doc_api_not_found_returns_nonzero_exit(
    capsys: pytest.CaptureFixture[str],
) -> None:
    api_name = "__not_existing_api_for_test__"

    exit_code = doc_module.cmd_doc(doc_command="api", names=[api_name])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert f"## {api_name}" in captured.out
    assert "(API not found)" in captured.out


def test_doc_class_not_found_returns_nonzero_exit(
    capsys: pytest.CaptureFixture[str],
) -> None:
    class_name = "__NotExistingClassForTest__"

    exit_code = doc_module.cmd_doc(doc_command="class", names=[class_name])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert f"## {class_name}" in captured.out
    assert "(Class not found)" in captured.out
