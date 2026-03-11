"""
schema_codegen.py

一个“单文件”的代码生成/重构版本（由原多模块项目合并而来）。

它会读取两份输入源码文件（通常由 napcat / onebot 相关接口定义生成）：
- api_typedict.py   : TypedDict/TypeAlias 形式的 schema 定义
- api_dataclass.py  : dataclass 形式的消息段定义（OB11Message*）

然后输出两份生成文件：
- src/napcat/types/messages/generated.py  : 展平后的 MessageSegment dataclass
- src/napcat/types/schemas.py             : 清理/合并后的 TypedDict schema + generated imports

特性：
- 单文件：便于复制、审核、分发
- 更清晰的代码组织：按 “配置/IO/解析/变换/组装/流水线” 分区
- 更漂亮的日志输出：带层级、时间戳、可选颜色
- 保持与原项目一致的核心逻辑与生成结果（在依赖一致的前提下）

运行方式示例：
    python schema_codegen.py \
        --typedict api_typedict.py \
        --dataclass api_dataclass.py \
        --out-generated src/napcat/types/messages/generated.py \
        --out-schemas src/napcat/types/schemas.py

也可以在代码中直接调用：
    from schema_codegen import CodegenConfig, run_pipeline
    run_pipeline(CodegenConfig(...))

依赖：
- libcst
- （可选）ruff + uv（用于自动格式化生成文件）
"""

from __future__ import annotations

import ast
import logging
import os
import re
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast

try:
    import libcst as cst
    import libcst.matchers as m
except ModuleNotFoundError as e:  # pragma: no cover
    raise ModuleNotFoundError(
        "本脚本依赖 `libcst`。请先安装：pip install libcst"
    ) from e


__all__ = [
    "CodegenConfig",
    "run_pipeline",
]


# ============================================================================
# Logging
# ============================================================================

_LEVEL_TO_COLOR = {
    "DEBUG": "\x1b[38;5;246m",  # grey
    "INFO": "\x1b[38;5;39m",  # blue
    "WARNING": "\x1b[38;5;214m",  # orange
    "ERROR": "\x1b[38;5;196m",  # red
    "CRITICAL": "\x1b[48;5;196m\x1b[38;5;15m",  # red bg + white fg
}
_RESET = "\x1b[0m"


def _stream_supports_color(stream: object) -> bool:
    """Best-effort: detect whether ANSI color is likely supported."""
    if os.getenv("NO_COLOR"):
        return False
    if os.getenv("TERM") in {None, "", "dumb"}:
        return False
    isatty = getattr(stream, "isatty", None)
    return bool(isatty and isatty())


class _PrettyFormatter(logging.Formatter):
    """A compact, readable formatter with optional ANSI colors."""

    def __init__(self, use_color: bool) -> None:
        super().__init__(datefmt="%H:%M:%S")
        self._use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        # Timestamp
        ts = self.formatTime(record, self.datefmt)

        # Level
        level = record.levelname
        if self._use_color:
            color = _LEVEL_TO_COLOR.get(level, "")
            level_disp = f"{color}{level:<8}{_RESET}"
        else:
            level_disp = f"{level:<8}"

        # Message
        msg = record.getMessage()

        # Optional: add exception info
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            msg = f"{msg}\n{exc_text}"

        return f"{ts} | {level_disp} | {msg}"


def configure_logging(*, verbose: bool = False) -> None:
    """
    Configure root logging once.

    If the host application already configured logging handlers, we will not
    override them (to be a good citizen when imported as a library).
    """
    root = logging.getLogger()
    if root.handlers:
        # Respect existing configuration.
        return

    level = logging.DEBUG if verbose else logging.INFO
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setLevel(level)

    use_color = _stream_supports_color(sys.stderr)
    handler.setFormatter(_PrettyFormatter(use_color=use_color))

    root.setLevel(level)
    root.addHandler(handler)


logger = logging.getLogger("schema_codegen")


# ============================================================================
# Config model
# ============================================================================


@dataclass(frozen=True)
class CodegenConfig:
    """
    代码生成配置。

    你可以直接修改默认值，也可以在 run_pipeline() 传入自定义 config。
    """

    typedict_input_path: str = "api_typedict.py"
    dataclass_input_path: str = "api_dataclass.py"

    generated_output_path: str = "src/napcat/types/messages/generated.py"
    schemas_output_path: str = "src/napcat/types/schemas.py"
    messages_init_output_path: str = "src/napcat/types/messages/__init__.py"
    events_init_output_path: str = "src/napcat/types/events/__init__.py"
    types_init_output_path: str = "src/napcat/types/__init__.py"
    client_api_output_path: str = "src/napcat/client_api.py"
    matcher_stub_output_path: str = "src/napcat/matcher.pyi"
    openapi_input_path: str = "NapCatQQ/packages/napcat-schema/dist/openapi.json"
    client_api_codegen_script_path: str = "scripts/client-api-codegen.py"
    matcher_stub_codegen_script_path: str = "scripts/matcher-stub-codegen.py"
    update_init_script_path: str = "scripts/update-init.py"
    run_client_api_codegen_after_pipeline: bool = True
    run_matcher_stub_codegen_after_pipeline: bool = True
    run_update_init_after_pipeline: bool = True

    # 是否在主流程前先构建 openapi.json
    run_openapi_codegen_before_pipeline: bool = True

    # openapi 预生成命令（默认对应 NapCatQQ/package.json 的 build:openapi）
    openapi_codegen_runner: tuple[str, ...] = ("pnpm", "run", "build:openapi")
    openapi_codegen_cwd: str = "NapCatQQ"

    # 是否在主流程前先调用 datamodel-codegen 生成输入文件
    run_datamodel_codegen_before_pipeline: bool = True

    # datamodel-codegen 调用命令（默认使用 `uv run datamodel-codegen`）
    datamodel_codegen_runner: tuple[str, ...] = ("uv", "run", "datamodel-codegen")

    # 预生成使用的 profiles（按顺序执行）
    datamodel_codegen_profiles: tuple[str, ...] = ("api-typedict", "api-dataclass")

    # 主流程结束后是否清理预生成输入文件（api_typedict.py / api_dataclass.py）
    cleanup_codegen_inputs_after_pipeline: bool = True

    # 是否在最后调用 Ruff 自动修复 + 格式化
    format_with_ruff: bool = True

    # Ruff 调用命令（默认使用 `uv run ruff`，与原项目保持一致）
    ruff_runner: tuple[str, ...] = ("uv", "run", "ruff")

    # Ruff 失败时是否忽略（默认 False：保持原项目行为——失败即中断）
    ignore_ruff_errors: bool = False


# ============================================================================
# IO helpers
# ============================================================================


def read_text(path: str | os.PathLike[str]) -> str:
    """Read a UTF-8 text file."""
    return Path(path).read_text(encoding="utf-8")


