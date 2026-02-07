from collections.abc import Sequence
import re
import subprocess

import libcst as cst


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_text(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _apply_generated_name_rules(name: str) -> str:
    replaced = name.replace("OB11MessageData", "Message")
    replaced = replaced.replace("OB11Message", "")
    return replaced


def _collect_top_level_definition_names(source: str) -> set[str]:
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


def _replace_identifier_names(source: str, rename_map: dict[str, str]) -> tuple[str, set[str]]:
    replaced = source
    applied_names: set[str] = set()

    for old_name in sorted(rename_map, key=len, reverse=True):
        new_name = rename_map[old_name]
        pattern = re.compile(rf"\b{re.escape(old_name)}\b")
        replaced, count = pattern.subn(new_name, replaced)
        if count > 0:
            applied_names.add(old_name)

    return replaced, applied_names


def _expr_to_dotted_name(expr: cst.BaseExpression) -> str | None:
    if isinstance(expr, cst.Name):
        return expr.value
    if isinstance(expr, cst.Attribute):
        left = _expr_to_dotted_name(expr.value)
        if left is None:
            return None
        return f"{left}.{expr.attr.value}"
    return None


def _collect_generated_import_names(source: str) -> set[str]:
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


def postprocess_generated_file(path: str) -> dict[str, str]:
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
    print(
        f"Post-processed generated file {path} with {len(applied_rename_map)} renames."
    )
    return applied_rename_map


def postprocess_schemas_file(path: str, generated_rename_map: dict[str, str]) -> None:
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

    print(
        "Post-processed schemas file "
        f"{path} with {len(applied_names)} renames from generated imports."
    )


def postprocess_generated_files(paths: Sequence[str]) -> None:
    for path in paths:
        source = read_text(path)

        replaced = source.replace("OB11MessageData", "Message")
        replaced = replaced.replace("OB11Message", "")

        if replaced != source:
            write_text(path, replaced)

        print(f"Post-processed replacements for {path}.")


def format_generated_files_with_ruff(paths: Sequence[str]) -> None:
    if not paths:
        return

    subprocess.run(["uv", "run", "ruff", "check", "--fix", *paths], check=True)
    subprocess.run(["uv", "run", "ruff", "format", *paths], check=True)

    print(f"Formatted generated files with Ruff: {', '.join(paths)}.")
