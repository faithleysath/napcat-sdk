"""
Registry for shared CLI and MCP doc operations.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, cast
from urllib.parse import urlparse

from .models import OperationResult
from .render import (
    render_api_details_text,
    render_api_index_text,
    render_class_definitions_text,
    render_code_files_text,
    render_code_index_text,
    render_json_result,
)
from .service import DocService

OperationHandler = Callable[[DocService, Mapping[str, Any]], OperationResult[Any]]
JsonRenderer = Callable[[OperationResult[Any]], Any]
TextRenderer = Callable[[OperationResult[Any]], str]
ArgumentNormalizer = Callable[[Mapping[str, Any]], dict[str, Any]]
ResourceMatcher = Callable[[str], dict[str, str] | None]
ResourceHandler = Callable[[DocService, Mapping[str, str]], OperationResult[Any]]


@dataclass(slots=True, frozen=True)
class OperationSpec:
    key: str
    cli_name: str | None
    mcp_tool_name: str | None
    description: str
    arg_schema: dict[str, Any]
    invoke: OperationHandler
    render_text: TextRenderer
    render_json: JsonRenderer
    normalize_arguments: ArgumentNormalizer


@dataclass(slots=True, frozen=True)
class ResourceSpec:
    key: str
    uri: str | None
    uri_template: str | None
    name: str
    mime_type: str
    description: str
    match_uri: ResourceMatcher
    read: ResourceHandler
    render_text: TextRenderer


def _normalize_no_args(args: Mapping[str, Any]) -> dict[str, Any]:
    del args
    return {}


def _normalize_names_argument(args: Mapping[str, Any]) -> dict[str, Any]:
    raw_names = args.get("names")
    if not isinstance(raw_names, list):
        raise ValueError("Argument 'names' is required and must be a list of strings.")
    candidate_names = cast(list[object], raw_names)
    if not all(isinstance(item, str) for item in candidate_names):
        raise ValueError("Argument 'names' must be a list of strings.")
    names = [item.strip() for item in candidate_names if isinstance(item, str)]
    if not names:
        raise ValueError("Argument 'names' is required and cannot be empty.")
    if any(not item for item in names):
        raise ValueError("Argument 'names' must contain non-empty strings only.")
    return {"names": names}


def _normalize_paths_argument(args: Mapping[str, Any]) -> dict[str, Any]:
    raw_paths = args.get("paths")
    if isinstance(raw_paths, list):
        candidate_paths = cast(list[object], raw_paths)
        if not all(isinstance(path, str) for path in candidate_paths):
            raise ValueError("Argument 'paths' must be a list of strings.")
        paths = [path.strip() for path in candidate_paths if isinstance(path, str)]
    elif isinstance(raw_paths, str):
        paths = [raw_paths.strip()]
    else:
        raise ValueError("Argument 'paths' is required and must be a list of strings.")

    if not paths:
        raise ValueError("Argument 'paths' cannot be empty.")
    if any(not path for path in paths):
        raise ValueError("Argument 'paths' must contain non-empty strings only.")
    return {"paths": paths}


def _parse_static_uri(expected_uri: str) -> ResourceMatcher:
    def _match(uri: str) -> dict[str, str] | None:
        if uri == expected_uri:
            return {}
        return None

    return _match


def _parse_api_uri(uri: str) -> dict[str, str] | None:
    parsed = urlparse(uri)
    if parsed.scheme != "napcat-docs" or parsed.netloc != "api":
        return None
    api_name = parsed.path.lstrip("/")
    if not api_name or api_name == "index":
        return None
    return {"api_name": api_name.rsplit("/", 1)[-1]}


def _parse_code_uri(uri: str) -> dict[str, str] | None:
    parsed = urlparse(uri)
    if parsed.scheme != "napcat-docs" or parsed.netloc != "code":
        return None
    file_path = parsed.path.lstrip("/")
    if not file_path or file_path == "index":
        return None
    return {"file_path": file_path}


def _parse_class_uri(uri: str) -> dict[str, str] | None:
    parsed = urlparse(uri)
    if parsed.scheme != "napcat-docs" or parsed.netloc != "class":
        return None
    class_name = parsed.path.lstrip("/")
    if not class_name:
        return None
    return {"class_name": class_name.rsplit("/", 1)[-1]}


DOC_OPERATIONS: tuple[OperationSpec, ...] = (
    OperationSpec(
        key="list_apis",
        cli_name="apis",
        mcp_tool_name="list_apis",
        description="列出 NapCat SDK 的全部 API",
        arg_schema={"type": "object", "properties": {}},
        invoke=lambda service, _args: service.list_apis(),
        render_text=render_api_index_text,
        render_json=render_json_result,
        normalize_arguments=_normalize_no_args,
    ),
    OperationSpec(
        key="get_api_details",
        cli_name="api",
        mcp_tool_name="get_api_details",
        description="获取 NapCat SDK API 的函数签名、返回类型与相关 TypedDict 定义",
        arg_schema={
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
        invoke=lambda service, args: service.get_api_details(args["names"]),
        render_text=render_api_details_text,
        render_json=render_json_result,
        normalize_arguments=_normalize_names_argument,
    ),
    OperationSpec(
        key="list_code_files",
        cli_name="files",
        mcp_tool_name="list_code_files",
        description="列出 NapCat SDK 源码目录树及每个文件的模块 docstring（文件内容必须通过 get_code_file 访问，不得直接读取文件系统）",
        arg_schema={"type": "object", "properties": {}},
        invoke=lambda service, _args: service.list_code_files(),
        render_text=render_code_index_text,
        render_json=render_json_result,
        normalize_arguments=_normalize_no_args,
    ),
    OperationSpec(
        key="get_code_file",
        cli_name="code",
        mcp_tool_name="get_code_file",
        description="获取 NapCat SDK 指定源码文件的完整内容",
        arg_schema={
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
        invoke=lambda service, args: service.get_code_files(args["paths"]),
        render_text=render_code_files_text,
        render_json=render_json_result,
        normalize_arguments=_normalize_paths_argument,
    ),
    OperationSpec(
        key="get_class_definition",
        cli_name="class",
        mcp_tool_name="get_class_definition",
        description="根据类名查询类定义和其所在源码文件路径",
        arg_schema={
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
        invoke=lambda service, args: service.get_class_definitions(args["names"]),
        render_text=render_class_definitions_text,
        render_json=render_json_result,
        normalize_arguments=_normalize_names_argument,
    ),
)


DOC_RESOURCES: tuple[ResourceSpec, ...] = (
    ResourceSpec(
        key="api-index",
        uri="napcat-docs://api/index",
        uri_template=None,
        name="NapCat API Index",
        mime_type="text/markdown",
        description="NapCat SDK API 列表概览",
        match_uri=_parse_static_uri("napcat-docs://api/index"),
        read=lambda service, _params: service.list_apis(),
        render_text=render_api_index_text,
    ),
    ResourceSpec(
        key="code-index",
        uri="napcat-docs://code/index",
        uri_template=None,
        name="NapCat Source Code Index",
        mime_type="text/markdown",
        description="NapCat SDK 源码目录树与模块 docstring",
        match_uri=_parse_static_uri("napcat-docs://code/index"),
        read=lambda service, _params: service.list_code_files(),
        render_text=render_code_index_text,
    ),
    ResourceSpec(
        key="api-detail",
        uri=None,
        uri_template="napcat-docs://api/{api_name}",
        name="NapCat API Detail",
        mime_type="text/markdown",
        description="NapCat SDK API 的函数签名、返回类型与相关 TypedDict 源码",
        match_uri=_parse_api_uri,
        read=lambda service, params: service.get_api_details([params["api_name"]]),
        render_text=render_api_details_text,
    ),
    ResourceSpec(
        key="code-file",
        uri=None,
        uri_template="napcat-docs://code/{file_path}",
        name="NapCat Source Code File",
        mime_type="text/markdown",
        description="NapCat SDK 源码文件的完整内容",
        match_uri=_parse_code_uri,
        read=lambda service, params: service.get_code_files([params["file_path"]]),
        render_text=render_code_files_text,
    ),
    ResourceSpec(
        key="class-definition",
        uri=None,
        uri_template="napcat-docs://class/{class_name}",
        name="NapCat Class Definition",
        mime_type="text/markdown",
        description="按类名查询类定义和文件路径",
        match_uri=_parse_class_uri,
        read=lambda service, params: service.get_class_definitions([params["class_name"]]),
        render_text=render_class_definitions_text,
    ),
)

_CLI_OPERATIONS = {
    spec.cli_name: spec
    for spec in DOC_OPERATIONS
    if spec.cli_name is not None
}

_MCP_TOOL_OPERATIONS = {
    spec.mcp_tool_name: spec
    for spec in DOC_OPERATIONS
    if spec.mcp_tool_name is not None
}


def get_cli_operation(name: str) -> OperationSpec | None:
    return _CLI_OPERATIONS.get(name)


def get_mcp_tool_operation(name: str) -> OperationSpec | None:
    return _MCP_TOOL_OPERATIONS.get(name)


def list_mcp_tool_operations() -> tuple[OperationSpec, ...]:
    return tuple(spec for spec in DOC_OPERATIONS if spec.mcp_tool_name is not None)


def list_mcp_resources() -> tuple[ResourceSpec, ...]:
    return tuple(spec for spec in DOC_RESOURCES if spec.uri is not None)


def list_mcp_resource_templates() -> tuple[ResourceSpec, ...]:
    return tuple(spec for spec in DOC_RESOURCES if spec.uri_template is not None)


def match_resource_uri(uri: str) -> tuple[ResourceSpec, dict[str, str]] | None:
    for spec in DOC_RESOURCES:
        params = spec.match_uri(uri)
        if params is not None:
            return spec, params
    return None
