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
from .validation import normalize_string_values

OperationHandler = Callable[[DocService, Mapping[str, Any]], OperationResult[Any]]
JsonRenderer = Callable[[OperationResult[Any]], Any]
TextRenderer = Callable[[OperationResult[Any]], str]
ArgumentNormalizer = Callable[[Mapping[str, Any]], dict[str, Any]]
ResourceMatcher = Callable[[str], dict[str, str] | None]
ResourceHandler = Callable[[DocService, Mapping[str, str]], OperationResult[Any]]
DocServiceMethod = Callable[..., OperationResult[Any]]


@dataclass(slots=True, frozen=True)
class OperationSpec:
    key: str
    cli_name: str | None
    cli_usage: str | None
    cli_help: str | None
    cli_description: str | None
    argument_spec: StringListArgumentSpec | None
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


@dataclass(slots=True, frozen=True)
class StringListArgumentSpec:
    name: str
    metavar: str
    description: str
    invalid_container_message: str
    empty_message: str
    invalid_item_message: str
    allow_single_string: bool = False


@dataclass(slots=True, frozen=True)
class OperationDefinition:
    key: str
    cli_name: str | None
    cli_usage: str | None
    cli_help: str | None
    cli_description: str | None
    mcp_tool_name: str | None
    description: str
    service_method_name: str
    render_text: TextRenderer
    argument_spec: StringListArgumentSpec | None = None


@dataclass(slots=True, frozen=True)
class ResourceDefinition:
    key: str
    name: str
    mime_type: str
    description: str
    match_uri: ResourceMatcher
    service_method_name: str
    render_text: TextRenderer
    uri: str | None = None
    uri_template: str | None = None
    parameter_name: str | None = None


_EMPTY_OBJECT_SCHEMA: dict[str, Any] = {"type": "object", "properties": {}}

_API_NAMES_ARGUMENT = StringListArgumentSpec(
    name="names",
    metavar="NAME",
    description="NapCat API 名称列表 (例如 ['send_private_msg'])",
    invalid_container_message="Argument 'names' is required and must be a list of strings.",
    empty_message="Argument 'names' is required and cannot be empty.",
    invalid_item_message="Argument 'names' must contain non-empty strings only.",
)
_CLASS_NAMES_ARGUMENT = StringListArgumentSpec(
    name="names",
    metavar="NAME",
    description="类名列表 (例如 ['NapCatClient'])",
    invalid_container_message="Argument 'names' is required and must be a list of strings.",
    empty_message="Argument 'names' is required and cannot be empty.",
    invalid_item_message="Argument 'names' must contain non-empty strings only.",
)
_PATHS_ARGUMENT = StringListArgumentSpec(
    name="paths",
    metavar="PATH",
    description="源码文件的相对路径列表 (例如 ['client.py', 'types/__init__.py'])",
    invalid_container_message="Argument 'paths' is required and must be a list of strings.",
    empty_message="Argument 'paths' cannot be empty.",
    invalid_item_message="Argument 'paths' must contain non-empty strings only.",
    allow_single_string=True,
)


def _normalize_no_args(args: Mapping[str, Any]) -> dict[str, Any]:
    del args
    return {}


def _normalize_string_list_argument(
    args: Mapping[str, Any],
    argument_spec: StringListArgumentSpec,
) -> dict[str, Any]:
    return {
        argument_spec.name: list(
            normalize_string_values(
                args.get(argument_spec.name),
                invalid_container_message=argument_spec.invalid_container_message,
                empty_message=argument_spec.empty_message,
                invalid_item_message=argument_spec.invalid_item_message,
                allow_single_string=argument_spec.allow_single_string,
            )
        )
    }


def _build_string_list_schema(argument_spec: StringListArgumentSpec) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            argument_spec.name: {
                "type": "array",
                "items": {"type": "string"},
                "description": argument_spec.description,
            }
        },
        "required": [argument_spec.name],
    }


def _get_service_method(service: DocService, method_name: str) -> DocServiceMethod:
    return cast(DocServiceMethod, getattr(service, method_name))


def _build_operation_handler(
    service_method_name: str,
    *,
    argument_name: str | None = None,
) -> OperationHandler:
    def _invoke(service: DocService, args: Mapping[str, Any]) -> OperationResult[Any]:
        method = _get_service_method(service, service_method_name)
        if argument_name is None:
            return cast(Callable[[], OperationResult[Any]], method)()
        return cast(Callable[[Any], OperationResult[Any]], method)(args[argument_name])

    return _invoke


def _build_resource_handler(
    service_method_name: str,
    *,
    parameter_name: str | None = None,
) -> ResourceHandler:
    def _read(service: DocService, params: Mapping[str, str]) -> OperationResult[Any]:
        method = _get_service_method(service, service_method_name)
        if parameter_name is None:
            return cast(Callable[[], OperationResult[Any]], method)()
        return cast(Callable[[list[str]], OperationResult[Any]], method)([params[parameter_name]])

    return _read


def _build_argument_normalizer(
    argument_spec: StringListArgumentSpec | None,
) -> ArgumentNormalizer:
    if argument_spec is None:
        return _normalize_no_args

    def _normalize(args: Mapping[str, Any]) -> dict[str, Any]:
        return _normalize_string_list_argument(args, argument_spec)

    return _normalize


