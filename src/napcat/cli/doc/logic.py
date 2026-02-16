"""
NapCat 文档查询核心逻辑

提供文档查询的纯函数，可被 CLI 命令和 MCP 服务器共同使用。
"""

from __future__ import annotations

import ast
import importlib.resources
import inspect
import os
import re
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any, ForwardRef, TypeAliasType, TypedDict, get_args, get_origin

from napcat.client_api import NapCatAPIMixin


class ApiDoc(TypedDict):
    """API 文档数据结构"""
    description: str
    sig: str
    response_type: str
    typed_dict_codes: list[str]


# 缓存变量
_api_data_cache: dict[str, ApiDoc] | None = None
_class_def_cache: dict[str, list[dict[str, str]]] = {}
_class_index_ready = False


def _is_typed_dict_class(tp: Any) -> bool:
    """判断是否为 TypedDict 类"""
    return (
        isinstance(tp, type)
        and hasattr(tp, "__required_keys__")
        and hasattr(tp, "__optional_keys__")
    )


def _resolve_forward_ref(tp: Any, globalns: dict[str, Any] | None) -> Any:
    """解析前向引用"""
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
    """格式化类型表达式"""
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
    """构建返回类型文本"""
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
    """收集函数引用的所有 TypedDict"""
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
    """获取 TypedDict 类的源码"""
    try:
        return inspect.getsource(td_cls).rstrip()
    except (OSError, TypeError):
        return f"class {td_cls.__name__}(TypedDict):\n    ..."


def _extract_description(full_doc: str) -> str:
    """截取 docstring 到"标签"行（包含该行）"""
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
    """构建函数签名文本"""
    signature = inspect.signature(func)
    params = list(signature.parameters.values())
    if params and params[0].name == "self":
        signature = signature.replace(parameters=params[1:])

    doc = inspect.getdoc(func) or ""
    if doc:
        return f'async def {func_name}{signature}:\n    """\n{doc}\n    """'
    return f"async def {func_name}{signature}:\n    pass"


def _build_api_data() -> dict[str, ApiDoc]:
    """构建 API 数据"""
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
    """获取 API 数据（带缓存）"""
    global _api_data_cache
    if _api_data_cache is None:
        _api_data_cache = _build_api_data()
    return _api_data_cache


def _get_source_root() -> Path:
    """获取 napcat 包的源码根目录"""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "client.py").is_file() and (parent / "client_api.py").is_file():
            return parent

    # 回退到旧的固定层级，避免极端路径下直接崩溃。
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


def _scan_class_definitions() -> dict[str, list[dict[str, str]]]:
    """遍历源码文件并收集类定义"""
    source_root = _get_source_root()
    class_map: dict[str, list[dict[str, str]]] = {}

    for root, dirs, files in os.walk(source_root):
        dirs[:] = [
            d for d in dirs if not d.startswith("__") and not d.startswith(".")
        ]
        dirs.sort()

        root_path = Path(root)
        py_files = sorted([f for f in files if f.endswith(".py")])
        for py_file in py_files:
            file_path = root_path / py_file
            relative_path = file_path.relative_to(source_root).as_posix()

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                tree = ast.parse(content)
            except Exception:
                continue

            for node in tree.body:
                if not isinstance(node, ast.ClassDef):
                    continue

                class_name = node.name
                class_src = ast.get_source_segment(content, node)
                if not class_src:
                    class_src = f"class {class_name}:\n    ..."

                class_map.setdefault(class_name, []).append(
                    {
                        "path": relative_path,
                        "code": class_src.rstrip(),
                    }
                )

    return class_map


def _ensure_class_index_ready() -> None:
    """确保类索引已准备就绪"""
    global _class_def_cache
    global _class_index_ready
    if not _class_index_ready:
        _class_def_cache = _scan_class_definitions()
        _class_index_ready = True


# --- 公开的 logic_* 函数 ---

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


def logic_get_code_index() -> str:
    """生成源码目录树和模块 docstring 索引"""
    source_root = _get_source_root()
    lines: list[str] = [
        "# NapCat Source Code Index",
        "",
        "NOTE: File contents can be accessed via CLI `napcat-sdk doc code <PATH>` or MCP tool `get_code_file`.",
        "",
    ]

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
                    lines.append(
                        f"{indent}  API definitions - use CLI `napcat-sdk doc apis` or MCP `list_apis` to query"
                    )
                else:  # types/schemas.py
                    lines.append(
                        f"{indent}  TypedDict definitions - use CLI `napcat-sdk doc api <NAME>` or MCP `get_api_details`"
                    )
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
            "## API Definitions File\n\n"
            "This file contains all NapCat SDK API definitions.\n\n"
            "CLI: Use `napcat-sdk doc apis` to list all APIs.\n"
            "CLI: Use `napcat-sdk doc api <NAME>` to get API details.\n"
            "MCP: Use `list_apis` and `get_api_details` tools for structured lookup.\n"
        )
    elif normalized_path == "types/schemas.py":
        return (
            f"# {file_path}\n\n"
            "## TypedDict Definitions File\n\n"
            "This file contains all TypedDict type definitions.\n\n"
            "CLI: Use `napcat-sdk doc api <NAME>` to see related TypedDicts.\n"
            "MCP: Use `get_api_details` to include TypedDicts referenced by each API.\n"
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


def logic_get_class_detail(class_name: str) -> str:
    """根据类名查询定义与文件路径"""
    _ensure_class_index_ready()
    infos = _class_def_cache.get(class_name)
    if not infos:
        return f"## {class_name}\n(Class not found)"

    blocks: list[str] = []
    for info in infos:
        blocks.append(
            f"**Source:** `{info['path']}`\n\n"
            f"```python\n{info['code']}\n```"
        )

    return f"## {class_name}\n" + "\n\n---\n\n".join(blocks)


def logic_get_class_details(class_names: list[str]) -> str:
    """批量获取类定义与文件路径"""
    results: list[str] = []
    for name in class_names:
        results.append(logic_get_class_detail(name))
    return "\n\n---\n\n".join(results)


def logic_get_llms_txt() -> str:
    """获取 llms.txt 文件内容，为 LLM 提供核心概念和最佳实践"""
    # 首选：通过 importlib.resources 访问包内文件（pip 安装后）
    try:
        files = importlib.resources.files("napcat")
        llms_file = files.joinpath("llms.txt")
        if llms_file.is_file():
            return llms_file.read_text(encoding="utf-8")
    except Exception:
        pass

    # 后备：开发时从项目根目录读取 (repo_root/llms.txt)
    source_root = _get_source_root()
    dev_path = source_root.parent.parent / "llms.txt"
    if dev_path.is_file():
        return dev_path.read_text(encoding="utf-8")

    return "# Error\n\nllms.txt not found in package or project root"