def write_text(path: str | os.PathLike[str], content: str) -> None:
    """Write a UTF-8 text file, ensuring parent directory exists."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def _apply_generated_name_rules(name: str) -> str:
    """
    Apply renaming rules for generated artifacts.

    Special-case datamodel-codegen full-path names for message node unions so
    the public API stays semantic after upstream switched `OB11MessageNode`
    from a single object to a union.

    - OB11MessageData -> Message
    - OB11Message*    -> remove prefix
    """
    special_cases = {
        "OB11MessageNodeOB11MessageNode": "NodeReference",
        "OB11MessageNodeOB11MessageNode1": "NodeInline",
        "OB11MessageNodeOB11MessageNode1DataNew": "NodeInlineDataNew",
    }
    if name in special_cases:
        return special_cases[name]

    replaced = name.replace("OB11MessageData", "Message")
    replaced = replaced.replace("OB11Message", "")
    return replaced


def _collect_top_level_definition_names(source: str) -> set[str]:
    """Collect class names and TypeAlias names from a python module source."""
    module = cst.parse_module(source)
    names: set[str] = set()

    for stmt in module.body:
        if isinstance(stmt, cst.ClassDef):
            names.add(stmt.name.value)
            continue

        if isinstance(stmt, cst.SimpleStatementLine):
            for small_stmt in stmt.body:
                if isinstance(small_stmt, cst.TypeAlias):
                    names.add(small_stmt.name.value)

    return names


def _replace_identifier_names(
    source: str, rename_map: dict[str, str]
) -> tuple[str, set[str]]:
    """
    Replace identifiers using a conservative word-boundary regex.

    Returns:
        (replaced_source, applied_old_names)
    """
    replaced = source
    applied_names: set[str] = set()

    # Replace longer names first to avoid partial overlaps.
    for old_name in sorted(rename_map, key=len, reverse=True):
        new_name = rename_map[old_name]
        pattern = re.compile(rf"\b{re.escape(old_name)}\b")
        replaced, count = pattern.subn(new_name, replaced)
        if count > 0:
            applied_names.add(old_name)

    return replaced, applied_names


def _expr_to_dotted_name(expr: cst.BaseExpression) -> str | None:
    """Convert Name/Attribute chain into dotted string (best-effort)."""
    if isinstance(expr, cst.Name):
        return expr.value
    if isinstance(expr, cst.Attribute):
        left = _expr_to_dotted_name(expr.value)
        if left is None:
            return None
        return f"{left}.{expr.attr.value}"
    return None


def _collect_generated_import_names(source: str) -> set[str]:
    """
    Collect names imported from `.messages.generated`.

    This is used by `postprocess_schemas_file()` to rename imported symbols
    consistently with generated.py renames.
    """
    module = cst.parse_module(source)
    imported_names: set[str] = set()

    for stmt in module.body:
        if not isinstance(stmt, cst.SimpleStatementLine):
            continue

        for small_stmt in stmt.body:
            if not isinstance(small_stmt, cst.ImportFrom):
                continue

            module_expr = small_stmt.module
            if module_expr is None:
                continue

            module_name = _expr_to_dotted_name(module_expr)
            if module_name is None:
                continue

            full_module_name = "." * len(small_stmt.relative) + module_name
            if full_module_name != ".messages.generated":
                continue

            if isinstance(small_stmt.names, cst.ImportStar):
                continue

            for alias in small_stmt.names:
                if isinstance(alias.name, cst.Name):
                    imported_names.add(alias.name.value)

    return imported_names


def _module_uses_typeddict(module: cst.Module) -> bool:
    """Whether the module defines any TypedDict classes."""
    for stmt in module.body:
        if not isinstance(stmt, cst.ClassDef):
            continue
        if any(get_base_class_name(base) == "TypedDict" for base in stmt.bases):
            return True
    return False


def _is_future_import_statement(stmt: cst.BaseStatement) -> bool:
    """Whether a statement line is `from __future__ import ...`."""
    if not isinstance(stmt, cst.SimpleStatementLine):
        return False
    return any(
        isinstance(small_stmt, cst.ImportFrom)
        and _expr_to_dotted_name(small_stmt.module) == "__future__"
        for small_stmt in stmt.body
    )


class TypedDictCompatibilityTransformer(cst.CSTTransformer):
    """Drop typing-extensions-only TypedDict class keywords from generated output."""

    def __init__(self) -> None:
        self.removed_keyword_count = 0

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.ClassDef:
        if not any(
            get_base_class_name(base) == "TypedDict" for base in original_node.bases
        ):
            return updated_node

        kept_keywords: list[cst.Arg] = []
        removed = False
        for keyword in updated_node.keywords:
            if keyword.keyword is not None and keyword.keyword.value in {
                "closed",
                "extra_items",
            }:
                self.removed_keyword_count += 1
                removed = True
                continue
            kept_keywords.append(keyword)

        if not removed:
            return updated_node

        return updated_node.with_changes(keywords=tuple(kept_keywords))


def postprocess_typeddict_imports(path: str | os.PathLike[str]) -> None:
    """
    Normalize TypedDict usage in generated artifacts.

    We intentionally drop typing-extensions-only class keywords like
    `closed=True` so the final generated artifacts can use stdlib
    `typing.TypedDict` on Python 3.12+.
    """
    path = str(path)
    source = read_text(path)
    parsed_module = cst.parse_module(source)
    compatibility_transformer = TypedDictCompatibilityTransformer()
    module = parsed_module.visit(compatibility_transformer)

    uses_typeddict = _module_uses_typeddict(module)
    has_typing_typedict = False
    changed = compatibility_transformer.removed_keyword_count > 0
    new_body: list[cst.BaseStatement] = []

    for stmt in module.body:
        if not isinstance(stmt, cst.SimpleStatementLine):
            new_body.append(stmt)
            continue

        new_small_stmts: list[cst.BaseSmallStatement] = []
        for small_stmt in stmt.body:
            if not isinstance(small_stmt, cst.ImportFrom):
                new_small_stmts.append(small_stmt)
                continue

            module_expr = small_stmt.module
            if module_expr is None:
                new_small_stmts.append(small_stmt)
                continue

            module_name = _expr_to_dotted_name(module_expr)
            if module_name == "typing_extensions":
                if isinstance(small_stmt.names, cst.ImportStar):
                    new_small_stmts.append(small_stmt)
                    continue

                kept_aliases = [
                    alias
                    for alias in small_stmt.names
                    if not (
                        isinstance(alias.name, cst.Name)
                        and alias.name.value == "TypedDict"
                    )
                ]
                if len(kept_aliases) != len(small_stmt.names):
                    changed = True
                    if kept_aliases:
                        new_small_stmts.append(
                            small_stmt.with_changes(names=tuple(kept_aliases))
                        )
                    continue

                new_small_stmts.append(small_stmt)
                continue

            if module_name != "typing":
                new_small_stmts.append(small_stmt)
                continue

            if isinstance(small_stmt.names, cst.ImportStar):
                has_typing_typedict = True
                new_small_stmts.append(small_stmt)
                continue

            if any(
                isinstance(alias.name, cst.Name) and alias.name.value == "TypedDict"
                for alias in small_stmt.names
            ):
                has_typing_typedict = True
            new_small_stmts.append(small_stmt)

        if not new_small_stmts:
            changed = True
            continue

        if len(new_small_stmts) != len(stmt.body):
            changed = True
        new_body.append(stmt.with_changes(body=tuple(new_small_stmts)))

    if uses_typeddict and not has_typing_typedict:
        insert_index = 0
        for i, stmt in enumerate(new_body):
            if i == 0 and is_docstring_stmt(stmt):
                insert_index = i + 1
                continue
            if _is_future_import_statement(stmt) or is_import_statement(stmt):
                insert_index = i + 1
                continue
            break
        new_body.insert(
            insert_index,
            cst.parse_statement("from typing import TypedDict\n"),
        )
        changed = True

    if not changed:
        return

    normalized_source = cst.Module(body=tuple(new_body)).code
    normalized_source = re.sub(
        r"^(from typing import .+?),\s*$",
        r"\1",
        normalized_source,
        flags=re.MULTILINE,
    )
    write_text(path, normalized_source)
    logger.info("🧹 Normalized TypedDict imports: %s", path)


def postprocess_generated_file(path: str | os.PathLike[str]) -> dict[str, str]:
    """
    Post-process generated.py:
    - apply naming rules (OB11Message* -> *)
    - return a rename map actually applied (used by schemas.py postprocess)
    """
    path = str(path)
    source = read_text(path)

    top_level_names = _collect_top_level_definition_names(source)
    rename_map = {
        name: new_name
        for name in top_level_names
        if (new_name := _apply_generated_name_rules(name)) != name
    }

    replaced, applied_names = _replace_identifier_names(source, rename_map)

    if replaced != source:
        write_text(path, replaced)

    applied_rename_map = {name: rename_map[name] for name in applied_names}
    logger.info(
        "🧹 Post-processed generated file: %s (renamed %d symbols)",
        path,
        len(applied_rename_map),
    )
    return applied_rename_map


def postprocess_schemas_file(
    path: str | os.PathLike[str],
    generated_rename_map: dict[str, str],
) -> None:
    """
    Post-process schemas.py:
    - rename imported generated symbols to match generated.py renames
    """
    path = str(path)
    source = read_text(path)
    imported_names = _collect_generated_import_names(source)

    schemas_rename_map = {
        name: new_name
        for name, new_name in generated_rename_map.items()
        if name in imported_names
    }

    replaced, applied_names = _replace_identifier_names(source, schemas_rename_map)

    if replaced != source:
        write_text(path, replaced)

    logger.info(
        "🧹 Post-processed schemas file: %s (applied %d renames from generated imports)",
        path,
        len(applied_names),
    )


def postprocess_float_to_int_with_location_exceptions(
    path: str | os.PathLike[str],
) -> None:
    """
    Post-process generated code types:
    - globally replace `float` -> `int`
    - then restore `lat` / `lon` field annotations to `str | float`
    """
    path = str(path)
    source = read_text(path)

    replaced = re.sub(r"\bfloat\b", "int", source)

    # Restore location field types.
    replaced = re.sub(
        r"^(\s*lat:\s*)str\s*\|\s*int(\s*(?:=[^\n]*)?)$",
        r"\1str | float\2",
        replaced,
        flags=re.MULTILINE,
    )
    replaced = re.sub(
        r"^(\s*lon:\s*)str\s*\|\s*int(\s*(?:=[^\n]*)?)$",
        r"\1str | float\2",
        replaced,
        flags=re.MULTILINE,
    )

    if replaced != source:
        write_text(path, replaced)
        logger.info("🧹 Post-processed float->int with location exceptions: %s", path)


def format_generated_files_with_ruff(
    paths: Sequence[str | os.PathLike[str]],
    *,
    ruff_runner: Sequence[str] = ("uv", "run", "ruff"),
) -> None:
    """
    Run Ruff to auto-fix & format generated files.

    Notes:
    - Uses subprocess; will raise if command fails.
    - If you don't have uv/ruff, set config.format_with_ruff = False.
    """
    str_paths = [str(p) for p in paths if p]
    if not str_paths:
        return

    # `ruff check --fix`
    subprocess.run([*ruff_runner, "check", "--fix", *str_paths], check=True)
    # `ruff format`
    subprocess.run([*ruff_runner, "format", *str_paths], check=True)

    logger.info("✨ Formatted generated files with Ruff: %s", ", ".join(str_paths))


def _collect_paths_for_ruff_formatting(cfg: CodegenConfig) -> list[str]:
    """Return Ruff targets, keeping optional generated artifacts truly optional."""
    paths = [
        cfg.generated_output_path,
        cfg.schemas_output_path,
        cfg.messages_init_output_path,
        cfg.events_init_output_path,
        cfg.types_init_output_path,
    ]

    optional_paths = [
        (
            cfg.run_client_api_codegen_after_pipeline,
            cfg.client_api_output_path,
        ),
        (
            cfg.run_matcher_stub_codegen_after_pipeline,
            cfg.matcher_stub_output_path,
        ),
    ]
    for was_generated, path in optional_paths:
        if path and (was_generated or Path(path).exists()):
            paths.append(path)

    return paths


def run_datamodel_codegen_profiles(
    profiles: Sequence[str],
    *,
    runner: Sequence[str] = ("uv", "run", "datamodel-codegen"),
) -> None:
    """Run datamodel-codegen for each configured profile."""
    for profile in profiles:
        logger.info("🛠️  Running datamodel-codegen profile: %s", profile)
        subprocess.run([*runner, "--profile", profile], check=True)


def run_openapi_codegen(
    *,
    runner: Sequence[str] = ("pnpm", "run", "build:openapi"),
    cwd: str | os.PathLike[str] = "NapCatQQ",
) -> None:
    """Build OpenAPI artifact (openapi.json) in NapCat workspace."""
    logger.info("🛠️  Running OpenAPI codegen: %s (cwd=%s)", " ".join(runner), cwd)
    subprocess.run([*runner], check=True, cwd=str(cwd))


def run_client_api_codegen(
    *,
    script_path: str | os.PathLike[str],
    openapi_path: str | os.PathLike[str],
    schemas_path: str | os.PathLike[str],
    output_path: str | os.PathLike[str],
) -> None:
    """Generate src/napcat/client_api.py mixin from openapi + schemas.py."""
    script = str(script_path)
    openapi = str(openapi_path)
    schemas = str(schemas_path)
    out = str(output_path)

    logger.info("🛠️  Running client API codegen: %s", script)
    completed = subprocess.run(
        [
            sys.executable,
            script,
            "--openapi",
            openapi,
            "--schemas",
            schemas,
            "--out",
            out,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    stdout = (completed.stdout or "").strip()
    if stdout:
        for line in stdout.splitlines():
            logger.info("%s", line)

    stderr = (completed.stderr or "").strip()
    if stderr:
        for line in stderr.splitlines():
            logger.warning("[client-api-codegen] %s", line)


def run_update_init_codegen(*, script_path: str | os.PathLike[str]) -> None:
    """Update aggregate __init__.py files from generated notice/messages exports."""
    script = str(script_path)

    logger.info("🛠️  Running update-init: %s", script)
    completed = subprocess.run(
        [sys.executable, script],
        check=True,
        capture_output=True,
        text=True,
    )

    stdout = (completed.stdout or "").strip()
    if stdout:
        for line in stdout.splitlines():
            logger.info("%s", line)

    stderr = (completed.stderr or "").strip()
    if stderr:
        for line in stderr.splitlines():
            logger.warning("[update-init] %s", line)


def run_matcher_stub_codegen(
    *,
    script_path: str | os.PathLike[str],
    output_path: str | os.PathLike[str],
) -> None:
    """Generate src/napcat/matcher.pyi from final event dataclasses."""
    script = str(script_path)
    out = str(output_path)

    logger.info("🛠️  Running matcher stub codegen: %s", script)
    completed = subprocess.run(
        [sys.executable, script, "--out", out],
        check=True,
        capture_output=True,
        text=True,
    )

    stdout = (completed.stdout or "").strip()
    if stdout:
        for line in stdout.splitlines():
            logger.info("%s", line)

    stderr = (completed.stderr or "").strip()
    if stderr:
        for line in stderr.splitlines():
            logger.warning("[matcher-stub-codegen] %s", line)


def cleanup_codegen_input_files(paths: Sequence[str | os.PathLike[str]]) -> list[str]:
    """Delete temporary codegen input files if they exist."""
    removed: list[str] = []
    for path in paths:
        p = Path(path)
        if not p.exists():
            continue
        p.unlink()
        removed.append(str(p))
    return removed


def _arg_base_is_message_segment(base: cst.Arg) -> bool:
    return isinstance(base.value, cst.Name) and base.value.value == "MessageSegment"


def collect_generated_exports_for_messages_init(source: str) -> list[str]:
    """Collect exports for `messages/__init__.py` from generated.py source."""
    module = cst.parse_module(source)
    exports: set[str] = set()

    for stmt in module.body:
        if isinstance(stmt, cst.ClassDef):
            if any(_arg_base_is_message_segment(base) for base in stmt.bases):
                exports.add(stmt.name.value)
            continue

        if isinstance(stmt, cst.SimpleStatementLine):
            for small_stmt in stmt.body:
                if not isinstance(small_stmt, cst.TypeAlias):
                    continue
                if small_stmt.name.value in {"Message", "MessageData", "Model"}:
                    exports.add(small_stmt.name.value)

    return sorted(exports)


def build_messages_init_content(exports: Sequence[str]) -> str:
    """Build `src/napcat/types/messages/__init__.py` content."""
    lines = [
        "from .base import MessageSegment, UnknownMessageSegment",
    ]

    if exports:
        lines.append("from .generated import (")
        lines.extend(f"    {name}," for name in exports)
        lines.append(")")

    lines.append("")
    lines.append("__all__ = [")
    lines.append('    "MessageSegment",')
    lines.append('    "UnknownMessageSegment",')
    lines.extend(f'    "{name}",' for name in exports)
    lines.append("]")
    lines.append("")
    return "\n".join(lines)


def write_messages_init_file(
    path: str | os.PathLike[str],
    generated_source: str,
) -> list[str]:
    """Generate and write `messages/__init__.py` from generated.py content."""
    exports = collect_generated_exports_for_messages_init(generated_source)
    content = build_messages_init_content(exports)
    write_text(path, content)
    logger.info(
        "✅ Wrote messages __init__ to: %s (exports %d symbols)", path, len(exports)
    )
    return exports


# ============================================================================
# CST Visitors (Collectors)
# ============================================================================


class ClassCollector(cst.CSTVisitor):
    """Collect all ClassDef nodes by name."""

    def __init__(self) -> None:
        self.definitions: dict[str, cst.ClassDef] = {}

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        self.definitions[node.name.value] = node


class NameCollector(cst.CSTVisitor):
    """Collect all Name nodes in a subtree."""

    def __init__(self) -> None:
        self.names: set[str] = set()

    def visit_Name(self, node: cst.Name) -> None:
        self.names.add(node.value)


# ============================================================================
# Predicates (small helpers)
# ============================================================================


def is_docstring_stmt(stmt: cst.BaseStatement) -> bool:
    """Whether a statement looks like a docstring expression statement."""
    return m.matches(
        stmt,
        m.SimpleStatementLine(
            body=[m.Expr(value=m.SimpleString() | m.ConcatenatedString())]
        ),
    )


def is_dataclass_class(class_node: cst.ClassDef) -> bool:
    """Detect `@dataclass` decorator (both bare and call form)."""
    for decorator in class_node.decorators:
        d = decorator.decorator
        if isinstance(d, cst.Name) and d.value == "dataclass":
            return True
        if (
            isinstance(d, cst.Call)
            and isinstance(d.func, cst.Name)
            and d.func.value == "dataclass"
        ):
            return True
    return False


def is_import_statement(stmt: cst.BaseStatement) -> bool:
    """Whether a statement line contains Import/ImportFrom."""
    if not isinstance(stmt, cst.SimpleStatementLine):
        return False
    for small_stmt in stmt.body:
        if isinstance(small_stmt, cst.Import) or isinstance(small_stmt, cst.ImportFrom):
            return True
    return False


# ============================================================================
# Extractors (read/collect info from CST)
# ============================================================================


def get_field_blocks(
    class_node: cst.ClassDef,
) -> list[tuple[str, cst.AnnAssign, list[cst.BaseStatement]]]:
    """
    Extract annotated field blocks from a class body.

    We treat a field as:
    - a SimpleStatementLine with exactly one AnnAssign, e.g. `x: int = 1`
    - and also attach any following docstring-like statement lines as belonging
      to that field (so generated output keeps field-level docs).
    """
    body = list(class_node.body.body)
    result: list[tuple[str, cst.AnnAssign, list[cst.BaseStatement]]] = []

    i = 0
    while i < len(body):
        stmt = body[i]
        if (
            isinstance(stmt, cst.SimpleStatementLine)
            and len(stmt.body) == 1
            and isinstance(stmt.body[0], cst.AnnAssign)
        ):
            ann_assign = stmt.body[0]
            if not isinstance(ann_assign.target, cst.Name):
                i += 1
                continue

            field_name = ann_assign.target.value
            block: list[cst.BaseStatement] = [stmt]

            j = i + 1
            while j < len(body):
                next_stmt = body[j]
                if isinstance(next_stmt, cst.SimpleStatementLine) and is_docstring_stmt(
                    next_stmt
                ):
                    block.append(next_stmt)
                    j += 1
                    continue
                break

            result.append((field_name, ann_assign, block))
            i = j
            continue

        i += 1

    return result


def extract_literal_string(annotation: cst.BaseExpression) -> str | None:
    """
    Extract Literal["..."] string value from a CST expression.

    Example:
        Literal["text"]  -> "text"
    """
    if not isinstance(annotation, cst.Subscript):
        return None
    if (
        not isinstance(annotation.value, cst.Name)
        or annotation.value.value != "Literal"
    ):
        return None
    if len(annotation.slice) != 1:
        return None

    first_slice = annotation.slice[0]
    if not isinstance(first_slice.slice, cst.Index):
        return None

    literal_expr = first_slice.slice.value
    if isinstance(literal_expr, cst.SimpleString):
        try:
            literal = ast.literal_eval(literal_expr.value)
            if isinstance(literal, str):
                return literal
        except Exception:
            return None
    return None


def get_base_class_name(base: cst.Arg) -> str | None:
    """Get base class name if it's a simple `Name`."""
    if isinstance(base.value, cst.Name):
        return base.value.value
    return None


