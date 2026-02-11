"""
NapCat 文档 MCP 服务器

实现了基于 MCP 协议的文档查询服务，允许 LLM 通过工具调用查询 NapCat SDK 的 API 定义、签名和 TypedDict 结构。
支持 stdio 通信模式。
"""

import ast
import datetime
import inspect
import os
import re
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any, ForwardRef, TypeAliasType, TypedDict, cast, get_args, get_origin
from urllib.parse import urlparse

import orjson

from ..client_api import NapCatAPIMixin


class ApiDoc(TypedDict):
    description: str
    sig: str
    response_type: str
    typed_dict_codes: list[str]


_api_data_cache: dict[str, ApiDoc] | None = None


def _is_typed_dict_class(tp: Any) -> bool:
    return (
        isinstance(tp, type)
        and hasattr(tp, "__required_keys__")
        and hasattr(tp, "__optional_keys__")
    )


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


def _format_type_expr(tp: Any, globalns: dict[str, Any] | None = None) -> str:
    tp = _resolve_forward_ref(tp, globalns)

    if isinstance(tp, TypeAliasType):
        return tp.__name__

    origin = get_origin(tp)
    if origin is None:
        if isinstance(tp, ForwardRef):
            return tp.__forward_arg__
        return getattr(tp, "__name__", repr(tp))

    args = get_args(tp)
    origin_name = getattr(origin, "__name__", repr(origin).replace("typing.", ""))
    if not args:
        return origin_name
    return (
        f"{origin_name}[{', '.join(_format_type_expr(arg, globalns) for arg in args)}]"
    )


def _build_response_type_text(func: Any) -> str:
    signature = inspect.signature(func)
    return_ann = signature.return_annotation
    if return_ann is inspect.Signature.empty:
        return ""

    func_globals = getattr(func, "__globals__", {})
    resolved = _resolve_forward_ref(return_ann, func_globals)
    if isinstance(resolved, TypeAliasType):
        return f"{resolved.__name__} = {_format_type_expr(resolved.__value__, func_globals)}"
    return _format_type_expr(resolved, func_globals)


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

        td_module_globals = (
            vars(sys.modules.get(current.__module__))
            if sys.modules.get(current.__module__)
            else {}
        )

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
        return f'async def {func_name}{signature}:\n    """\n{doc}\n    """'
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
        if name == "set_online_status":
            description = "设置在线状态"
        sig = _build_signature_text(name, func)
        response_type = _build_response_type_text(func)
        typed_dicts = _collect_referenced_typed_dicts(func)
        typed_dict_codes = [_get_typed_dict_source(td) for td in typed_dicts]

        api_data[name] = {
            "description": description,
            "sig": sig,
            "response_type": response_type,
            "typed_dict_codes": typed_dict_codes,
        }

    return dict(sorted(api_data.items(), key=lambda item: item[0]))


def _get_api_data() -> dict[str, ApiDoc]:
    global _api_data_cache
    if _api_data_cache is None:
        _api_data_cache = _build_api_data()
    return _api_data_cache


# --- 2. 业务逻辑层 (复用核心) ---

# 2.1 API 相关
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
            response_type_section = ""
            if info["response_type"]:
                response_type_section = (
                    f"\n\n### Response Type\n\n```python\n{info['response_type']}\n```"
                )

            typed_dict_section = ""
            if info["typed_dict_codes"]:
                typed_dict_blocks = "\n\n".join(
                    f"```python\n{code}\n```" for code in info["typed_dict_codes"]
                )
                typed_dict_section = (
                    f"\n\n### Referenced TypedDicts\n\n{typed_dict_blocks}"
                )

            results.append(
                f"## {name}\n"
                f"```python\n{info['sig']}\n```"
                f"{response_type_section}"
                f"{typed_dict_section}"
            )
        else:
            results.append(f"## {name}\n(API not found)")
    return "\n---\n".join(results)


# 2.2 源码相关
def _get_source_root() -> Path:
    """获取 napcat 包的源码根目录"""
    # __file__ 是 doc_server.py: src/napcat/mcp/doc_server.py
    current = Path(__file__).resolve()
    # 向上两级到 napcat 目录
    return current.parent.parent


