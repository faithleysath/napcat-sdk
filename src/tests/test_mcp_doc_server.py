from __future__ import annotations

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
