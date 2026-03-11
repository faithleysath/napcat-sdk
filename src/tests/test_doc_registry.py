from __future__ import annotations

import pytest

from napcat.cli.doc.registry import (
    get_cli_operation,
    get_mcp_tool_operation,
    list_cli_operations,
    list_mcp_tool_operations,
    match_resource_uri,
)


def test_registry_exposes_expected_cli_and_mcp_names() -> None:
    assert get_cli_operation("apis") is not None
    assert get_cli_operation("api") is not None
    assert get_cli_operation("files") is not None
    assert get_cli_operation("code") is not None
    assert get_cli_operation("class") is not None

    assert [spec.mcp_tool_name for spec in list_mcp_tool_operations()] == [
        "list_apis",
        "get_api_details",
        "list_code_files",
        "get_code_file",
        "get_class_definition",
    ]
    assert [spec.cli_usage for spec in list_cli_operations()] == [
        "apis",
        "api <NAME>...",
        "files",
        "code <PATH>...",
        "class <NAME>...",
    ]


def test_registry_normalizers_strip_cli_and_mcp_arguments() -> None:
    api_spec = get_mcp_tool_operation("get_api_details")
    code_spec = get_mcp_tool_operation("get_code_file")

    assert api_spec is not None
    assert code_spec is not None
    assert api_spec.normalize_arguments({"names": [" send_private_msg "]}) == {
        "names": ["send_private_msg"],
    }
    assert code_spec.normalize_arguments({"paths": " client.py "}) == {
        "paths": ["client.py"],
    }


def test_registry_rejects_empty_string_arguments() -> None:
    api_spec = get_cli_operation("api")
    code_spec = get_cli_operation("code")

    assert api_spec is not None
    assert code_spec is not None

    with pytest.raises(ValueError, match="non-empty strings only"):
        api_spec.normalize_arguments({"names": [" "]})

    with pytest.raises(ValueError, match="non-empty strings only"):
        code_spec.normalize_arguments({"paths": [" "]})


def test_registry_matches_resource_uri_templates() -> None:
    matched = match_resource_uri("napcat-docs://class/NapCatClient")

    assert matched is not None
    spec, params = matched
    assert spec.key == "class-definition"
    assert params == {"class_name": "NapCatClient"}
