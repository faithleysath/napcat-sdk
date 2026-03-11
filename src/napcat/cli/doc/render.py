"""
Renderers for structured doc results.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import asdict
from pathlib import PurePosixPath
from typing import Any

from .models import (
    ApiDetailItem,
    ApiIndexItem,
    ClassDefinitionItem,
    CodeFileItem,
    CodeIndexEntry,
    DocProblem,
    OperationResult,
)

_CODE_INDEX_CATEGORY_GUIDANCE = {
    "api-definitions": "API definitions - use CLI `napcat-sdk doc apis` or MCP `list_apis` to query",
    "typed-dicts": "TypedDict definitions - use CLI `napcat-sdk doc api <NAME>` or MCP `get_api_details`",
}


def render_problem_text(problems: Sequence[DocProblem]) -> str:
    if not problems:
        return ""
    return "# Error\n\n" + "\n".join(problem.message for problem in problems)


def render_api_index_text(result: OperationResult[ApiIndexItem]) -> str:
    if result.problems:
        return render_problem_text(result.problems)

    lines = ["# NapCat API Index"]
    for item in result.items:
        lines.append(f"- **{item.name}**: {item.description}")
    return "\n".join(lines)


def render_json_result(result: OperationResult[Any]) -> dict[str, Any]:
    return {
        "ok": result.ok,
        "items": [asdict(item) for item in result.items],
        "problems": [asdict(problem) for problem in result.problems],
    }


def render_api_details_text(result: OperationResult[ApiDetailItem]) -> str:
    if result.problems:
        return render_problem_text(result.problems)
    return "\n---\n".join(_render_api_detail_item_text(item) for item in result.items)


def render_code_index_text(result: OperationResult[CodeIndexEntry]) -> str:
    if result.problems:
        return render_problem_text(result.problems)

    lines = [
        "# NapCat Source Code Index",
        "",
        "NOTE: File contents can be accessed via CLI `napcat-sdk doc code <PATH>` or MCP tool `get_code_file`.",
        "",
    ]
    lines.extend(_render_code_index_entries(result.items))
    return "\n".join(lines)


def render_code_files_text(result: OperationResult[CodeFileItem]) -> str:
    if result.problems:
        return render_problem_text(result.problems)
    return "\n\n---\n\n".join(_render_code_file_item_text(item) for item in result.items)


def render_class_definitions_text(result: OperationResult[ClassDefinitionItem]) -> str:
    if result.problems:
        return render_problem_text(result.problems)
    return "\n\n---\n\n".join(
        _render_class_definition_item_text(item) for item in result.items
    )


def _render_api_detail_item_text(item: ApiDetailItem) -> str:
    if not item.found:
        return f"## {item.name}\n(API not found)"

    response_type_section = ""
    if item.response_type:
        response_type_section = (
            f"\n\n### Response Type\n\n```python\n{item.response_type}\n```"
        )

    typed_dict_section = ""
    if item.typed_dict_codes:
        typed_dict_blocks = "\n\n".join(
            f"```python\n{code}\n```" for code in item.typed_dict_codes
        )
        typed_dict_section = f"\n\n### Referenced TypedDicts\n\n{typed_dict_blocks}"

    signature = item.signature or "async def unknown(...):\n    pass"
    return (
        f"## {item.name}\n"
        f"```python\n{signature}\n```"
        f"{response_type_section}"
        f"{typed_dict_section}"
    )


def _render_code_index_entries(entries: Iterable[CodeIndexEntry]) -> list[str]:
    lines: list[str] = []
    seen_dirs: set[tuple[str, ...]] = set()

    for entry in entries:
        path = PurePosixPath(entry.path)
        parents = path.parts[:-1]
        for depth in range(1, len(parents) + 1):
            parent_parts = parents[:depth]
            if parent_parts in seen_dirs:
                continue
            seen_dirs.add(parent_parts)
            indent = "  " * depth
            lines.append(f"{indent}## {parent_parts[-1]}/")
        lines.append("")

        indent = "  " * len(parents)
        lines.append(f"{indent}- **{path.name}** (`{entry.path}`)")
        for detail_line in _render_code_index_detail_lines(entry):
            lines.append(f"{indent}  {detail_line}")
        lines.append("")

    return lines


def _render_code_index_detail_lines(entry: CodeIndexEntry) -> tuple[str, ...]:
    if guidance := _CODE_INDEX_CATEGORY_GUIDANCE.get(entry.category):
        return (guidance,)
    if entry.summary:
        return (entry.summary,)
    return ()


def _render_code_file_item_text(item: CodeFileItem) -> str:
    if not item.found:
        problem_text = item.problems[0].message if item.problems else "Unknown error"
        return f"# Error\n\n{problem_text}"

    content = item.content or ""
    return f"# {item.path}\n\n```python\n{content}\n```"


def _render_class_definition_item_text(item: ClassDefinitionItem) -> str:
    if not item.found:
        return f"## {item.name}\n(Class not found)"

    blocks = [
        f"**Source:** `{source.path}`\n\n```python\n{source.code}\n```"
        for source in item.sources
    ]
    return f"## {item.name}\n" + "\n\n---\n\n".join(blocks)