def _materialize_operation(definition: OperationDefinition) -> OperationSpec:
    actual_normalizer = _build_argument_normalizer(definition.argument_spec)
    actual_schema = (
        _EMPTY_OBJECT_SCHEMA
        if definition.argument_spec is None
        else _build_string_list_schema(definition.argument_spec)
    )
    actual_argument_name = (
        None
        if definition.argument_spec is None
        else definition.argument_spec.name
    )

    return OperationSpec(
        key=definition.key,
        cli_name=definition.cli_name,
        cli_usage=definition.cli_usage,
        cli_help=definition.cli_help,
        cli_description=definition.cli_description or definition.cli_help,
        argument_spec=definition.argument_spec,
        mcp_tool_name=definition.mcp_tool_name,
        description=definition.description,
        arg_schema=actual_schema,
        invoke=_build_operation_handler(
            definition.service_method_name,
            argument_name=actual_argument_name,
        ),
        render_text=definition.render_text,
        render_json=render_json_result,
        normalize_arguments=actual_normalizer,
    )


def _materialize_resource(definition: ResourceDefinition) -> ResourceSpec:
    return ResourceSpec(
        key=definition.key,
        uri=definition.uri,
        uri_template=definition.uri_template,
        name=definition.name,
        mime_type=definition.mime_type,
        description=definition.description,
        match_uri=definition.match_uri,
        read=_build_resource_handler(
            definition.service_method_name,
            parameter_name=definition.parameter_name,
        ),
        render_text=definition.render_text,
    )


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


_OPERATION_DEFINITIONS: tuple[OperationDefinition, ...] = (
    OperationDefinition(
        key="list_apis",
        cli_name="apis",
        cli_usage="apis",
        cli_help="List all available APIs",
        cli_description="List all NapCat SDK API methods",
        mcp_tool_name="list_apis",
        description="列出 NapCat SDK 的全部 API",
        service_method_name="list_apis",
        render_text=render_api_index_text,
    ),
    OperationDefinition(
        key="get_api_details",
        cli_name="api",
        cli_usage="api <NAME>...",
        cli_help="Get API details",
        cli_description="Get detailed information about one or more APIs",
        mcp_tool_name="get_api_details",
        description="获取 NapCat SDK API 的函数签名、返回类型与相关 TypedDict 定义",
        service_method_name="get_api_details",
        render_text=render_api_details_text,
        argument_spec=_API_NAMES_ARGUMENT,
    ),
    OperationDefinition(
        key="list_code_files",
        cli_name="files",
        cli_usage="files",
        cli_help="List source code files",
        cli_description="List the source code directory structure",
        mcp_tool_name="list_code_files",
        description="列出 NapCat SDK 源码目录树及每个文件的模块 docstring（文件内容必须通过 get_code_file 访问，不得直接读取文件系统）",
        service_method_name="list_code_files",
        render_text=render_code_index_text,
    ),
    OperationDefinition(
        key="get_code_file",
        cli_name="code",
        cli_usage="code <PATH>...",
        cli_help="View source code file",
        cli_description="View the content of source code files",
        mcp_tool_name="get_code_file",
        description="获取 NapCat SDK 指定源码文件的完整内容",
        service_method_name="get_code_files",
        render_text=render_code_files_text,
        argument_spec=_PATHS_ARGUMENT,
    ),
    OperationDefinition(
        key="get_class_definition",
        cli_name="class",
        cli_usage="class <NAME>...",
        cli_help="View class definition",
        cli_description="View class definitions by name",
        mcp_tool_name="get_class_definition",
        description="根据类名查询类定义和其所在源码文件路径",
        service_method_name="get_class_definitions",
        render_text=render_class_definitions_text,
        argument_spec=_CLASS_NAMES_ARGUMENT,
    ),
)


DOC_OPERATIONS: tuple[OperationSpec, ...] = tuple(
    _materialize_operation(definition)
    for definition in _OPERATION_DEFINITIONS
)


_RESOURCE_DEFINITIONS: tuple[ResourceDefinition, ...] = (
    ResourceDefinition(
        key="api-index",
        uri="napcat-docs://api/index",
        name="NapCat API Index",
        mime_type="text/markdown",
        description="NapCat SDK API 列表概览",
        match_uri=_parse_static_uri("napcat-docs://api/index"),
        service_method_name="list_apis",
        render_text=render_api_index_text,
    ),
    ResourceDefinition(
        key="code-index",
        uri="napcat-docs://code/index",
        name="NapCat Source Code Index",
        mime_type="text/markdown",
        description="NapCat SDK 源码目录树与模块 docstring",
        match_uri=_parse_static_uri("napcat-docs://code/index"),
        service_method_name="list_code_files",
        render_text=render_code_index_text,
    ),
    ResourceDefinition(
        key="api-detail",
        uri_template="napcat-docs://api/{api_name}",
        name="NapCat API Detail",
        mime_type="text/markdown",
        description="NapCat SDK API 的函数签名、返回类型与相关 TypedDict 源码",
        match_uri=_parse_api_uri,
        service_method_name="get_api_details",
        render_text=render_api_details_text,
        parameter_name="api_name",
    ),
    ResourceDefinition(
        key="code-file",
        uri_template="napcat-docs://code/{file_path}",
        name="NapCat Source Code File",
        mime_type="text/markdown",
        description="NapCat SDK 源码文件的完整内容",
        match_uri=_parse_code_uri,
        service_method_name="get_code_files",
        render_text=render_code_files_text,
        parameter_name="file_path",
    ),
    ResourceDefinition(
        key="class-definition",
        uri_template="napcat-docs://class/{class_name}",
        name="NapCat Class Definition",
        mime_type="text/markdown",
        description="按类名查询类定义和文件路径",
        match_uri=_parse_class_uri,
        service_method_name="get_class_definitions",
        render_text=render_class_definitions_text,
        parameter_name="class_name",
    ),
)


DOC_RESOURCES: tuple[ResourceSpec, ...] = tuple(
    _materialize_resource(definition)
    for definition in _RESOURCE_DEFINITIONS
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


def list_cli_operations() -> tuple[OperationSpec, ...]:
    return tuple(spec for spec in DOC_OPERATIONS if spec.cli_name is not None)


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