def collect_names_from_expr(expr: cst.BaseExpression) -> set[str]:
    """Collect Name identifiers appearing in an expression subtree."""
    visitor = NameCollector()
    expr.visit(visitor)
    return visitor.names


def collect_annotation_names_from_class(class_node: cst.ClassDef) -> set[str]:
    """Collect all identifier names used in field annotations of a class."""
    names: set[str] = set()
    for _, ann_assign, _ in get_field_blocks(class_node):
        names.update(collect_names_from_expr(ann_assign.annotation.annotation))
    return names


def collect_typedict_helper_classes(
    message_classes: Sequence[cst.ClassDef],
    typedict_module: cst.Module,
    typedict_definitions: dict[str, cst.ClassDef],
    *,
    extra_root_names: Sequence[str] = (),
) -> list[cst.ClassDef]:
    """
    Collect helper TypedDict classes referenced by generated message classes.

    We do a BFS over annotation names so we can include dependency TypedDicts
    that the message segment classes reference.
    """
    message_class_names = {cls.name.value for cls in message_classes}

    helper_names: set[str] = set()
    queue: list[str] = []

    for cls in message_classes:
        for name in collect_annotation_names_from_class(cls):
            if name not in message_class_names:
                queue.append(name)
    for name in extra_root_names:
        if name not in message_class_names:
            queue.append(name)

    while queue:
        current = queue.pop()
        if current in helper_names or current in message_class_names:
            continue

        helper_cls = typedict_definitions.get(current)
        if not helper_cls:
            continue

        helper_names.add(current)
        for dep_name in collect_annotation_names_from_class(helper_cls):
            if dep_name not in helper_names and dep_name not in message_class_names:
                queue.append(dep_name)

    # Keep original ordering in the typedict module.
    ordered_helpers: list[cst.ClassDef] = []
    for stmt in typedict_module.body:
        if isinstance(stmt, cst.ClassDef) and stmt.name.value in helper_names:
            ordered_helpers.append(stmt)

    return ordered_helpers


