"""
Structured service layer for doc queries.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from . import logic
from .models import (
    ApiDetailItem,
    ApiIndexItem,
    ClassDefinitionItem,
    ClassDefinitionSource,
    CodeEntryCategory,
    CodeFileItem,
    CodeIndexEntry,
    DocProblem,
    OperationResult,
)

_CLIENT_API_PATH = "client_api.py"
_SCHEMAS_PATH = "types/schemas.py"


class DocService:
    """Shared application service for CLI and MCP doc operations."""

    def list_apis(self) -> OperationResult[ApiIndexItem]:
        api_data = logic.get_api_data_map()
        items = tuple(
            ApiIndexItem(name=name, description=info["description"])
            for name, info in api_data.items()
        )
        return OperationResult(ok=True, items=items)

    def get_api_details(self, names: Sequence[str]) -> OperationResult[ApiDetailItem]:
        normalized_names, problems = self._normalize_string_sequence(names, field_name="names")
        if problems:
            return OperationResult(ok=False, items=(), problems=problems)

        api_data = logic.get_api_data_map()
        items: list[ApiDetailItem] = []
        has_missing = False
        for name in normalized_names:
            info = api_data.get(name)
            if info is None:
                has_missing = True
                items.append(
                    ApiDetailItem(
                        name=name,
                        found=False,
                        signature=None,
                        description=None,
                        response_type=None,
                        problems=(
                            DocProblem(
                                kind="not_found",
                                message=f"API not found: {name}",
                                target=name,
                            ),
                        ),
                    )
                )
                continue

            items.append(
                ApiDetailItem(
                    name=name,
                    found=True,
                    signature=info["sig"],
                    description=info["description"],
                    response_type=info["response_type"] or None,
                    typed_dict_codes=tuple(info["typed_dict_codes"]),
                )
            )

        return OperationResult(ok=not has_missing, items=tuple(items))

    def list_code_files(self) -> OperationResult[CodeIndexEntry]:
        items = tuple(
            CodeIndexEntry(
                path=module["path"],
                summary=self._build_module_summary(module["docstring"]),
                category=self._get_code_entry_category(module["path"]),
            )
            for module in logic.list_python_modules()
        )
        return OperationResult(ok=True, items=items)

    def get_code_files(self, paths: Sequence[str]) -> OperationResult[CodeFileItem]:
        normalized_paths, problems = self._normalize_string_sequence(paths, field_name="paths")
        if problems:
            return OperationResult(ok=False, items=(), problems=problems)

        items = tuple(self._get_code_file_item(path) for path in normalized_paths)
        ok = all(item.found and not item.problems for item in items)
        return OperationResult(ok=ok, items=items)

    def get_class_definitions(
        self,
        names: Sequence[str],
    ) -> OperationResult[ClassDefinitionItem]:
        normalized_names, problems = self._normalize_string_sequence(names, field_name="names")
        if problems:
            return OperationResult(ok=False, items=(), problems=problems)

        class_index = logic.get_class_index()
        items: list[ClassDefinitionItem] = []
        has_missing = False

        for name in normalized_names:
            infos = class_index.get(name)
            if not infos:
                has_missing = True
                items.append(
                    ClassDefinitionItem(
                        name=name,
                        found=False,
                        sources=(),
                        problems=(
                            DocProblem(
                                kind="not_found",
                                message=f"Class not found: {name}",
                                target=name,
                            ),
                        ),
                    )
                )
                continue

            items.append(
                ClassDefinitionItem(
                    name=name,
                    found=True,
                    sources=tuple(
                        ClassDefinitionSource(path=info["path"], code=info["code"])
                        for info in infos
                    ),
                )
            )

        return OperationResult(ok=not has_missing, items=tuple(items))

    def _get_code_file_item(self, path: str) -> CodeFileItem:
        normalized_path = Path(path).as_posix()
        source_root = logic.get_source_root_path()
        try:
            target = (source_root / normalized_path).resolve()
            target.relative_to(source_root)
        except (ValueError, RuntimeError):
            return CodeFileItem(
                path=normalized_path,
                found=False,
                content=None,
                problems=(
                    DocProblem(
                        kind="invalid_input",
                        message=f"Invalid file path: {normalized_path}",
                        target=normalized_path,
                    ),
                ),
            )

        if not target.is_file():
            return CodeFileItem(
                path=normalized_path,
                found=False,
                content=None,
                problems=(
                    DocProblem(
                        kind="not_found",
                        message=f"File not found: {normalized_path}",
                        target=normalized_path,
                    ),
                ),
            )

        if target.suffix != ".py":
            return CodeFileItem(
                path=normalized_path,
                found=False,
                content=None,
                problems=(
                    DocProblem(
                        kind="invalid_input",
                        message=f"Not a Python file: {normalized_path}",
                        target=normalized_path,
                    ),
                ),
            )

        try:
            content = target.read_text(encoding="utf-8")
        except Exception as exc:
            return CodeFileItem(
                path=normalized_path,
                found=False,
                content=None,
                problems=(
                    DocProblem(
                        kind="internal",
                        message=f"Failed to read file: {exc}",
                        target=normalized_path,
                    ),
                ),
            )

        return CodeFileItem(path=normalized_path, found=True, content=content)

    def _build_module_summary(self, module_doc: str) -> str | None:
        if module_doc in ("(No module docstring)", "(Failed to parse)"):
            return None

        first_line = module_doc.strip().split("\n", 1)[0]
        if not first_line:
            return None
        return first_line[:80] + "..." if len(first_line) > 80 else first_line

    def _get_code_entry_category(self, path: str) -> CodeEntryCategory:
        if path == _CLIENT_API_PATH:
            return "api-definitions"
        if path == _SCHEMAS_PATH:
            return "typed-dicts"
        return "module"

    def _normalize_string_sequence(
        self,
        values: Sequence[object],
        *,
        field_name: str,
    ) -> tuple[tuple[str, ...], tuple[DocProblem, ...]]:
        if isinstance(values, (str, bytes)):
            return (), (
                DocProblem(
                    kind="invalid_input",
                    message=f"Argument '{field_name}' must be a sequence of strings.",
                    target=field_name,
                ),
            )

        normalized = list(values)
        if not normalized:
            return (), (
                DocProblem(
                    kind="invalid_input",
                    message=f"Argument '{field_name}' cannot be empty.",
                    target=field_name,
                ),
            )

        invalid_values = [
            value
            for value in normalized
            if not isinstance(value, str) or not value.strip()
        ]
        if invalid_values:
            return (), (
                DocProblem(
                    kind="invalid_input",
                    message=f"Argument '{field_name}' must contain non-empty strings only.",
                    target=field_name,
                ),
            )

        return tuple(
            value for value in normalized
            if isinstance(value, str) and value.strip()
        ), ()
