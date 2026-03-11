from __future__ import annotations

import json
from typing import cast

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


def test_doc_apis_json_returns_structured_index(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = doc_module.cmd_doc(doc_command="apis", json_output=True)
    captured = capsys.readouterr()

    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["problems"] == []
    assert payload["items"]
    assert isinstance(payload["items"][0], dict)
    first_item = cast(dict[str, str], payload["items"][0])
    assert {"name", "description"} <= set(first_item.keys())


def test_doc_code_json_returns_rendered_content(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = doc_module.cmd_doc(
        doc_command="code",
        json_output=True,
        paths=["client.py"],
    )
    captured = capsys.readouterr()

    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["problems"] == []
    assert isinstance(payload["items"][0], dict)
    first_item = cast(dict[str, str], payload["items"][0])
    assert first_item["path"] == "client.py"
    assert "class NapCatClient" in first_item["content"]