def _extract_module_docstring(file_path: Path) -> str:
    """提取 Python 文件的模块级 docstring"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content)
            docstring = ast.get_docstring(tree)
            return docstring if docstring else "(No module docstring)"
        except SyntaxError:
            return "(Failed to parse)"
    except Exception as e:
        return f"(Error reading file: {e})"


def logic_get_code_index() -> str:
    """生成源码目录树和模块 docstring 索引"""
    source_root = _get_source_root()
    lines: list[str] = ["# NapCat Source Code Index", ""]

    # 遍历源码目录
    for root, dirs, files in os.walk(source_root):
        # 排除 __pycache__ 等目录
        dirs[:] = [
            d for d in dirs if not d.startswith("__") and not d.startswith(".")
        ]
        dirs.sort()

        root_path = Path(root)
        relative_root = root_path.relative_to(source_root)

        # 计算缩进层级
        depth = len(relative_root.parts) if str(relative_root) != "." else 0
        indent = "  " * depth

        # 如果不是根目录，显示目录名
        if str(relative_root) != ".":
            dir_name = relative_root.parts[-1]
            lines.append(f"{indent}## {dir_name}/")
            lines.append("")

        # 列出 Python 文件
        py_files = sorted([f for f in files if f.endswith(".py")])
        for py_file in py_files:
            file_path = root_path / py_file
            relative_path = file_path.relative_to(source_root)
            docstring = _extract_module_docstring(file_path)

            # 使用 POSIX 路径格式
            posix_path = relative_path.as_posix()

            # 特殊处理：client_api.py 和 types/schemas.py
            if posix_path in ("client_api.py", "types/schemas.py"):
                lines.append(f"{indent}- **{py_file}** (`{posix_path}`)")
                if posix_path == "client_api.py":
                    lines.append(f"{indent}  ⚠️ API 定义文件，请使用 list_apis 和 get_api_details 工具查询")
                else:  # types/schemas.py
                    lines.append(f"{indent}  ⚠️ TypedDict 定义文件，请通过 get_api_details 工具查看相关 API 的类型定义")
                lines.append("")
                continue

            lines.append(f"{indent}- **{py_file}** (`{posix_path}`)")
            if docstring and docstring not in ("(No module docstring)", "(Failed to parse)"):
                # 取 docstring 第一行并限制长度
                doc_lines = docstring.strip().split("\n")
                first_line = doc_lines[0]
                if len(first_line) > 80:
                    first_line = first_line[:80] + "..."
                lines.append(f"{indent}  {first_line}")
            lines.append("")

    return "\n".join(lines)


def logic_get_code_file(file_path: str) -> str:
    """获取指定源码文件的完整内容"""
    source_root = _get_source_root()

    # 规范化路径格式
    normalized_path = Path(file_path).as_posix()

    # 特殊处理：client_api.py 和 types/schemas.py
    if normalized_path == "client_api.py":
        return (
            f"# {file_path}\n\n"
            "## ⚠️ 此文件包含 NapCat SDK 的所有 API 定义\n\n"
            "此文件包含大量自动生成的 API 方法定义。为了更高效地查询：\n\n"
            "### 推荐方式\n\n"
            "**使用工具（Tools）：**\n"
            "- `list_apis` - 获取所有可用 API 的列表\n"
            "- `get_api_details` - 获取指定 API 的详细签名、返回类型和 TypedDict 定义\n\n"
            "**使用资源（Resources）：**\n"
            "- `napcat-docs://api/index` - 查看 API 索引\n"
            "- `napcat-docs://api/{api_name}` - 查看特定 API 详情\n\n"
            "### 示例\n\n"
            "```\n"
            "# 获取所有 API\n"
            "list_apis()\n\n"
            "# 获取 send_private_msg 的详细定义\n"
            "get_api_details(names=['send_private_msg'])\n"
            "```\n"
        )
    elif normalized_path == "types/schemas.py":
        return (
            f"# {file_path}\n\n"
            "## ⚠️ 此文件包含 NapCat SDK 的所有 TypedDict 类型定义\n\n"
            "此文件包含大量 TypedDict 定义，这些类型通常与特定 API 方法关联。\n\n"
            "### 推荐方式\n\n"
            "**通过 API 查询相关类型：**\n"
            "使用 `get_api_details` 工具查询 API 时，会自动包含该 API 引用的所有 TypedDict 定义。\n\n"
            "例如，查询 `send_private_msg` 时，会自动返回相关的请求和响应类型定义。\n\n"
            "### 示例\n\n"
            "```\n"
            "# 查询 API 及其相关的 TypedDict\n"
            "get_api_details(names=['send_private_msg'])\n"
            "```\n\n"
            "这样可以获得完整的上下文，而不仅仅是孤立的类型定义。\n"
        )

    # 安全性检查：确保路径在源码目录内
    try:
        target = (source_root / file_path).resolve()
        target.relative_to(source_root)
    except (ValueError, RuntimeError):
        return f"# Error\n\nInvalid file path: {file_path}"

    if not target.is_file():
        return f"# Error\n\nFile not found: {file_path}"

    if target.suffix != ".py":
        return f"# Error\n\nNot a Python file: {file_path}"

    try:
        with open(target, encoding="utf-8") as f:
            content = f.read()
        return f"# {file_path}\n\n```python\n{content}\n```"
    except Exception as e:
        return f"# Error\n\nFailed to read file: {e}"


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
    URI_API_INDEX = "napcat-docs://api/index"
    URI_API_TEMPLATE = "napcat-docs://api/{api_name}"
    URI_CODE_INDEX = "napcat-docs://code/index"
    URI_CODE_TEMPLATE = "napcat-docs://code/{file_path}"

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
                                "description": "列出 NapCat SDK 源码目录树及每个文件的模块 docstring",
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
                                if not all(
                                    isinstance(item, str) for item in candidate_names
                                ):
                                    raise ValueError(
                                        "Argument 'names' must be a list of strings."
                                    )
                                names = [cast(str, item) for item in candidate_names]
                            else:
                                raise ValueError(
                                    "Argument 'names' is required and cannot be empty."
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
