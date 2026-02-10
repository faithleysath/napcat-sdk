import sys
from typing import Any

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

def main():
    sys.stderr.write("Starting Modern NapCat Docs Server (stdio/orjson)...\n")

    # 预定义常量
    PROTOCOL_VERSION = "2024-11-05"
    URI_INDEX = "napcat-docs://api/index"
    URI_TEMPLATE = "napcat-docs://api/{api_name}"

    for line in sys.stdin.buffer:
        msg_id: Any | None = None
        try:
            req = orjson.loads(line)
            msg_id = req.get("id")

            # 默认响应结构
            resp = {"jsonrpc": "2.0", "id": msg_id}

            match req.get("method"):

                # --- 握手 ---
                case "initialize":
                    resp["result"] = {
                        "protocolVersion": PROTOCOL_VERSION,
                        "capabilities": {
                            "tools": {},
                            "resources": {}
                        },
                        "serverInfo": {"name": "napcat-docs", "version": "2.0"}
                    }

                case "notifications/initialized":
                    continue # 通知无需回复

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
                    uri = req["params"]["uri"]
                    content = ""

                    if uri == URI_INDEX:
                        content = logic_get_index()
                    elif uri.startswith("napcat-docs://api/"):
                        # 解析 URI 提取单个 name
                        api_name = uri.split("/")[-1]
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
                    name = params.get("name")
                    args = params.get("arguments", {})

                    match name:
                        case "list_apis":
                            result_text = logic_get_index()
                        case "get_api_details":
                            # 即使客户端传了单个字符串，也尽量兼容处理，但标准是列表
                            names = args.get("names", [])
                            result_text = logic_get_details(names)
                        case _:
                            raise ValueError(f"Unknown tool: {name}")

                    resp["result"] = {"content": [{"type": "text", "text": result_text}]}

                # --- 未知请求 ---
                case _:
                    # 仅当有 id 时才报错，避免回复 notification
                    if msg_id is not None:
                        raise ValueError("Method not found")

            if resp.get("result") or resp.get("error"):
                send_response(resp)

        except Exception as e:
            if msg_id is not None:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32000, "message": str(e)}
                }
                send_response(err_resp)
            sys.stderr.write(f"Error processing: {e}\n")

if __name__ == "__main__":
    main()
