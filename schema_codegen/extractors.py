import ast
from collections.abc import Sequence

import libcst as cst

from .collectors import NameCollector
from .predicates import is_docstring_stmt


def get_field_blocks(
    class_node: cst.ClassDef,
) -> list[tuple[str, cst.AnnAssign, list[cst.BaseStatement]]]:
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
                if isinstance(next_stmt, cst.SimpleStatementLine) and is_docstring_stmt(next_stmt):
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
    if not isinstance(annotation, cst.Subscript):
        return None
    if not isinstance(annotation.value, cst.Name) or annotation.value.value != "Literal":
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
    if isinstance(base.value, cst.Name):
        return base.value.value
    return None


def collect_names_from_expr(expr: cst.BaseExpression) -> set[str]:
    visitor = NameCollector()
    expr.visit(visitor)
    return visitor.names


def collect_annotation_names_from_class(class_node: cst.ClassDef) -> set[str]:
    names: set[str] = set()
    for _, ann_assign, _ in get_field_blocks(class_node):
        names.update(collect_names_from_expr(ann_assign.annotation.annotation))
    return names


def collect_typedict_helper_classes(
    message_classes: Sequence[cst.ClassDef],
    typedict_module: cst.Module,
    typedict_definitions: dict[str, cst.ClassDef],
) -> list[cst.ClassDef]:
    message_class_names = {cls.name.value for cls in message_classes}

    helper_names: set[str] = set()
    queue: list[str] = []

    for cls in message_classes:
        for name in collect_annotation_names_from_class(cls):
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

    ordered_helpers: list[cst.ClassDef] = []
    for stmt in typedict_module.body:
        if isinstance(stmt, cst.ClassDef) and stmt.name.value in helper_names:
            ordered_helpers.append(stmt)

    return ordered_helpers


def collect_top_level_definition_names(module: cst.Module) -> set[str]:
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


def collect_selected_type_alias_blocks(
    module: cst.Module,
    target_alias_names: set[str],
) -> list[cst.SimpleStatementLine]:
    body = list(module.body)
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
                    and small_stmt.name.value in target_alias_names
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
