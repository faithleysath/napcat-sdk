"""
NapCat 文档查询核心逻辑

提供文档查询的纯函数，可被 CLI 命令和 MCP 服务器共同使用。
"""

from __future__ import annotations

import ast
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


class ModuleDoc(TypedDict):
    """源码模块文档数据结构。"""

    path: str
    docstring: str


class ClassSourceDoc(TypedDict):
    """类定义源码数据结构。"""

    path: str
    code: str


# 缓存变量
_api_data_cache: dict[str, ApiDoc] | None = None
_class_def_cache: dict[str, list[ClassSourceDoc]] = {}
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


def _scan_class_definitions() -> dict[str, list[ClassSourceDoc]]:
    """遍历源码文件并收集类定义"""
    source_root = get_source_root_path()
    class_map: dict[str, list[ClassSourceDoc]] = {}

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


def get_api_data_map() -> dict[str, ApiDoc]:
    """返回 API 元数据映射。"""
    return dict(_get_api_data())


def get_source_root_path() -> Path:
    """返回源码根目录。"""
    return _get_source_root()


def get_module_docstring(file_path: Path) -> str:
    """返回模块 docstring。"""
    return _extract_module_docstring(file_path)


def list_python_modules() -> tuple[ModuleDoc, ...]:
    """返回源码根目录下全部 Python 模块及其模块文档。"""
    source_root = get_source_root_path()
    modules: list[ModuleDoc] = []

    for root, dirs, files in os.walk(source_root):
        dirs[:] = [
            entry for entry in dirs if not entry.startswith("__") and not entry.startswith(".")
        ]
        dirs.sort()

        root_path = Path(root)
        py_files = sorted(file_name for file_name in files if file_name.endswith(".py"))
        for py_file in py_files:
            file_path = root_path / py_file
            modules.append(
                {
                    "path": file_path.relative_to(source_root).as_posix(),
                    "docstring": get_module_docstring(file_path),
                }
            )

    return tuple(modules)


def get_class_index() -> dict[str, tuple[ClassSourceDoc, ...]]:
    """返回类定义索引。"""
    _ensure_class_index_ready()
    return {
        class_name: tuple(entries)
        for class_name, entries in _class_def_cache.items()
    }
