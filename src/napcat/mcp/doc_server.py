import datetime
import sys
from typing import Any, cast
from urllib.parse import urlparse

import orjson

# --- 1. 数据层 (模拟 NapCat 文档数据) ---
API_DATA: dict[str, dict[str, str]] = {
    "send_private_msg": {
        "api_code": "def send_private_msg(user_id: int, message: str) -> dict:\n    # 发送私聊消息...",
        "description": "向指定用户发送私聊消息。"
    },
    "send_group_msg": {
        "api_code": "def send_group_msg(group_id: int, message: str) -> dict:\n    # 发送群消息...",
        "description": "向指定群组发送消息。"
    },
    "get_login_info": {
        "api_code": "def get_login_info() -> dict:\n    # 获取登录号信息...",
        "description": "获取当前登录机器人的详细信息。"
    }
}

# --- 2. 业务逻辑层 (复用核心) ---
def logic_get_index() -> str:
    """生成 API 目录索引"""
    lines: list[str] = ["# NapCat API Index"]
    for name, info in API_DATA.items():
        lines.append(f"- **{name}**: {info['description']}")
    return "\n".join(lines)

def logic_get_details(api_names: list[str]) -> str:
    """批量获取 API 详情"""
    results: list[str] = []
    for name in api_names:
        if info := API_DATA.get(name):
            results.append(f"## {name}\n> {info['description']}\n\n```python\n{info['api_code']}\n```")
        else:
            results.append(f"## {name}\n(API not found)")
    return "\n---\n".join(results)

# --- 3. 协议工具层 ---
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
    URI_INDEX = "napcat-docs://api/index"
    URI_TEMPLATE = "napcat-docs://api/{api_name}"

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
                        "capabilities": {
                            "tools": {},
                            "resources": {},
                            "logging": {}
                        },
                        "serverInfo": {"name": "napcat-docs", "version": "2.0"}
                    }

                case "notifications/initialized":
                    continue # 通知无需回复

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
                        "resources": [{
                            "uri": URI_INDEX,
                            "name": "NapCat API Index",
                            "mimeType": "text/markdown",
                            "description": "API 列表概览"
                        }]
                    }

                case "resources/templates/list":
                    resp["result"] = {
                        "resourceTemplates": [{
                            "uriTemplate": URI_TEMPLATE,
                            "name": "API Detail",
                            "mimeType": "text/markdown",
                            "description": "API 源码与详情"
                        }]
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

                    if uri == URI_INDEX:
                        content = logic_get_index()
                    elif uri.startswith("napcat-docs://api/"):
                        # 更稳健地解析 URI，避免查询参数影响结果
                        parsed = urlparse(uri)
                        path = parsed.path
                        api_name: str = path.rsplit("/", 1)[-1]
                        if not api_name:
                            raise ValueError(f"Invalid API URI: {uri}")
                        content = logic_get_details([api_name])
                    else:
                        raise ValueError(f"Unknown URI: {uri}")

                    resp["result"] = {
                        "contents": [{"uri": uri, "mimeType": "text/markdown", "text": content}]
                    }

                # --- 工具发现 (Tool Discovery) ---
                case "tools/list":
                    resp["result"] = {
                        "tools": [
                            {
                                "name": "list_apis",
                                "description": "查看所有可用 API 的列表",
                                "inputSchema": {"type": "object", "properties": {}}
                            },
                            {
                                "name": "get_api_details",
                                "description": "获取一个或多个 API 的详细源码定义",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "names": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "API 名称列表 (例如 ['send_private_msg'])"
                                        }
                                    },
                                    "required": ["names"]
                                }
                            }
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
                            # 即使客户端传了单个字符串，也尽量兼容处理，但标准是列表
                            raw_names = cast(Any, args.get("names"))
                            names: list[str]
                            if isinstance(raw_names, str):
                                names = [raw_names]
                            elif isinstance(raw_names, list):
                                candidate_names = cast(list[Any], raw_names)
                                if not all(isinstance(item, str) for item in candidate_names):
                                    raise ValueError("Argument 'names' must be a list of strings.")
                                names = [cast(str, item) for item in candidate_names]
                            else:
                                raise ValueError("Argument 'names' is required and cannot be empty.")
                            if not names:
                                raise ValueError("Argument 'names' is required and cannot be empty.")
                            result_text = logic_get_details(names)
                        case _:
                            raise ValueError(f"Unknown tool: {name}")

                    resp["result"] = {"content": [{"type": "text", "text": result_text}]}

                # --- 未知请求 ---
                case _:
                    # 仅对 request 返回 Method not found；notification 静默忽略
                    if msg_id is not None:
                        log(f"Method not found: {method}")
                        resp["error"] = {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }

            # 仅对 request（有 id）回复，且按键存在性判断 result/error
            if msg_id is not None and ("result" in resp or "error" in resp):
                send_response(resp)

        except Exception as e:
            if msg_id is not None:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32000, "message": str(e)}
                }
                send_response(err_resp)
            log(f"Error processing request: {e}")

if __name__ == "__main__":
    main()
