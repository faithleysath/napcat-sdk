"""
NapCat 文档 MCP 服务器。
"""

from __future__ import annotations

import datetime
import sys
from collections.abc import Callable, Mapping
from typing import Any, cast

import orjson

from ..doc.registry import (
    get_mcp_tool_operation,
    list_mcp_resource_templates,
    list_mcp_resources,
    list_mcp_tool_operations,
    match_resource_uri,
)
from ..doc.service import DocService

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "napcat-docs"
SERVER_VERSION = "2.0"


def send_response(response: dict[str, Any]) -> None:
    """Serialize a JSON-RPC response to stdout."""
    sys.stdout.buffer.write(orjson.dumps(response) + b"\n")
    sys.stdout.buffer.flush()


def log(msg: str) -> None:
    """Write logs to stderr without disturbing MCP stdout."""
    timestamp = datetime.datetime.now().isoformat()
    sys.stderr.write(f"[{timestamp}] {msg}\n")
    sys.stderr.flush()


def handle_request(
    req: Mapping[str, Any],
    *,
    service: DocService | None = None,
    logger: Callable[[str], None] | None = None,
) -> dict[str, Any] | None:
    """Handle a single JSON-RPC request."""
    msg_id = req.get("id")
    actual_service = service or DocService()
    actual_logger = logger or log

    try:
        return _process_request(req, service=actual_service, logger=actual_logger)
    except Exception as exc:
        actual_logger(f"Error processing request: {exc}")
        if msg_id is None:
            return None
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32000, "message": str(exc)},
        }


def _process_request(
    req: Mapping[str, Any],
    *,
    service: DocService,
    logger: Callable[[str], None],
) -> dict[str, Any] | None:
    method = req.get("method")
    msg_id = req.get("id")
    resp: dict[str, Any] = {"jsonrpc": "2.0", "id": msg_id}

    match method:
        case "initialize":
            resp["result"] = {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}, "resources": {}, "logging": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            }
        case "notifications/initialized":
            return None
        case "ping":
            resp["result"] = {}
        case "logging/setLevel":
            resp["result"] = {}
        case "prompts/list":
            resp["result"] = {"prompts": []}
        case "notifications/cancelled":
            params = req.get("params", {})
            if isinstance(params, dict):
                cancelled_params = cast(dict[str, Any], params)
                request_id = cancelled_params.get("requestId")
            else:
                request_id = None
            logger(f"Client cancelled request: {request_id}")
            return None
        case "resources/list":
            resp["result"] = {
                "resources": [
                    {
                        "uri": cast(str, spec.uri),
                        "name": spec.name,
                        "mimeType": spec.mime_type,
                        "description": spec.description,
                    }
                    for spec in list_mcp_resources()
                ]
            }
        case "resources/templates/list":
            resp["result"] = {
                "resourceTemplates": [
                    {
                        "uriTemplate": cast(str, spec.uri_template),
                        "name": spec.name,
                        "mimeType": spec.mime_type,
                        "description": spec.description,
                    }
                    for spec in list_mcp_resource_templates()
                ]
            }
        case "resources/read":
            params = _require_dict(req.get("params"), error="Invalid params for resources/read")
            uri = params.get("uri")
            if not isinstance(uri, str):
                raise ValueError("Invalid or missing 'uri' in resources/read")

            matched_resource = match_resource_uri(uri)
            if matched_resource is None:
                raise ValueError(f"Unknown URI: {uri}")

            spec, resource_params = matched_resource
            result = spec.read(service, resource_params)
            resp["result"] = {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": spec.mime_type,
                        "text": spec.render_text(result),
                    }
                ]
            }
        case "tools/list":
            resp["result"] = {
                "tools": [
                    {
                        "name": cast(str, spec.mcp_tool_name),
                        "description": spec.description,
                        "inputSchema": spec.arg_schema,
                    }
                    for spec in list_mcp_tool_operations()
                ]
            }
        case "tools/call":
            params = _require_dict(req.get("params", {}), error="Invalid params for tools/call")
            name = params.get("name")
            arguments = _require_dict(
                params.get("arguments", {}),
                error="Invalid 'arguments' for tools/call",
            )

            if not isinstance(name, str):
                raise ValueError("Invalid or missing 'name' in tools/call")

            spec = get_mcp_tool_operation(name)
            if spec is None:
                raise ValueError(f"Unknown tool: {name}")

            normalized_arguments = spec.normalize_arguments(arguments)
            result = spec.invoke(service, normalized_arguments)
            resp["result"] = {
                "content": [{"type": "text", "text": spec.render_text(result)}]
            }
        case _:
            if msg_id is not None:
                logger(f"Method not found: {method}")
                resp["error"] = {
                    "code": -32601,
                    "message": f"Method not found: {method}",
                }
            else:
                return None

    if msg_id is None:
        return None
    return resp


def _require_dict(value: Any, *, error: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(error)
    return cast(dict[str, Any], value)


def main() -> None:
    log("Starting Modern NapCat Docs Server (stdio/orjson)...")
    service = DocService()

    for line in sys.stdin.buffer:
        line_content = line.strip()
        if not line_content:
            continue

        try:
            req_obj = orjson.loads(line_content)
            if not isinstance(req_obj, dict):
                raise ValueError("Invalid JSON-RPC request: payload must be an object")
            req = cast(dict[str, Any], req_obj)
        except Exception as exc:
            log(f"Error processing request: {exc}")
            continue

        response = handle_request(req, service=service, logger=log)
        if response is not None:
            send_response(response)


if __name__ == "__main__":
    main()
