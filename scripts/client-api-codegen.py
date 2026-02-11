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


def _extract_example_value(examples_obj: Any, preferred_key: str | None = None) -> Any:
    examples = get_dict(examples_obj)
    if not examples:
        return None

    candidate_keys: list[str] = []
    if preferred_key is not None:
        candidate_keys.append(preferred_key)
    candidate_keys.extend(k for k in examples.keys() if k not in candidate_keys)

    for key in candidate_keys:
        item = get_dict(examples.get(key))
        if not item:
            continue
        # 按需求：遇到 $ref 直接忽略
        if "$ref" in item:
            continue
        if "value" in item:
            return item.get("value")

    return None


def _format_json_block(value: Any, max_chars: int = 2000) -> str:
    text = json.dumps(value, ensure_ascii=False, indent=2)
    if len(text) > max_chars:
        text = text[: max_chars - 15].rstrip() + "\n... (truncated)"
    return text


def build_docstring(
    summary: str,
    description: str,
    tag: str,
    request_example: Any,
    success_data_example: Any,
) -> str:
    safe_summary = summary or "未提供描述"
    lines: list[str] = ['        """', f"        {safe_summary}"]

    if description:
        lines.extend(["", "        描述:"])
        for part in description.splitlines() or [description]:
            if part.strip() == "":
                lines.append("")
            else:
                lines.append(f"        {part}")

    lines.extend(["", f"        标签: {tag or ''}"])

    if request_example is not None:
        lines.extend(["", "        请求示例:"])
        req_block = _format_json_block(request_example)
        for line in req_block.splitlines():
            if line.strip() == "":
                lines.append("")
            else:
                lines.append(f"        {line}")

    if success_data_example is not None:
        lines.extend(["", "        成功响应 data 示例:"])
        resp_block = _format_json_block(success_data_example)
        for line in resp_block.splitlines():
            if line.strip() == "":
                lines.append("")
            else:
                lines.append(f"        {line}")

    lines.append('        """')
    return "\n".join(lines)


def generate_client_api_code(
    openapi: dict[str, Any], schema_symbols: set[str]
) -> tuple[str, int]:
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
        action = (
            raw_operation_id if isinstance(raw_operation_id, str) else path.lstrip("/")
        )
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
        raw_description = post_dict.get("description")
        description = (
            raw_description.strip() if isinstance(raw_description, str) else ""
        )
        raw_tags = post_dict.get("tags")
        tags: list[str] = []
        if isinstance(raw_tags, list):
            for item in cast(list[Any], raw_tags):
                if isinstance(item, str):
                    tags.append(item)
        first_tag = tags[0] if tags else ""

        request_examples = app_json.get("examples") if app_json else None
        request_example = _extract_example_value(
            request_examples, preferred_key="Default"
        )

        responses = get_dict(post_dict.get("responses"))
        response_200 = get_dict(responses.get("200"))
        response_content = get_dict(response_200.get("content"))
        response_app_json = get_dict(response_content.get("application/json"))
        response_examples = response_app_json.get("examples")
        success_response_example = _extract_example_value(
            response_examples, preferred_key="Success"
        )
        success_data_example = None
        if isinstance(success_response_example, dict):
            success_data_example = get_dict(success_response_example).get("data")

        doc = build_docstring(
            summary=summary,
            description=description,
            tag=first_tag,
            request_example=request_example,
            success_data_example=success_data_example,
        )

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
        return await self.call_action({action!r}, payload)
    """
            )
        elif request_schema:
            if request_type_exists:
                uses_unpack = True
                method_chunks.append(
                    f"""
    async def {method_name}(self, **kwargs: Unpack[{request_type}]) -> {response_ann}:
{doc}
        return await self.call_action({action!r}, kwargs)
    """
                )
            else:
                method_chunks.append(
                    f"""
    async def {method_name}(self, **kwargs: Any) -> {response_ann}:
{doc}
        return await self.call_action({action!r}, kwargs)
    """
                )
        else:
            method_chunks.append(
                f"""
    async def {method_name}(self, **kwargs: Any) -> {response_ann}:
{doc}
        return await self.call_action({action!r}, kwargs)
    """
            )

    typing_import = "from typing import Any"
    if uses_unpack:
        typing_import = "from typing import Any, Unpack"

    schemas_import = ""
    if imported_types:
        joined = "\n".join(f"    {name}," for name in sorted(imported_types))
        schemas_import = f"from .types.schemas import (\n{joined}\n)\n"

    methods_code = "".join(method_chunks)
    api_count = len(method_chunks)

    code = f'''# Auto-generated file. Do not modify directly.
# 自动生成的文件。请勿直接修改。

"""
NapCat 客户端 API Mixin

自动生成的 API 方法，实现了 OneBot 11 (以及扩展) 的所有 API 调用接口。
混入到 NapCatClient 类中使用。
"""

from collections.abc import Mapping
{typing_import}
{schemas_import}
class NapCatAPIMixin:
    """
    NapCat API mixin。
    所有自动生成的方法都混入 NapCatClient，通过 client.xxx 调用。
    """

    async def call_action(
        self, action: str, params: Mapping[str, Any] | None = None
    ) -> Any:
        raise NotImplementedError

{methods_code}
'''
    return code, api_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate src/napcat/client_api.py")
    parser.add_argument(
        "--openapi", default=str(DEFAULT_OPENAPI), help="Path to openapi.json"
    )
    parser.add_argument(
        "--schemas", default=str(DEFAULT_SCHEMAS), help="Path to schemas.py"
    )
    parser.add_argument(
        "--out", default=str(DEFAULT_OUTPUT), help="Path to client_api.py"
    )
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
