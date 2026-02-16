"""
NapCat 文档 MCP 服务器

实现了基于 MCP 协议的文档查询服务，允许 LLM 通过工具调用查询 NapCat SDK 的 API 定义、签名和 TypedDict 结构。
支持 stdio 通信模式。
"""

from __future__ import annotations

import datetime
import sys
from typing import Any, cast
from urllib.parse import urlparse

import orjson

from ..doc import (
    logic_get_class_detail,
    logic_get_class_details,
    logic_get_code_file,
    logic_get_code_index,
    logic_get_details,
    logic_get_index,
    logic_get_llms_txt,
)


# --- 协议工具层 ---
def send_response(response: dict[str, Any]):
    """使用 orjson 快速序列化并写入 stdout"""
    sys.stdout.buffer.write(orjson.dumps(response) + b"\n")
    sys.stdout.buffer.flush()


def log(msg: str):
    """输出带时间戳的日志到 stderr（不干扰 MCP stdout）"""
    timestamp = datetime.datetime.now().isoformat()
    sys.stderr.write(f"[{timestamp}] {msg}\n")
    sys.stderr.flush()


def main():
    log("Starting Modern NapCat Docs Server (stdio/orjson)...")

    # 预定义常量
    PROTOCOL_VERSION = "2024-11-05"
    URI_API_INDEX = "napcat-docs://api/index"
    URI_API_TEMPLATE = "napcat-docs://api/{api_name}"
    URI_CODE_INDEX = "napcat-docs://code/index"
    URI_CODE_TEMPLATE = "napcat-docs://code/{file_path}"
    URI_CLASS_TEMPLATE = "napcat-docs://class/{class_name}"

    for line in sys.stdin.buffer:
        msg_id: Any | None = None
        try:
            # 去除首尾空白，避免空行导致 JSON 解析异常
            line_content = line.strip()
            if not line_content:
                continue

            req_obj = orjson.loads(line_content)
            if not isinstance(req_obj, dict):
                raise ValueError("Invalid JSON-RPC request: payload must be an object")
            req = cast(dict[str, Any], req_obj)
            msg_id = req.get("id")
            method = cast(str | None, req.get("method"))

            # 默认响应结构
            resp = {"jsonrpc": "2.0", "id": msg_id}

            match method:
                # --- 握手 ---
                case "initialize":
                    resp["result"] = {
                        "protocolVersion": PROTOCOL_VERSION,
                        "capabilities": {"tools": {}, "resources": {}, "logging": {}},
                        "serverInfo": {"name": "napcat-docs", "version": "2.0"},
                    }

                case "notifications/initialized":
                    continue  # 通知无需回复

                # --- 心跳检测 (Ping) ---
                case "ping":
                    # 返回空对象即可，表明存活
                    resp["result"] = {}

                # --- 兼容客户端常见请求 ---
                case "logging/setLevel":
                    # 静默接受日志等级设置
                    resp["result"] = {}

                case "prompts/list":
                    # 当前未提供 prompts，返回空列表
                    resp["result"] = {"prompts": []}

                case "notifications/cancelled":
                    params = req.get("params", {})
                    if isinstance(params, dict):
                        params = cast(dict[str, Any], params)
                        request_id: Any | None = params.get("requestId")
                    else:
                        request_id: Any | None = None
                    log(f"Client cancelled request: {request_id}")

                # --- 资源发现 (Resource Discovery) ---
                case "resources/list":
                    resp["result"] = {
                        "resources": [
                            {
                                "uri": URI_API_INDEX,
                                "name": "NapCat API Index",
                                "mimeType": "text/markdown",
                                "description": "NapCat SDK API 列表概览",
                            },
                            {
                                "uri": URI_CODE_INDEX,
                                "name": "NapCat Source Code Index",
                                "mimeType": "text/markdown",
                                "description": "NapCat SDK 源码目录树与模块 docstring",
                            },
                        ]
                    }

                case "resources/templates/list":
                    resp["result"] = {
                        "resourceTemplates": [
                            {
                                "uriTemplate": URI_API_TEMPLATE,
                                "name": "NapCat API Detail",
                                "mimeType": "text/markdown",
                                "description": "NapCat SDK API 的函数签名、返回类型与相关 TypedDict 源码",
                            },
                            {
                                "uriTemplate": URI_CODE_TEMPLATE,
                                "name": "NapCat Source Code File",
                                "mimeType": "text/markdown",
                                "description": "NapCat SDK 源码文件的完整内容",
                            },
                            {
                                "uriTemplate": URI_CLASS_TEMPLATE,
                                "name": "NapCat Class Definition",
                                "mimeType": "text/markdown",
                                "description": "按类名查询类定义和文件路径",
                            },
                        ]
                    }

                # --- 资源读取 (Resource Read) ---
                case "resources/read":
                    params = req.get("params")
                    if not isinstance(params, dict):
                        raise ValueError("Invalid params for resources/read")
                    params = cast(dict[str, Any], params)

                    uri = cast(str | None, params.get("uri"))
                    if not isinstance(uri, str):
                        raise ValueError("Invalid or missing 'uri' in resources/read")

                    content = ""

                    if uri == URI_API_INDEX:
                        content = logic_get_index()
                    elif uri == URI_CODE_INDEX:
                        content = logic_get_code_index()
                    elif uri.startswith("napcat-docs://api/"):
                        # 解析 API 名称
                        parsed = urlparse(uri)
                        path = parsed.path
                        api_name: str = path.rsplit("/", 1)[-1]
                        if not api_name:
                            raise ValueError(f"Invalid API URI: {uri}")
                        content = logic_get_details([api_name])
                    elif uri.startswith("napcat-docs://code/"):
                        # 解析文件路径
                        parsed = urlparse(uri)
                        # 去掉开头的 /
                        file_path = parsed.path.lstrip("/")
                        if not file_path:
                            raise ValueError(f"Invalid code URI: {uri}")
                        content = logic_get_code_file(file_path)
                    elif uri.startswith("napcat-docs://class/"):
                        parsed = urlparse(uri)
                        class_name = parsed.path.rsplit("/", 1)[-1]
                        if not class_name:
                            raise ValueError(f"Invalid class URI: {uri}")
                        content = logic_get_class_detail(class_name)
                    else:
                        raise ValueError(f"Unknown URI: {uri}")

                    resp["result"] = {
                        "contents": [
                            {"uri": uri, "mimeType": "text/markdown", "text": content}
                        ]
                    }

                # --- 工具发现 (Tool Discovery) ---
                case "tools/list":
                    resp["result"] = {
                        "tools": [
                            {
                                "name": "list_apis",
                                "description": "列出 NapCat SDK 的全部 API",
                                "inputSchema": {"type": "object", "properties": {}},
                            },
                            {
                                "name": "get_api_details",
                                "description": "获取 NapCat SDK API 的函数签名、返回类型与相关 TypedDict 定义",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "names": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "NapCat API 名称列表 (例如 ['send_private_msg'])",
                                        }
                                    },
                                    "required": ["names"],
                                },
                            },
                            {
                                "name": "list_code_files",
                                "description": "列出 NapCat SDK 源码目录树及每个文件的模块 docstring（文件内容必须通过 get_code_file 访问，不得直接读取文件系统）",
                                "inputSchema": {"type": "object", "properties": {}},
                            },
                            {
                                "name": "get_code_file",
                                "description": "获取 NapCat SDK 指定源码文件的完整内容",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "paths": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "源码文件的相对路径列表 (例如 ['client.py', 'types/__init__.py'])",
                                        }
                                    },
                                    "required": ["paths"],
                                },
                            },
                            {
                                "name": "get_class_definition",
                                "description": "根据类名查询类定义和其所在源码文件路径",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "names": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "类名列表 (例如 ['NapCatClient'])",
                                        }
                                    },
                                    "required": ["names"],
                                },
                            },
                            {
                                "name": "get_llms_txt",
                                "description": "获取 llms.txt 文件内容，包含 NapCat SDK 的核心设计哲学、运行模式、事件处理最佳实践和常用代码模式",
                                "inputSchema": {"type": "object", "properties": {}},
                            },
                        ]
                    }

                # --- 工具调用 (Tool Call) ---
                case "tools/call":
                    params = req.get("params", {})
                    if not isinstance(params, dict):
                        raise ValueError("Invalid params for tools/call")
                    params = cast(dict[str, Any], params)

                    name = cast(str | None, params.get("name"))
                    args = params.get("arguments", {})
                    if not isinstance(args, dict):
                        raise ValueError("Invalid 'arguments' for tools/call")
                    args = cast(dict[str, Any], args)

                    match name:
                        case "list_apis":
                            result_text = logic_get_index()
                        case "get_api_details":
                            raw_names = cast(Any, args.get("names"))
                            names: list[str]
                            if isinstance(raw_names, list):
                                candidate_names = cast(list[Any], raw_names)
                                if not all(
                                    isinstance(item, str) for item in candidate_names
                                ):
                                    raise ValueError(
                                        "Argument 'names' must be a list of strings."
                                    )
                                names = [cast(str, item) for item in candidate_names]
                            else:
                                raise ValueError(
                                    "Argument 'names' is required and must be a list of strings."
                                )
                            if not names:
                                raise ValueError(
                                    "Argument 'names' is required and cannot be empty."
                                )
                            result_text = logic_get_details(names)
                        case "list_code_files":
                            result_text = logic_get_code_index()
                        case "get_code_file":
                            raw_paths = args.get("paths")
                            paths: list[str] = []

                            if isinstance(raw_paths, list):
                                paths = [str(p) for p in cast(list[Any], raw_paths)]
                            elif isinstance(raw_paths, str):
                                paths = [raw_paths]
                            else:
                                raise ValueError(
                                    "Argument 'paths' is required and must be a list of strings."
                                )

                            if not paths:
                                raise ValueError("Argument 'paths' cannot be empty.")

                            results = [logic_get_code_file(p) for p in paths]
                            result_text = "\n\n".join(results)
                        case "get_class_definition":
                            raw_names = args.get("names")
                            names: list[str]
                            if isinstance(raw_names, list):
                                candidate_names = cast(list[Any], raw_names)
                                if not all(isinstance(item, str) for item in candidate_names):
                                    raise ValueError(
                                        "Argument 'names' must be a list of strings."
                                    )
                                names = [cast(str, item) for item in candidate_names]
                            else:
                                raise ValueError(
                                    "Argument 'names' is required and must be a list of strings."
                                )
                            if not names:
                                raise ValueError(
                                    "Argument 'names' is required and cannot be empty."
                                )
                            result_text = logic_get_class_details(names)
                        case "get_llms_txt":
                            result_text = logic_get_llms_txt()
                        case _:
                            raise ValueError(f"Unknown tool: {name}")

                    resp["result"] = {
                        "content": [{"type": "text", "text": result_text}]
                    }

                # --- 未知请求 ---
                case _:
                    # 仅对 request 返回 Method not found；notification 静默忽略
                    if msg_id is not None:
                        log(f"Method not found: {method}")
                        resp["error"] = {
                            "code": -32601,
                            "message": f"Method not found: {method}",
                        }

            # 仅对 request（有 id）回复，且按键存在性判断 result/error
            if msg_id is not None and ("result" in resp or "error" in resp):
                send_response(resp)

        except Exception as e:
            if msg_id is not None:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32000, "message": str(e)},
                }
                send_response(err_resp)
            log(f"Error processing request: {e}")


if __name__ == "__main__":
    main()
