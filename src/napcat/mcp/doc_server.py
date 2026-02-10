import datetime
import inspect
import re
import sys
from collections.abc import Iterable
from typing import Any, ForwardRef, TypeAliasType, TypedDict, cast, get_args, get_origin
from urllib.parse import urlparse

import orjson

from ..client_api import NapCatAPIMixin


class ApiDoc(TypedDict):
    description: str
    sig: str
    typed_dict_codes: list[str]


_api_data_cache: dict[str, ApiDoc] | None = None


def _is_typed_dict_class(tp: Any) -> bool:
    return isinstance(tp, type) and hasattr(tp, "__required_keys__") and hasattr(tp, "__optional_keys__")


def _resolve_forward_ref(tp: Any, globalns: dict[str, Any] | None) -> Any:
    if not isinstance(tp, ForwardRef):
        return tp
    if not globalns:
        return tp
    try:
        return eval(tp.__forward_arg__, globalns, globalns)
    except Exception:
        return tp


def _iter_type_nodes(tp: Any, globalns: dict[str, Any] | None = None) -> Iterable[Any]:
    """递归展开类型注解节点（包含 TypeAliasType、泛型参数等）"""
    tp = _resolve_forward_ref(tp, globalns)
    yield tp

    if isinstance(tp, TypeAliasType):
        yield from _iter_type_nodes(tp.__value__, globalns)
        return

    origin = get_origin(tp)
    if origin is not None:
        yield from _iter_type_nodes(origin, globalns)

    for arg in get_args(tp):
        yield from _iter_type_nodes(arg, globalns)


def _collect_referenced_typed_dicts(func: Any) -> list[type[Any]]:
    direct_found: dict[str, type[Any]] = {}
    signature = inspect.signature(func)
    func_globals = getattr(func, "__globals__", {})

    for param in signature.parameters.values():
        if param.annotation is inspect.Signature.empty:
            continue
        for node in _iter_type_nodes(param.annotation, func_globals):
            if _is_typed_dict_class(node):
                direct_found[node.__name__] = node

    if signature.return_annotation is not inspect.Signature.empty:
        for node in _iter_type_nodes(signature.return_annotation, func_globals):
            if _is_typed_dict_class(node):
                direct_found[node.__name__] = node

    # 递归展开 TypedDict 字段上的依赖（例如 list[OtherTypedDict]）
    resolved: dict[str, type[Any]] = dict(direct_found)
    queue: list[type[Any]] = list(direct_found.values())

    while queue:
        current = queue.pop(0)

        try:
            field_annotations = inspect.get_annotations(current, eval_str=True)
        except Exception:
            field_annotations = getattr(current, "__annotations__", {})

        td_module_globals = vars(sys.modules.get(current.__module__)) if sys.modules.get(current.__module__) else {}

        for field_type in field_annotations.values():
            for node in _iter_type_nodes(field_type, td_module_globals):
                if _is_typed_dict_class(node) and node.__name__ not in resolved:
                    resolved[node.__name__] = node
                    queue.append(node)

    return [resolved[name] for name in sorted(resolved.keys())]


def _get_typed_dict_source(td_cls: type[Any]) -> str:
    try:
        return inspect.getsource(td_cls).rstrip()
    except (OSError, TypeError):
        return f"class {td_cls.__name__}(TypedDict):\n    ..."


def _extract_description(full_doc: str) -> str:
    """截取 docstring 到“标签”行（包含该行）"""
    if not full_doc.strip():
        return "(No description)"

    lines = full_doc.splitlines()
    keep: list[str] = []
    for line in lines:
        keep.append(line)
        if re.match(r"^\s*标签\s*[：:]", line):
            break

    text = "\n".join(keep).strip()
    return text if text else "(No description)"


def _build_signature_text(func_name: str, func: Any) -> str:
    signature = inspect.signature(func)
    params = list(signature.parameters.values())
    if params and params[0].name == "self":
        signature = signature.replace(parameters=params[1:])

    doc = inspect.getdoc(func) or ""
    if doc:
        return f"async def {func_name}{signature}:\n    \"\"\"\n{doc}\n    \"\"\""
    return f"async def {func_name}{signature}:\n    pass"


def _build_api_data() -> dict[str, ApiDoc]:
    api_data: dict[str, ApiDoc] = {}

    members = inspect.getmembers(NapCatAPIMixin, predicate=inspect.isfunction)
    for name, func in members:
        # _ 开头方法也是公开 API；仅排除内部基类入口
        if name == "call_action":
            continue
        if name.startswith("__"):
            continue

        full_doc = inspect.getdoc(func) or ""
        description = _extract_description(full_doc)
        sig = _build_signature_text(name, func)
        typed_dicts = _collect_referenced_typed_dicts(func)
        typed_dict_codes = [_get_typed_dict_source(td) for td in typed_dicts]

        api_data[name] = {
            "description": description,
            "sig": sig,
            "typed_dict_codes": typed_dict_codes,
        }

    return dict(sorted(api_data.items(), key=lambda item: item[0]))


def _get_api_data() -> dict[str, ApiDoc]:
    global _api_data_cache
    if _api_data_cache is None:
        _api_data_cache = _build_api_data()
    return _api_data_cache

# --- 2. 业务逻辑层 (复用核心) ---
def logic_get_index() -> str:
    """生成 API 目录索引"""
    api_data = _get_api_data()
    lines: list[str] = ["# NapCat API Index"]
    for name, info in api_data.items():
        lines.append(f"- **{name}**: {info['description']}")
    return "\n".join(lines)

def logic_get_details(api_names: list[str]) -> str:
    """批量获取 API 详情"""
    api_data = _get_api_data()
    results: list[str] = []
    for name in api_names:
        if info := api_data.get(name):
            typed_dict_section = ""
            if info["typed_dict_codes"]:
                typed_dict_blocks = "\n\n".join(
                    f"```python\n{code}\n```" for code in info["typed_dict_codes"]
                )
                typed_dict_section = f"\n\n### Referenced TypedDicts\n\n{typed_dict_blocks}"

            results.append(
                f"## {name}\n"
                f"```python\n{info['sig']}\n```"
                f"{typed_dict_section}"
            )
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