def collect_top_level_definition_names(module: cst.Module) -> set[str]:
    """Collect class names and TypeAlias names from a CST module."""
    names: set[str] = set()
    for stmt in module.body:
        if isinstance(stmt, cst.ClassDef):
            names.add(stmt.name.value)
            continue

        if isinstance(stmt, cst.SimpleStatementLine):
            for small_stmt in stmt.body:
                if isinstance(small_stmt, cst.TypeAlias):
                    names.add(small_stmt.name.value)
    return names


def collect_annotation_names_from_module(module: cst.Module) -> set[str]:
    """Collect all identifier names referenced by class field annotations and TypeAlias values."""
    names: set[str] = set()
    for stmt in module.body:
        if isinstance(stmt, cst.ClassDef):
            names.update(collect_annotation_names_from_class(stmt))
            continue

        if isinstance(stmt, cst.SimpleStatementLine):
            for small_stmt in stmt.body:
                if isinstance(small_stmt, cst.TypeAlias):
                    names.update(collect_names_from_expr(small_stmt.value))
    return names


def collect_definition_annotation_names(module: cst.Module) -> dict[str, set[str]]:
    """Collect annotation/reference names for each top-level definition."""
    result: dict[str, set[str]] = {}
    for stmt in module.body:
        if isinstance(stmt, cst.ClassDef):
            result[stmt.name.value] = collect_annotation_names_from_class(stmt)
            continue

        if isinstance(stmt, cst.SimpleStatementLine):
            for small_stmt in stmt.body:
                if isinstance(small_stmt, cst.TypeAlias):
                    result[small_stmt.name.value] = collect_names_from_expr(
                        small_stmt.value
                    )
    return result


