"""
Generate `src/napcat/client_api.py` from OpenAPI + generated schemas.

默认输入：
- OpenAPI: NapCatQQ/packages/napcat-schema/dist/openapi.json
- Schemas: src/napcat/types/schemas.py

默认输出：
- src/napcat/client_api.py
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from typing import Any, cast


DEFAULT_OPENAPI = Path("NapCatQQ/packages/napcat-schema/dist/openapi.json")
DEFAULT_SCHEMAS = Path("src/napcat/types/schemas.py")
DEFAULT_OUTPUT = Path("src/napcat/client_api.py")


def snake_to_classname(s: str) -> str:
    if s.startswith("_"):
        s = "field" + s
    if s.startswith("."):
        s = "field_" + s[1:]
    parts = s.split("_")
    return "".join(word[0].upper() + word[1:] for word in parts if word)


def sanitize_method_name(action: str) -> str:
    name = action.replace(".", "dot_")
    name = re.sub(r"\W", "_", name)
    if not name:
        return "unknown_action"
    if name[0].isdigit():
        return f"field_{name}"
    return name


def collect_schema_symbols(schema_source: str) -> set[str]:
    module = ast.parse(schema_source)
    symbols: set[str] = set()

    for node in module.body:
        if isinstance(node, ast.ClassDef):
            symbols.add(node.name)
            continue
        if isinstance(node, ast.TypeAlias):
            symbols.add(node.name.id)
            continue
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    symbols.add(target.id)

    return symbols


def get_dict(value: Any) -> dict[str, Any]:
    return cast(dict[str, Any], value) if isinstance(value, dict) else {}


def build_docstring(summary: str, tag: str) -> str:
    safe_summary = summary or "未提供描述"
    safe_tag = tag or ""
    return (
        '        """\n'
        f"        {safe_summary}\n\n"
        f"        标签: {safe_tag}\n"
        '        """'
    )


def generate_client_api_code(openapi: dict[str, Any], schema_symbols: set[str]) -> tuple[str, int]:
    paths = get_dict(openapi.get("paths"))

    method_chunks: list[str] = []
    imported_types: set[str] = set()
    uses_unpack = False

    for path, endpoint in paths.items():
        endpoint_dict = get_dict(endpoint)
        if not endpoint_dict:
            continue

        post_dict = get_dict(endpoint_dict.get("post"))
        if not post_dict:
            continue

        raw_operation_id = post_dict.get("operationId")
        action = raw_operation_id if isinstance(raw_operation_id, str) else path.lstrip("/")
        if not action:
            continue

        method_name = sanitize_method_name(action)
        request_type = f"{snake_to_classname(action)}PostRequest"
        response_type = f"{snake_to_classname(action)}PostResponse"

        request_schema: Any = None
        request_body = get_dict(post_dict.get("requestBody"))
        content = get_dict(request_body.get("content"))
        app_json = get_dict(content.get("application/json"))
        if app_json:
            request_schema = app_json.get("schema")

        response_ann = "Any"
        if response_type in schema_symbols:
            response_ann = response_type
            imported_types.add(response_type)

        raw_summary = post_dict.get("summary")
        summary = raw_summary if isinstance(raw_summary, str) else ""
        raw_tags = post_dict.get("tags")
        tags: list[str] = []
        if isinstance(raw_tags, list):
            for item in cast(list[Any], raw_tags):
                if isinstance(item, str):
                    tags.append(item)
        first_tag = tags[0] if tags else ""
        doc = build_docstring(summary, first_tag)

        is_union_request = isinstance(request_schema, dict) and (
            "oneOf" in request_schema or "anyOf" in request_schema
        )

        request_type_exists = request_type in schema_symbols
        if request_type_exists:
            imported_types.add(request_type)

        if is_union_request:
            payload_ann = request_type if request_type_exists else "Any"
            method_chunks.append(
                f"""
    async def {method_name}(self, payload: {payload_ann}) -> {response_ann}:
{doc}
        return await self._client.call_action({action!r}, payload)
    """
            )
        elif request_schema:
            if request_type_exists:
                uses_unpack = True
                method_chunks.append(
                    f"""
    async def {method_name}(self, **kwargs: Unpack[{request_type}]) -> {response_ann}:
{doc}
        return await self._client.call_action({action!r}, kwargs)
    """
                )
            else:
                method_chunks.append(
                    f"""
    async def {method_name}(self, **kwargs: Any) -> {response_ann}:
{doc}
        return await self._client.call_action({action!r}, kwargs)
    """
                )
        else:
            method_chunks.append(
                f"""
    async def {method_name}(self, **kwargs: Any) -> {response_ann}:
{doc}
        return await self._client.call_action({action!r}, kwargs)
    """
            )

    typing_import = "from typing import Any, Protocol"
    if uses_unpack:
        typing_import = "from typing import Any, Unpack, Protocol"

    schemas_import = ""
    if imported_types:
        joined = "\n".join(f"    {name}," for name in sorted(imported_types))
        schemas_import = f"from .types.schemas import (\n{joined}\n)\n"

    methods_code = "".join(method_chunks)
    api_count = len(method_chunks)

    code = f'''# Auto-generated file. Do not modify directly.
# 自动生成的文件。请勿直接修改。

from collections.abc import Mapping
{typing_import}
{schemas_import}
# 定义一个 Protocol，避免循环导入 Client 类，同时保证类型提示
class CallActionProtocol(Protocol):
    async def call_action(self, action: str, params: Mapping[str, Any] | None = None) -> Any: ...


class NapCatAPI:
    """
    NapCat API 命名空间。
    所有自动生成的方法都挂载于此，通过 client.api.xxx 调用。
    """

    def __init__(self, client: CallActionProtocol):
        self._client = client

{methods_code}
'''
    return code, api_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate src/napcat/client_api.py")
    parser.add_argument("--openapi", default=str(DEFAULT_OPENAPI), help="Path to openapi.json")
    parser.add_argument("--schemas", default=str(DEFAULT_SCHEMAS), help="Path to schemas.py")
    parser.add_argument("--out", default=str(DEFAULT_OUTPUT), help="Path to client_api.py")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    openapi_path = Path(args.openapi)
    schemas_path = Path(args.schemas)
    out_path = Path(args.out)

    openapi = json.loads(openapi_path.read_text(encoding="utf-8"))
    schema_source = schemas_path.read_text(encoding="utf-8")
    symbols = collect_schema_symbols(schema_source)

    code, api_count = generate_client_api_code(openapi, symbols)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(code, encoding="utf-8")
    print(f"Generated {api_count} API methods -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
