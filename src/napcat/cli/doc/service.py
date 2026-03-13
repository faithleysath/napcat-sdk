"""
Structured service layer for doc queries.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from pathlib import Path
from textwrap import dedent

from ..config import InstanceConfig
from . import logic
from .models import (
    AgentBundleSection,
    ApiDetailItem,
    ApiIndexItem,
    ClassDefinitionItem,
    ClassDefinitionSource,
    CodeEntryCategory,
    CodeFileItem,
    CodeIndexEntry,
    DocProblem,
    OperationResult,
    ProblemKind,
)
from .render import (
    render_api_index_text,
    render_class_definitions_text,
    render_code_index_text,
)
from .validation import normalize_string_values

_CLIENT_API_PATH = "client_api.py"
_SCHEMAS_PATH = "types/schemas.py"
_AGENT_EMBEDDED_CODE_PATHS = (
    "client.py",
    "cli/__init__.py",
    "cli/commands/call.py",
    "cli/commands/webhook.py",
    "cli/gateway/webhook.py",
)
_AGENT_TLDR_TEXT = dedent(
    """
    1) Create / inspect config
      napcat-sdk config <NAME> --ws <URL>
      napcat-sdk config mybot --ws ws://127.0.0.1:3001 --token <TOKEN>
      napcat-sdk config mybot
      napcat-sdk config rm mybot

    2) Start / stop / inspect
      napcat-sdk start mybot
      napcat-sdk list
      napcat-sdk log mybot -f
      napcat-sdk stop mybot

    3) Discover and call APIs
      napcat-sdk doc apis
      napcat-sdk doc api send_private_msg
      napcat-sdk call mybot send_private_msg '{"user_id":"123","message":"hi"}'

    4) Manage webhooks
      napcat-sdk webhook mybot add https://example.com/hook --event message
      napcat-sdk webhook mybot list --event notice
      napcat-sdk webhook mybot rm https://example.com/hook --event meta

    5) Inspect docs and code
      napcat-sdk doc files
      napcat-sdk doc code cli/__init__.py
      napcat-sdk doc class NapCatClient
      napcat-sdk doc agent --full
      napcat-sdk doc agent --with-code
    """
).strip()
_TYPED_DICT_NAME_RE = re.compile(r"^class\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", re.MULTILINE)


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
                items.append(self._build_missing_api_detail_item(name))
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

        return self._build_lookup_result(items, has_missing=has_missing)

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
                items.append(self._build_missing_class_definition_item(name))
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

        return self._build_lookup_result(items, has_missing=has_missing)

    def get_agent_bundle(
        self,
        full: bool = False,
        with_code: bool = False,
    ) -> OperationResult[AgentBundleSection]:
        """Build an AI-oriented documentation bundle."""
        api_index = self.list_apis()
        code_index = self.list_code_files()
        api_data = logic.get_api_data_map()

        sections = [
            AgentBundleSection(
                title="Overview",
                content=self._build_agent_overview(
                    api_count=len(api_index.items),
                    module_count=len(code_index.items),
                    full=full,
                    with_code=with_code,
                ),
            ),
            AgentBundleSection(
                title="CLI Workflow",
                content=self._build_agent_cli_workflow(),
            ),
            AgentBundleSection(
                title="Operational Conventions",
                content=self._build_agent_operational_conventions(),
            ),
            AgentBundleSection(
                title="CLI TL;DR",
                content=_AGENT_TLDR_TEXT,
            ),
            AgentBundleSection(
                title="Documentation Navigation",
                content=self._build_agent_doc_navigation(),
            ),
            AgentBundleSection(
                title="Key Source Entry Points",
                content=self._build_agent_key_entry_points(),
            ),
            AgentBundleSection(
                title="API Index",
                content=self._strip_top_heading(render_api_index_text(api_index)),
            ),
            AgentBundleSection(
                title="Source Code Index",
                content=self._strip_top_heading(render_code_index_text(code_index)),
            ),
        ]

        if full:
            sections.extend(
                (
                    AgentBundleSection(
                        title="API Signatures and Responses",
                        content=self._build_agent_api_reference(api_data),
                    ),
                    AgentBundleSection(
                        title="TypedDict Appendix",
                        content=self._build_agent_typed_dict_appendix(api_data),
                    ),
                    AgentBundleSection(
                        title="Key Class Definitions",
                        content=self._build_agent_key_class_definitions(),
                    ),
                )
            )

        if with_code:
            sections.append(
                AgentBundleSection(
                    title="Embedded Source Files",
                    content=self._build_agent_embedded_code_section(),
                )
            )

        return OperationResult(ok=True, items=tuple(sections))

    def _get_code_file_item(self, path: str) -> CodeFileItem:
        normalized_path = Path(path).as_posix()
        source_root = logic.get_source_root_path()
        try:
            target = (source_root / normalized_path).resolve()
            target.relative_to(source_root)
        except (ValueError, RuntimeError):
            return self._build_code_file_problem_item(
                normalized_path,
                kind="invalid_input",
                message=f"Invalid file path: {normalized_path}",
            )

        if not target.is_file():
            return self._build_code_file_problem_item(
                normalized_path,
                kind="not_found",
                message=f"File not found: {normalized_path}",
            )

        if target.suffix != ".py":
            return self._build_code_file_problem_item(
                normalized_path,
                kind="invalid_input",
                message=f"Not a Python file: {normalized_path}",
            )

        try:
            content = target.read_text(encoding="utf-8")
        except Exception as exc:
            return self._build_code_file_problem_item(
                normalized_path,
                kind="internal",
                message=f"Failed to read file: {exc}",
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
        try:
            normalized_values = normalize_string_values(
                values,
                invalid_container_message=f"Argument '{field_name}' must be a sequence of strings.",
                empty_message=f"Argument '{field_name}' cannot be empty.",
                invalid_item_message=f"Argument '{field_name}' must contain non-empty strings only.",
            )
        except ValueError as exc:
            return (), self._build_problem(
                kind="invalid_input",
                message=str(exc),
                target=field_name,
            )

        return normalized_values, ()

    def _build_problem(
        self,
        *,
        kind: ProblemKind,
        message: str,
        target: str | None,
    ) -> tuple[DocProblem, ...]:
        return (DocProblem(kind=kind, message=message, target=target),)

    def _build_lookup_result[T](
        self,
        items: Sequence[T],
        *,
        has_missing: bool,
    ) -> OperationResult[T]:
        return OperationResult(ok=not has_missing, items=tuple(items))

    def _build_missing_api_detail_item(self, name: str) -> ApiDetailItem:
        return ApiDetailItem(
            name=name,
            found=False,
            signature=None,
            description=None,
            response_type=None,
            problems=self._build_problem(
                kind="not_found",
                message=f"API not found: {name}",
                target=name,
            ),
        )

    def _build_missing_class_definition_item(self, name: str) -> ClassDefinitionItem:
        return ClassDefinitionItem(
            name=name,
            found=False,
            sources=(),
            problems=self._build_problem(
                kind="not_found",
                message=f"Class not found: {name}",
                target=name,
            ),
        )

    def _build_code_file_problem_item(
        self,
        path: str,
        *,
        kind: ProblemKind,
        message: str,
    ) -> CodeFileItem:
        return CodeFileItem(
            path=path,
            found=False,
            content=None,
            problems=self._build_problem(
                kind=kind,
                message=message,
                target=path,
            ),
        )

    def _build_agent_overview(
        self,
        *,
        api_count: int,
        module_count: int,
        full: bool,
        with_code: bool,
    ) -> str:
        mode_notes: list[str] = []
        if full:
            mode_notes.append(
                "Full mode expands API signatures, deduplicated TypedDict definitions, and key class definitions."
            )
        else:
            mode_notes.append(
                "Use `napcat-sdk doc agent --full` to expand API signatures, deduplicated TypedDict definitions, and key class definitions."
            )

        if with_code:
            mode_notes.append(
                "Source-embedded mode includes curated implementation files so an agent can inspect real code without extra `doc code` calls."
            )
        else:
            mode_notes.append(
                "Use `napcat-sdk doc agent --with-code` to embed curated implementation files for one-pass code-aware onboarding."
            )
        return dedent(
            f"""
            Primary CLI entrypoints:
            - In a checkout: `uv run napcat-sdk`
            - Installed console script: `napcat-sdk`

            This bundle is intended to bootstrap an AI agent without external docs.
            It summarizes {api_count} API actions and {module_count} Python source files from the SDK.

            {" ".join(mode_notes)}
            """
        ).strip()

    def _build_agent_cli_workflow(self) -> str:
        return dedent(
            """
            Recommended lifecycle:
            1. Create or inspect an instance with `napcat-sdk config <NAME> --ws <URL>` or `napcat-sdk config <NAME>`.
            2. Start it with `napcat-sdk start <NAME>` and verify state with `napcat-sdk list` or `napcat-sdk log <NAME> -f`.
            3. Discover API actions with `napcat-sdk doc apis`, inspect one action with `napcat-sdk doc api <ACTION>`, then invoke it with `napcat-sdk call <NAME> <ACTION> [JSON]`.
            4. Manage outbound event delivery with `napcat-sdk webhook <NAME> add|list|rm ...`.
            5. Explore implementation details with `napcat-sdk doc files`, `napcat-sdk doc code <PATH>`, and `napcat-sdk doc class <NAME>`.
            """
        ).strip()

    def _build_agent_operational_conventions(self) -> str:
        return dedent(
            f"""
            - Instance state lives under `{InstanceConfig.BASE_DIR}`.
            - Real instance configs are stored in `{InstanceConfig.BASE_DIR}/<NAME>/config.toml`.
            - Runtime files include `gateway.pid`, `gateway.sock`, and `gateway.log` inside the instance directory.
            - `call` requires an existing, running instance.
            - `webhook --event TYPE` accepts `message`, `notice`, `request`, `meta`, or `*` for all events.
            - `meta` maps to OneBot `post_type=meta_event`.
            """
        ).strip()

    def _build_agent_doc_navigation(self) -> str:
        return dedent(
            """
            Core documentation commands:
            - `napcat-sdk doc apis`: list all available OneBot actions exposed by the SDK.
            - `napcat-sdk doc api <ACTION>`: show signature, response type, and referenced TypedDicts for one or more actions.
            - `napcat-sdk doc files`: show the Python source tree with module summaries.
            - `napcat-sdk doc code <PATH>`: print a Python source file by relative path.
            - `napcat-sdk doc class <NAME>`: show class definitions by class name.
            - `napcat-sdk mcp doc`: start an MCP server exposing the same docs over stdio.
            """
        ).strip()

    def _build_agent_key_entry_points(self) -> str:
        return dedent(
            """
            High-signal files and why they matter:
            - `client.py`: primary async client implementation (`NapCatClient`).
            - `client_api.py`: generated API mixin methods and docstrings for every action.
            - `types/schemas.py`: request/response TypedDicts and event payload schemas.
            - `cli/__init__.py`: argparse definitions, help text, and command dispatch.
            - `cli/commands/*.py`: imperative behavior for each CLI subcommand.
            - `cli/gateway/*.py`: local gateway protocol, daemon, RPC bridge, and webhook dispatch.
            """
        ).strip()

    def _build_agent_api_reference(self, api_data: dict[str, logic.ApiDoc]) -> str:
        blocks: list[str] = []
        for name, info in api_data.items():
            lines = [f"## {name}", "```python", info["sig"], "```", "", info["description"]]
            if info["response_type"]:
                lines.extend(("", "### Response Type", "", "```python", info["response_type"], "```"))
            blocks.append("\n".join(lines).strip())
        return "\n\n---\n\n".join(blocks)

    def _build_agent_typed_dict_appendix(self, api_data: dict[str, logic.ApiDoc]) -> str:
        typed_dicts: dict[str, str] = {}
        fallback_index = 1
        for info in api_data.values():
            for code in info["typed_dict_codes"]:
                match = _TYPED_DICT_NAME_RE.search(code)
                if match is not None:
                    typed_dicts.setdefault(match.group(1), code)
                    continue

                key = f"TypedDict{fallback_index}"
                fallback_index += 1
                typed_dicts.setdefault(key, code)

        lines = [
            f"Deduplicated TypedDict definitions referenced by the API surface: {len(typed_dicts)} total.",
        ]
        for name in sorted(typed_dicts):
            lines.extend(("", f"## {name}", "", "```python", typed_dicts[name], "```"))
        return "\n".join(lines).strip()

    def _build_agent_key_class_definitions(self) -> str:
        class_result = self.get_class_definitions(
            ["NapCatClient", "InstanceConfig", "WebhookDispatcher"]
        )
        return render_class_definitions_text(class_result)

    def _build_agent_embedded_code_section(self) -> str:
        code_result = self.get_code_files(_AGENT_EMBEDDED_CODE_PATHS)
        lines = [
            "Curated high-signal source files embedded for agents that want concrete implementation context in a single response.",
            "Use `napcat-sdk doc code <PATH>` for additional files beyond this curated set.",
        ]
        for item in code_result.items:
            if not item.found or item.content is None:
                problem_text = item.problems[0].message if item.problems else "Unknown error"
                lines.extend(("", f"### {item.path}", "", f"(Unavailable: {problem_text})"))
                continue

            lines.extend(("", f"### {item.path}", "", "```python", item.content, "```"))

        return "\n".join(lines).strip()

    def _strip_top_heading(self, text: str) -> str:
        lines = text.splitlines()
        if lines and lines[0].startswith("# "):
            lines = lines[1:]
            if lines and not lines[0].strip():
                lines = lines[1:]
        return "\n".join(lines).strip()