def collect_selected_type_alias_blocks(
    module: cst.Module,
    target_alias_names: set[str],
) -> list[cst.SimpleStatementLine]:
    """
    Collect TypeAlias statements by name, including alias-to-alias dependencies.

    Returned statements keep original order and include following docstrings.
    """
    body = list(module.body)
    alias_dependencies: dict[str, set[str]] = {}
    alias_names: set[str] = set()

    for stmt in body:
        if not isinstance(stmt, cst.SimpleStatementLine):
            continue
        for small_stmt in stmt.body:
            if not isinstance(small_stmt, cst.TypeAlias):
                continue
            alias_names.add(small_stmt.name.value)
            alias_dependencies[small_stmt.name.value] = collect_names_from_expr(
                small_stmt.value
            )

    selected_alias_names: set[str] = set()
    queue = list(target_alias_names)
    while queue:
        current = queue.pop()
        if current in selected_alias_names or current not in alias_names:
            continue
        selected_alias_names.add(current)
        for dep_name in alias_dependencies.get(current, set()):
            if dep_name in alias_names and dep_name not in selected_alias_names:
                queue.append(dep_name)

    collected: list[cst.SimpleStatementLine] = []

    i = 0
    while i < len(body):
        stmt = body[i]
        matched_alias = False
        matched_stmt: cst.SimpleStatementLine | None = None

        if isinstance(stmt, cst.SimpleStatementLine):
            matched_stmt = stmt
            for small_stmt in stmt.body:
                if (
                    isinstance(small_stmt, cst.TypeAlias)
                    and small_stmt.name.value in selected_alias_names
                ):
                    matched_alias = True
                    break

        if not matched_alias:
            i += 1
            continue

        if matched_stmt is not None:
            collected.append(matched_stmt)
        i += 1
        while i < len(body):
            next_stmt = body[i]
            if not isinstance(next_stmt, cst.SimpleStatementLine):
                break
            if not is_docstring_stmt(next_stmt):
                break

            collected.append(next_stmt)
            i += 1

    return collected


def collect_names_from_type_alias_blocks(
    alias_blocks: Sequence[cst.SimpleStatementLine],
) -> set[str]:
    """Collect referenced names from TypeAlias statements."""
    names: set[str] = set()
    for stmt in alias_blocks:
        for small_stmt in stmt.body:
            if isinstance(small_stmt, cst.TypeAlias):
                names.update(collect_names_from_expr(small_stmt.value))
    return names


# ============================================================================
# TypedDict transforms
# ============================================================================


class ResponseFlattener(cst.CSTTransformer):
    """
    Flatten `*PostResponse` TypedDict classes.

    - If `data: DataXXX` refers to a TypedDict class named `DataXXX`, we inline
      its body into the PostResponse class and record that DataXXX was flattened.
    - Otherwise, we convert the PostResponse class to a `TypeAlias` pointing to
      the annotation of `data`.
    """

    def __init__(self, definitions: dict[str, cst.ClassDef]):
        self.definitions = definitions
        self.flattened_classes: list[str] = []

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> (
        cst.BaseStatement | cst.FlattenSentinel[cst.BaseStatement] | cst.RemovalSentinel
    ):
        if not original_node.name.value.endswith("PostResponse"):
            return updated_node

        data_annotation: cst.BaseExpression | None = None
        data_field_pattern = m.SimpleStatementLine(
            body=[m.AnnAssign(target=m.Name("data"))]
        )

        for stmt in original_node.body.body:
            if m.matches(stmt, data_field_pattern):
                simple_stmt = cast(cst.SimpleStatementLine, stmt)
                ann_assign = cast(cst.AnnAssign, simple_stmt.body[0])
                data_annotation = ann_assign.annotation.annotation
                break

        if not data_annotation:
            return updated_node

        # Case 1: inline referenced DataXXX TypedDict
        if (
            isinstance(data_annotation, cst.Name)
            and data_annotation.value in self.definitions
            and data_annotation.value.startswith("Data")
        ):
            ref_class_name = data_annotation.value
            ref_class_node = self.definitions[ref_class_name]

            new_body_list: list[cst.BaseStatement] = []

            # Keep docstring of PostResponse
            if original_node.body.body and is_docstring_stmt(
                cast(cst.BaseStatement, original_node.body.body[0])
            ):
                doc_stmt = cast(cst.BaseStatement, original_node.body.body[0])
                new_body_list.append(doc_stmt)

            # Inline body of DataXXX (strip its own docstring if present)
            source_stmts = cast(Sequence[cst.BaseStatement], ref_class_node.body.body)
            ref_body_stmts = list(source_stmts)
            if ref_body_stmts and is_docstring_stmt(ref_body_stmts[0]):
                ref_body_stmts.pop(0)

            new_body_list.extend(ref_body_stmts)
            self.flattened_classes.append(ref_class_name)

            return updated_node.with_changes(
                bases=[cst.Arg(value=cst.Name("TypedDict"))],
                body=cst.IndentedBlock(body=new_body_list),
            )

        # Case 2: convert class to type alias
        type_alias_node = cst.TypeAlias(name=original_node.name, value=data_annotation)
        return cst.SimpleStatementLine(
            body=[type_alias_node],
            leading_lines=original_node.leading_lines,
        )


