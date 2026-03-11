from __future__ import annotations

import io
from collections.abc import Callable

import orjson
import pytest

from napcat.cli.doc.service import DocService
from napcat.cli.mcp import doc_server


def _silent_log(_msg: str) -> None:
    return None


def test_doc_server_tools_list_is_registry_backed() -> None:
    response = doc_server.handle_request(
        {"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        logger=_silent_log,
    )

    assert response is not None
    tools = response["result"]["tools"]
    assert [tool["name"] for tool in tools] == [
        "list_apis",
        "get_api_details",
        "list_code_files",
        "get_code_file",
        "get_class_definition",
    ]


def test_doc_server_tools_call_returns_text_content() -> None:
    service = DocService()
    api_name = service.list_apis().items[0].name

    response = doc_server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_api_details",
                "arguments": {"names": [api_name]},
            },
        },
        service=service,
        logger=_silent_log,
    )

    assert response is not None
    content = response["result"]["content"]
    assert content[0]["type"] == "text"
    assert content[0]["text"].startswith(f"## {api_name}\n")


def test_doc_server_initialize_contract_is_stable() -> None:
    response = doc_server.handle_request(
        {"jsonrpc": "2.0", "id": 1, "method": "initialize"},
        logger=_silent_log,
    )

    assert response == {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}, "resources": {}, "logging": {}},
            "serverInfo": {"name": "napcat-docs", "version": "2.0"},
        },
    }


def test_doc_server_resource_endpoints_work() -> None:
    resources_response = doc_server.handle_request(
        {"jsonrpc": "2.0", "id": 1, "method": "resources/list"},
        logger=_silent_log,
    )
    templates_response = doc_server.handle_request(
        {"jsonrpc": "2.0", "id": 2, "method": "resources/templates/list"},
        logger=_silent_log,
    )
    read_response = doc_server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "resources/read",
            "params": {"uri": "napcat-docs://code/client.py"},
        },
        logger=_silent_log,
    )

    assert resources_response is not None
    assert templates_response is not None
    assert read_response is not None
    assert [resource["uri"] for resource in resources_response["result"]["resources"]] == [
        "napcat-docs://api/index",
        "napcat-docs://code/index",
    ]
    assert [resource["uriTemplate"] for resource in templates_response["result"]["resourceTemplates"]] == [
        "napcat-docs://api/{api_name}",
        "napcat-docs://code/{file_path}",
        "napcat-docs://class/{class_name}",
    ]
    assert "class NapCatClient" in read_response["result"]["contents"][0]["text"]


def test_doc_server_tools_call_normalizes_whitespace_contract() -> None:
    response = doc_server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_code_file",
                "arguments": {"paths": " client.py "},
            },
        },
        logger=_silent_log,
    )

    assert response is not None
    assert response["result"]["content"] == [
        {
            "type": "text",
            "text": response["result"]["content"][0]["text"],
        }
    ]
    assert response["result"]["content"][0]["text"].startswith("# client.py\n\n```python\n")
    assert "class NapCatClient" in response["result"]["content"][0]["text"]


def test_doc_server_code_index_resource_contract_includes_guidance() -> None:
    response = doc_server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "resources/read",
            "params": {"uri": "napcat-docs://code/index"},
        },
        logger=_silent_log,
    )

    assert response is not None
    assert response["result"]["contents"][0] == {
        "uri": "napcat-docs://code/index",
        "mimeType": "text/markdown",
        "text": response["result"]["contents"][0]["text"],
    }
    assert "# NapCat Source Code Index" in response["result"]["contents"][0]["text"]
    assert (
        "API definitions - use CLI `napcat-sdk doc apis` or MCP `list_apis` to query"
        in response["result"]["contents"][0]["text"]
    )
    assert (
        "TypedDict definitions - use CLI `napcat-sdk doc api <NAME>` or MCP `get_api_details`"
        in response["result"]["contents"][0]["text"]
    )


def test_doc_server_invalid_tool_arguments_return_jsonrpc_error() -> None:
    response = doc_server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_api_details",
                "arguments": {"names": "send_private_msg"},
            },
        },
        logger=_silent_log,
    )

    assert response is not None
    assert response["error"]["code"] == -32000
    assert "list of strings" in response["error"]["message"]


def test_doc_server_serve_stream_processes_stdio_protocol_flow() -> None:
    input_buffer = io.BytesIO(
        b"\n"
        + b"{not valid json}\n"
        + orjson.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"})
        + b"\n"
        + orjson.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        + b"\n"
        + orjson.dumps(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "get_code_file",
                    "arguments": {"paths": " client.py "},
                },
            }
        )
        + b"\n"
    )
    output_buffer = io.BytesIO()
    log_messages: list[str] = []

    doc_server.serve_stream(
        input_buffer,
        output_buffer,
        logger=log_messages.append,
    )

    output_lines = output_buffer.getvalue().splitlines()
    initialize_response = orjson.loads(output_lines[0])
    code_file_response = orjson.loads(output_lines[1])

    assert len(output_lines) == 2
    assert initialize_response["result"]["protocolVersion"] == "2024-11-05"
    assert code_file_response["result"]["content"][0]["text"].startswith(
        "# client.py\n\n```python\n"
    )
    assert "class NapCatClient" in code_file_response["result"]["content"][0]["text"]
    assert any(message.startswith("Error processing request:") for message in log_messages)


def test_doc_server_main_wires_stdio_streams(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FakeStdio:
        def __init__(self) -> None:
            self.buffer = io.BytesIO()

    fake_stdin = _FakeStdio()
    fake_stdout = _FakeStdio()
    captured: dict[str, object] = {}
    log_messages: list[str] = []
    fake_logger = log_messages.append

    def fake_serve_stream(
        input_buffer: io.BytesIO,
        output_buffer: io.BytesIO,
        *,
        service: DocService | None = None,
        logger: Callable[[str], None] | None = None,
    ) -> None:
        captured["input_buffer"] = input_buffer
        captured["output_buffer"] = output_buffer
        captured["service"] = service
        captured["logger"] = logger

    monkeypatch.setattr(doc_server.sys, "stdin", fake_stdin)
    monkeypatch.setattr(doc_server.sys, "stdout", fake_stdout)
    monkeypatch.setattr(doc_server, "serve_stream", fake_serve_stream)
    monkeypatch.setattr(doc_server, "log", fake_logger)

    doc_server.main()

    assert log_messages == ["Starting Modern NapCat Docs Server (stdio/orjson)..."]
    assert captured["input_buffer"] is fake_stdin.buffer
    assert captured["output_buffer"] is fake_stdout.buffer
    assert isinstance(captured["service"], DocService)
    assert captured["logger"] is fake_logger
