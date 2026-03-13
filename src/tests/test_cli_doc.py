from __future__ import annotations

import builtins
import json
from typing import cast

import pytest

import napcat.cli as cli_module
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


def test_doc_api_json_not_found_has_stable_problem_contract(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = doc_module.cmd_doc(
        doc_command="api",
        json_output=True,
        names=[" __not_existing_api_for_test__ "],
    )
    captured = capsys.readouterr()

    payload = json.loads(captured.out)
    assert exit_code == 1
    assert payload == {
        "ok": False,
        "items": [
            {
                "name": "__not_existing_api_for_test__",
                "found": False,
                "signature": None,
                "description": None,
                "response_type": None,
                "typed_dict_codes": [],
                "problems": [
                    {
                        "kind": "not_found",
                        "message": "API not found: __not_existing_api_for_test__",
                        "target": "__not_existing_api_for_test__",
                    }
                ],
            }
        ],
        "problems": [],
    }


def test_doc_files_text_keeps_special_file_guidance(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = doc_module.cmd_doc(doc_command="files")
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "# NapCat Source Code Index" in captured.out
    assert (
        "API definitions - use CLI `napcat-sdk doc apis` or MCP `list_apis` to query"
        in captured.out
    )
    assert (
        "TypedDict definitions - use CLI `napcat-sdk doc api <NAME>` or MCP `get_api_details`"
        in captured.out
    )


def test_cli_main_doc_code_json_runs_full_parse_and_dispatch_chain(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = cli_module.main(["doc", "code", "client.py", "--json"])
    captured = capsys.readouterr()

    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["items"][0]["path"] == "client.py"
    assert "class NapCatClient" in payload["items"][0]["content"]


def test_cli_main_doc_api_json_normalizes_argument_whitespace(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = cli_module.main(
        ["doc", "api", " __not_existing_api_for_test__ ", "--json"]
    )
    captured = capsys.readouterr()

    payload = json.loads(captured.out)
    assert exit_code == 1
    assert payload["items"][0]["name"] == "__not_existing_api_for_test__"
    assert payload["items"][0]["problems"][0]["target"] == "__not_existing_api_for_test__"


def test_doc_agent_text_returns_bundle_sections(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = doc_module.cmd_doc(doc_command="agent")
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "# NapCat Agent Bundle" in captured.out
    assert "## CLI Workflow" in captured.out
    assert "## API Index" in captured.out
    assert "uv run napcat-sdk" in captured.out


def test_doc_agent_json_returns_structured_sections(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = doc_module.cmd_doc(doc_command="agent", json_output=True)
    captured = capsys.readouterr()

    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["problems"] == []
    assert payload["items"]
    assert payload["items"][0]["title"] == "Overview"
    assert "Primary CLI entrypoints" in payload["items"][0]["content"]


def test_doc_agent_full_includes_expanded_reference_sections(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = doc_module.cmd_doc(doc_command="agent", full=True)
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "## API Signatures and Responses" in captured.out
    assert "## TypedDict Appendix" in captured.out
    assert "## Key Class Definitions" in captured.out
    assert "## send_private_msg" in captured.out


def test_doc_agent_with_code_embeds_curated_source_files(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = doc_module.cmd_doc(doc_command="agent", with_code=True)
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "## Embedded Source Files" in captured.out
    assert "### client.py" in captured.out
    assert "### cli/__init__.py" in captured.out
    assert "Use `napcat-sdk doc code <PATH>` for additional files" in captured.out


def test_doc_agent_json_with_code_includes_embedded_code_section(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = doc_module.cmd_doc(doc_command="agent", json_output=True, with_code=True)
    captured = capsys.readouterr()

    payload = json.loads(captured.out)
    assert exit_code == 0
    section_titles = [item["title"] for item in payload["items"]]
    assert "Embedded Source Files" in section_titles


def test_doc_agent_ignores_broken_pipe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_broken_pipe(*_args: object, **_kwargs: object) -> None:
        raise BrokenPipeError

    monkeypatch.setattr(builtins, "print", raise_broken_pipe)

    exit_code = doc_module.cmd_doc(doc_command="agent")

    assert exit_code == 0