class FlattenedClassRemover(cst.CSTTransformer):
    """Remove flattened DataXXX class definitions from TypedDict module."""

    def __init__(self, flattened_classes: Sequence[str]):
        self.flattened_class_set = set(flattened_classes)
        self.removed_count = 0

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> (
        cst.BaseStatement | cst.FlattenSentinel[cst.BaseStatement] | cst.RemovalSentinel
    ):
        if original_node.name.value in self.flattened_class_set:
            self.removed_count += 1
            return cst.RemoveFromParent()
        return updated_node


def get_top_level_definition_name(stmt: cst.BaseStatement) -> str | None:
    """Get the top-level class or type-alias name for a statement."""
    if isinstance(stmt, cst.ClassDef):
        return stmt.name.value

    if isinstance(stmt, cst.SimpleStatementLine):
        for small_stmt in stmt.body:
            if isinstance(small_stmt, cst.TypeAlias):
                return small_stmt.name.value

    return None


def remove_named_definitions_with_docstrings(
    module: cst.Module,
    names_to_remove: set[str],
) -> cst.Module:
    """Remove top-level definitions and any following standalone docstrings."""
    kept_body: list[cst.BaseStatement] = []
    body = list(module.body)
    i = 0

    while i < len(body):
        stmt = cast(cst.BaseStatement, body[i])
        definition_name = get_top_level_definition_name(stmt)
        if definition_name is None or definition_name not in names_to_remove:
            kept_body.append(stmt)
            i += 1
            continue

        i += 1
        while i < len(body) and is_docstring_stmt(cast(cst.BaseStatement, body[i])):
            i += 1

    return module.with_changes(body=tuple(kept_body))


# ============================================================================
# Message (dataclass) transforms
# ============================================================================


def collect_dataclass_fields_with_inheritance(
    class_name: str,
    definitions: dict[str, cst.ClassDef],
    visiting: set[str] | None = None,
) -> list[tuple[str, list[cst.BaseStatement]]]:
    """
    Collect field blocks from dataclass class, including inherited bases.

    - Preserve field order (base fields first, then child override).
    - Protect against circular inheritance via `visiting` set.
    """
    if visiting is None:
        visiting = set()
    if class_name in visiting:
        return []

    class_node = definitions.get(class_name)
    if not class_node or not is_dataclass_class(class_node):
        return []

    visiting.add(class_name)

    field_order: list[str] = []
    field_blocks: dict[str, list[cst.BaseStatement]] = {}

    def upsert_field(name: str, block: list[cst.BaseStatement]) -> None:
        if name not in field_blocks:
            field_order.append(name)
        field_blocks[name] = block

    # Bases first
    for base in class_node.bases:
        base_name = get_base_class_name(base)
        if not base_name:
            continue
        for fname, fblock in collect_dataclass_fields_with_inheritance(
            base_name, definitions, visiting
        ):
            upsert_field(fname, fblock)

    # Then this class
    for fname, _, fblock in get_field_blocks(class_node):
        upsert_field(fname, fblock)

    visiting.remove(class_name)
    return [(fname, field_blocks[fname]) for fname in field_order]


def collect_dataclass_class_names_with_inheritance(
    class_name: str,
    definitions: dict[str, cst.ClassDef],
    visiting: set[str] | None = None,
) -> set[str]:
    """Collect class names in the dataclass inheritance chain."""
    if visiting is None:
        visiting = set()
    if class_name in visiting:
        return set()

    class_node = definitions.get(class_name)
    if not class_node or not is_dataclass_class(class_node):
        return set()

    visiting.add(class_name)

    collected: set[str] = {class_name}
    for base in class_node.bases:
        base_name = get_base_class_name(base)
        if not base_name:
            continue
        collected.update(
            collect_dataclass_class_names_with_inheritance(
                base_name, definitions, visiting
            )
        )

    visiting.remove(class_name)
    return collected


def transform_message_segment_class(
    class_node: cst.ClassDef,
    definitions: dict[str, cst.ClassDef],
    flattened_dataclass_names: set[str] | None = None,
) -> cst.ClassDef | None:
    """
    Transform OB11Message* dataclass to MessageSegment subclass.

    Rules:
    - Must have `type: Literal["xxx"]`
    - Convert to:
        class Xxx(MessageSegment):
            _type: ClassVar[str] = "xxx"
            ...fields...

    Special handling:
    - If it has `data: SomeDataClass`, inline all fields from that dataclass
      (including bases) into the message segment, and record flattened names.
    """
    field_blocks = get_field_blocks(class_node)
    field_map = {name: (ann, block) for name, ann, block in field_blocks}

    type_field = field_map.get("type")
    if not type_field:
        return None

    type_ann, _ = type_field
    type_literal = extract_literal_string(type_ann.annotation.annotation)
    if type_literal is None:
        return None

    new_body: list[cst.BaseStatement] = []

    # Keep original class-level docstring, if present
    original_body = list(class_node.body.body)
    if original_body and is_docstring_stmt(cast(cst.BaseStatement, original_body[0])):
        new_body.append(cast(cst.BaseStatement, original_body[0]))

    # Inject `_type: ClassVar[str] = "..."`
    type_stmt = cst.parse_statement(f'_type: ClassVar[str] = "{type_literal}"\n')
    new_body.append(type_stmt)

    # Inline `data: SomeDataClass`
    data_field = field_map.get("data")
    if data_field:
        data_ann, _ = data_field
        data_annotation = data_ann.annotation.annotation
        if isinstance(data_annotation, cst.Name):
            if flattened_dataclass_names is not None:
                flattened_dataclass_names.update(
                    collect_dataclass_class_names_with_inheritance(
                        data_annotation.value,
                        definitions,
                    )
                )

            flattened_fields = collect_dataclass_fields_with_inheritance(
                data_annotation.value,
                definitions,
            )
            for _, block in flattened_fields:
                new_body.extend(block)

    # Add remaining fields (excluding "type" & "data")
    for name, _, block in field_blocks:
        if name in {"type", "data"}:
            continue
        new_body.extend(block)

    public_name = _apply_generated_name_rules(class_node.name.value)
    register_kwarg: list[cst.Arg] = []
    if public_name.endswith("CustomMusic") or public_name in {
        "NodeReference",
        "NodeInline",
    }:
        register_kwarg = [
            cst.Arg(keyword=cst.Name("register"), value=cst.Name("False"))
        ]

    return class_node.with_changes(
        decorators=[
            cst.Decorator(
                decorator=cst.Call(
                    func=cst.Name("dataclass"),
                    args=[
                        cst.Arg(keyword=cst.Name("slots"), value=cst.Name("True")),
                        cst.Arg(keyword=cst.Name("frozen"), value=cst.Name("True")),
                        cst.Arg(keyword=cst.Name("kw_only"), value=cst.Name("True")),
                    ],
                )
            )
        ],
        bases=[cst.Arg(value=cst.Name("MessageSegment"))],
        keywords=register_kwarg,
        body=cst.IndentedBlock(body=new_body),
    )


def collect_generated_message_classes(
    dataclass_module: cst.Module,
    dataclass_definitions: dict[str, cst.ClassDef],
) -> tuple[list[cst.ClassDef], set[str]]:
    """
    Collect & transform all message segment classes from the dataclass module.

    Target:
    - class names start with "OB11Message"
    - but do NOT end with "Data"
    - must be a dataclass
    """
    generated_message_classes: list[cst.ClassDef] = []
    flattened_dataclass_names: set[str] = set()

    for stmt in dataclass_module.body:
        if not isinstance(stmt, cst.ClassDef):
            continue

        class_name = stmt.name.value
        if not class_name.startswith("OB11Message"):
            continue
        if class_name.endswith("Data"):
            continue
        if not is_dataclass_class(stmt):
            continue

        transformed = transform_message_segment_class(
            stmt,
            dataclass_definitions,
            flattened_dataclass_names,
        )
        if transformed is None:
            continue
        generated_message_classes.append(transformed)

    return generated_message_classes, flattened_dataclass_names


# ============================================================================
# Assemble output modules
# ============================================================================


def build_generated_message_module(
    typedict_module: cst.Module,
    dataclass_module: cst.Module,
    typedict_definitions: dict[str, cst.ClassDef],
    generated_message_classes: list[cst.ClassDef],
) -> cst.Module:
    """
    Build `messages/generated.py` CST module:
    - header (future import, imports, base class import)
    - helper TypedDict dependencies
    - generated message segment classes
    - selected type aliases (e.g. OB11MessageData) from dataclass module
    """
    generated_message_alias_blocks = collect_selected_type_alias_blocks(
        dataclass_module,
        {"OB11MessageData"},
    )
    alias_reference_names = collect_names_from_type_alias_blocks(
        generated_message_alias_blocks
    )

    helper_typedict_classes = collect_typedict_helper_classes(
        generated_message_classes,
        typedict_module,
        typedict_definitions,
        extra_root_names=sorted(alias_reference_names),
    )

    typing_import_names = ["Any", "Literal", "ClassVar"]
    if helper_typedict_classes:
        typing_import_names.append("TypedDict")

    # If any helper TypedDict references NotRequired, import it.
    has_not_required = any(
        "NotRequired" in collect_annotation_names_from_class(helper_cls)
        for helper_cls in helper_typedict_classes
    )
    if has_not_required:
        typing_import_names.append("NotRequired")

    generated_header = cst.parse_module(
        f"""
# generated by schema_codegen_single.py

\"\"\"
OneBot 11 Message Segments

自动生成的消息段定义 (dataclass)。
包含所有支持的消息段类型，例如 Text, Image, Face 等。
\"\"\"

from __future__ import annotations
from .base import MessageSegment
from dataclasses import dataclass
from typing import {", ".join(typing_import_names)}
"""
    )

    return cst.Module(
        body=[
            *generated_header.body,
            *helper_typedict_classes,
            *generated_message_classes,
            *generated_message_alias_blocks,
        ]
    )


def build_schemas_module(
    cleaned_typedict_module: cst.Module,
    generated_message_module: cst.Module,
    flattened_dataclass_names: set[str],
) -> tuple[cst.Module, list[str]]:
    """
    Build `schemas.py`:
    - remove definitions that are replaced by generated imports (or unused)
    - insert `from .messages.generated import (...)` after existing imports
    """
    generated_definition_names = sorted(
        collect_top_level_definition_names(generated_message_module)
    )
    generated_definition_name_set = set(generated_definition_names)

    referenced_names_in_schemas_source = collect_annotation_names_from_module(
        cleaned_typedict_module
    )
    definition_annotation_names = collect_definition_annotation_names(
        cleaned_typedict_module
    )

    # Remove:
    # - any generated names (because schemas should import them)
    # - any flattened dataclass names (do not belong in schemas)
    #
    # We intentionally remove both sets unconditionally. These legacy local
    # definitions are superseded by `.messages.generated` imports inserted below.
    schemas_names_to_remove = generated_definition_name_set | flattened_dataclass_names

    # Remove unreferenced helper wrappers that only depend on flattened names,
    # e.g. `OB11MessageFileBase -> data: FileBaseData` after FileBaseData removal.
    orphan_helpers_to_remove = {
        name
        for name, ann_names in definition_annotation_names.items()
        if name not in generated_definition_name_set
        and name not in referenced_names_in_schemas_source
        and bool(ann_names & flattened_dataclass_names)
    }
    schemas_names_to_remove |= orphan_helpers_to_remove

    schemas_typedict_module = remove_named_definitions_with_docstrings(
        cleaned_typedict_module,
        schemas_names_to_remove,
    )

    generated_import_module = cst.parse_module(
        "from .messages.generated import (\n"
        + "".join(f"    {name},\n" for name in generated_definition_names)
        + ")\n"
    )

    schemas_body = list(schemas_typedict_module.body)

    # Insert import block after all existing imports.
    insert_index = 0
    for i, stmt in enumerate(schemas_body):
        if is_import_statement(cast(cst.BaseStatement, stmt)):
            insert_index = i + 1
            continue
        break

    docstring_stmt = cst.parse_statement(
        '"""\nOneBot 11/NapCat Schemas\n\n自动生成的 TypedDict 定义，用于 API 请求和响应的数据结构验证。\n"""'
    )

    schemas_module = cst.Module(
        body=[
            docstring_stmt,
            *schemas_body[:insert_index],
            *generated_import_module.body,
            *schemas_body[insert_index:],
        ]
    )

    return schemas_module, generated_definition_names


# ============================================================================
# Pipeline
# ============================================================================


def run_pipeline(config: CodegenConfig | None = None, *, verbose: bool = False) -> None:
    """
    Run the full codegen pipeline.

    Args:
        config: If None, use default CodegenConfig()
        verbose: enable DEBUG logs (only affects logging if not pre-configured)
    """
    configure_logging(verbose=verbose)
    cfg = config or CodegenConfig()

    logger.info("🚀 Start codegen pipeline")
    logger.debug("Config: %s", cfg)

    # Pre-generate openapi.json from NapCat workspace
    if cfg.run_openapi_codegen_before_pipeline:
        try:
            run_openapi_codegen(
                runner=cfg.openapi_codegen_runner,
                cwd=cfg.openapi_codegen_cwd,
            )
        except FileNotFoundError:
            logger.error(
                "OpenAPI codegen runner not found. "
                "Install pnpm (or required toolchain) or disable with run_openapi_codegen_before_pipeline=False.",
            )
            raise
        except subprocess.CalledProcessError:
            logger.error("OpenAPI codegen failed before pipeline. See error above.")
            raise

    # Pre-generate api input files from pyproject profiles
    if cfg.run_datamodel_codegen_before_pipeline:
        try:
            run_datamodel_codegen_profiles(
                cfg.datamodel_codegen_profiles,
                runner=cfg.datamodel_codegen_runner,
            )
        except FileNotFoundError:
            logger.error(
                "datamodel-codegen runner not found. "
                "Install uv/datamodel-codegen or disable with run_datamodel_codegen_before_pipeline=False.",
            )
            raise
        except subprocess.CalledProcessError:
            logger.error("datamodel-codegen failed before pipeline. See error above.")
            raise

    typedict_source = read_text(cfg.typedict_input_path)
    dataclass_source = read_text(cfg.dataclass_input_path)

    typedict_module = cst.parse_module(typedict_source)
    dataclass_module = cst.parse_module(dataclass_source)

    # Collect class definitions
    typedict_collector = ClassCollector()
    typedict_module.visit(typedict_collector)

    dataclass_collector = ClassCollector()
    dataclass_module.visit(dataclass_collector)

    logger.info(
        "📦 Collected %d TypedDict classes", len(typedict_collector.definitions)
    )
    logger.info(
        "📦 Collected %d Dataclass classes", len(dataclass_collector.definitions)
    )

    # Flatten PostResponse schemas
    typedict_flattener = ResponseFlattener(typedict_collector.definitions)
    flattened_typedict_module = typedict_module.visit(typedict_flattener)
    logger.info(
        "🧩 Flattened %d PostResponse data classes",
        len(typedict_flattener.flattened_classes),
    )

    typedict_remover = FlattenedClassRemover(typedict_flattener.flattened_classes)
    cleaned_typedict_module = flattened_typedict_module.visit(typedict_remover)
    logger.info(
        "🗑️  Removed %d flattened class definitions", typedict_remover.removed_count
    )

    # Transform message segment dataclasses
    generated_message_classes, flattened_dataclass_names = (
        collect_generated_message_classes(
            dataclass_module,
            dataclass_collector.definitions,
        )
    )
    logger.info(
        "🧱 Generated %d message segment classes", len(generated_message_classes)
    )

    # Assemble generated.py
    generated_message_module = build_generated_message_module(
        typedict_module,
        dataclass_module,
        typedict_collector.definitions,
        generated_message_classes,
    )

    write_text(cfg.generated_output_path, generated_message_module.code)
    logger.info("✅ Wrote generated messages to: %s", cfg.generated_output_path)

    # Assemble schemas.py
    schemas_module, generated_definition_names = build_schemas_module(
        cleaned_typedict_module,
        generated_message_module,
        flattened_dataclass_names,
    )

    write_text(cfg.schemas_output_path, schemas_module.code)
    logger.info(
        "✅ Wrote schemas module to: %s (imports %d generated symbols)",
        cfg.schemas_output_path,
        len(generated_definition_names),
    )

    # Postprocess renames
    generated_rename_map = postprocess_generated_file(cfg.generated_output_path)
    postprocess_schemas_file(cfg.schemas_output_path, generated_rename_map)

    # Postprocess float/int mapping in generated artifacts
    postprocess_float_to_int_with_location_exceptions(cfg.generated_output_path)
    postprocess_float_to_int_with_location_exceptions(cfg.schemas_output_path)
    postprocess_typeddict_imports(cfg.generated_output_path)
    postprocess_typeddict_imports(cfg.schemas_output_path)

    # Assemble messages/__init__.py from final generated output
    final_generated_source = read_text(cfg.generated_output_path)
    write_messages_init_file(
        cfg.messages_init_output_path,
        final_generated_source,
    )

    if cfg.run_update_init_after_pipeline:
        run_update_init_codegen(script_path=cfg.update_init_script_path)
        logger.info(
            "✅ Updated aggregate init modules: %s, %s",
            cfg.events_init_output_path,
            cfg.types_init_output_path,
        )

    # Generate client_api.py from OpenAPI + schemas.py
    if cfg.run_client_api_codegen_after_pipeline:
        run_client_api_codegen(
            script_path=cfg.client_api_codegen_script_path,
            openapi_path=cfg.openapi_input_path,
            schemas_path=cfg.schemas_output_path,
            output_path=cfg.client_api_output_path,
        )
        logger.info(
            "✅ Wrote client API mixin module to: %s", cfg.client_api_output_path
        )

    if cfg.run_matcher_stub_codegen_after_pipeline:
        run_matcher_stub_codegen(
            script_path=cfg.matcher_stub_codegen_script_path,
            output_path=cfg.matcher_stub_output_path,
        )
        logger.info("✅ Wrote matcher stub module to: %s", cfg.matcher_stub_output_path)

    # Format with Ruff
    if cfg.format_with_ruff:
        try:
            format_generated_files_with_ruff(
                _collect_paths_for_ruff_formatting(cfg),
                ruff_runner=cfg.ruff_runner,
            )
        except FileNotFoundError as _:
            if cfg.ignore_ruff_errors:
                logger.warning(
                    "⚠️  Ruff/uv not found. Skip formatting. (set format_with_ruff=False to disable)",
                )
            else:
                logger.error(
                    "Ruff/uv not found but format_with_ruff=True. "
                    "Install ruff (and uv) or set format_with_ruff=False.",
                )
                raise
        except subprocess.CalledProcessError as e:
            if cfg.ignore_ruff_errors:
                logger.warning("⚠️  Ruff failed (skip formatting): %s", e)
            else:
                logger.error("Ruff failed (format_with_ruff=True). See error above.")
                raise
    else:
        logger.info("ℹ️  Skip formatting (format_with_ruff=False)")

    # Cleanup temporary generated input files
    if cfg.cleanup_codegen_inputs_after_pipeline:
        removed_files = cleanup_codegen_input_files(
            [cfg.typedict_input_path, cfg.dataclass_input_path]
        )
        logger.info(
            "🧽 Cleaned up codegen inputs: %s",
            ", ".join(removed_files) if removed_files else "none",
        )

    logger.info("🎉 Done")


# ============================================================================
# ============================================================================
# CLI
# ============================================================================


def _parse_args(argv: Sequence[str] | None = None) -> tuple[CodegenConfig, bool]:
    """
    Parse CLI arguments.

    Returns:
        (config, verbose)
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog="schema_codegen_single",
        description="Single-file schema code generator (TypedDict + dataclass -> generated artifacts).",
    )
    parser.add_argument(
        "--typedict",
        default=CodegenConfig.typedict_input_path,
        help="Path to api_typedict.py",
    )
    parser.add_argument(
        "--dataclass",
        default=CodegenConfig.dataclass_input_path,
        help="Path to api_dataclass.py",
    )
    parser.add_argument(
        "--out-generated",
        default=CodegenConfig.generated_output_path,
        help="Output path for generated.py",
    )
    parser.add_argument(
        "--out-schemas",
        default=CodegenConfig.schemas_output_path,
        help="Output path for schemas.py",
    )
    parser.add_argument(
        "--out-messages-init",
        default=CodegenConfig.messages_init_output_path,
        help="Output path for messages/__init__.py",
    )

    parser.add_argument(
        "--no-ruff", action="store_true", help="Do not run ruff formatting"
    )
    parser.add_argument(
        "--no-update-init",
        action="store_true",
        help="Do not run update-init after pipeline",
    )
    parser.add_argument(
        "--ignore-ruff-errors",
        action="store_true",
        help="Ignore ruff failures (do not fail pipeline)",
    )
    parser.add_argument(
        "--no-openapi-pre-codegen",
        action="store_true",
        help="Skip building openapi.json before pipeline",
    )
    parser.add_argument(
        "--no-pre-codegen",
        action="store_true",
        help="Skip running datamodel-codegen profiles before pipeline",
    )
    parser.add_argument(
        "--no-cleanup-inputs",
        action="store_true",
        help="Do not delete codegen input files after pipeline",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logs")

    ns = parser.parse_args(argv)

    cfg = CodegenConfig(
        typedict_input_path=ns.typedict,
        dataclass_input_path=ns.dataclass,
        generated_output_path=ns.out_generated,
        schemas_output_path=ns.out_schemas,
        messages_init_output_path=ns.out_messages_init,
        run_openapi_codegen_before_pipeline=not ns.no_openapi_pre_codegen,
        run_datamodel_codegen_before_pipeline=not ns.no_pre_codegen,
        cleanup_codegen_inputs_after_pipeline=not ns.no_cleanup_inputs,
        run_update_init_after_pipeline=not ns.no_update_init,
        format_with_ruff=not ns.no_ruff,
        ignore_ruff_errors=bool(ns.ignore_ruff_errors),
    )
    return cfg, bool(ns.verbose)


def main(argv: Sequence[str] | None = None) -> int:
    """
    CLI entrypoint.

    Returns:
        process exit code
    """
    try:
        cfg, verbose = _parse_args(argv)
        run_pipeline(cfg, verbose=verbose)
        return 0
    except KeyboardInterrupt:  # pragma: no cover
        configure_logging()
        logger.error("Interrupted by user")
        return 130
    except Exception as e:  # pragma: no cover
        configure_logging()
        logger.exception("Unhandled error: %s", e)
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
