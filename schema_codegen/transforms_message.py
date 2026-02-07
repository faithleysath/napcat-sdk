from typing import cast

import libcst as cst
from libcst import BaseStatement

from .extractors import (
    extract_literal_string,
    get_base_class_name,
    get_field_blocks,
)
from .predicates import is_dataclass_class, is_docstring_stmt


def collect_dataclass_fields_with_inheritance(
    class_name: str,
    definitions: dict[str, cst.ClassDef],
    visiting: set[str] | None = None,
) -> list[tuple[str, list[BaseStatement]]]:
    if visiting is None:
        visiting = set()
    if class_name in visiting:
        return []

    class_node = definitions.get(class_name)
    if not class_node or not is_dataclass_class(class_node):
        return []

    visiting.add(class_name)

    field_order: list[str] = []
    field_blocks: dict[str, list[BaseStatement]] = {}

    def upsert_field(name: str, block: list[BaseStatement]) -> None:
        if name not in field_blocks:
            field_order.append(name)
        field_blocks[name] = block

    for base in class_node.bases:
        base_name = get_base_class_name(base)
        if not base_name:
            continue
        for fname, fblock in collect_dataclass_fields_with_inheritance(base_name, definitions, visiting):
            upsert_field(fname, fblock)

    for fname, _, fblock in get_field_blocks(class_node):
        upsert_field(fname, fblock)

    visiting.remove(class_name)
    return [(fname, field_blocks[fname]) for fname in field_order]


def collect_dataclass_class_names_with_inheritance(
    class_name: str,
    definitions: dict[str, cst.ClassDef],
    visiting: set[str] | None = None,
) -> set[str]:
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
            collect_dataclass_class_names_with_inheritance(base_name, definitions, visiting)
        )

    visiting.remove(class_name)
    return collected


def transform_message_segment_class(
    class_node: cst.ClassDef,
    definitions: dict[str, cst.ClassDef],
    flattened_dataclass_names: set[str] | None = None,
) -> cst.ClassDef | None:
    field_blocks = get_field_blocks(class_node)
    field_map = {name: (ann, block) for name, ann, block in field_blocks}

    type_field = field_map.get("type")
    if not type_field:
        return None

    type_ann, _ = type_field
    type_literal = extract_literal_string(type_ann.annotation.annotation)
    if type_literal is None:
        return None

    new_body: list[BaseStatement] = []
    original_body = list(class_node.body.body)
    if original_body and is_docstring_stmt(cast(BaseStatement, original_body[0])):
        new_body.append(cast(BaseStatement, original_body[0]))

    type_stmt = cst.parse_statement(f'_type: ClassVar[str] = "{type_literal}"\n')
    new_body.append(type_stmt)

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

    for name, _, block in field_blocks:
        if name in {"type", "data"}:
            continue
        new_body.extend(block)

    return class_node.with_changes(
        bases=[cst.Arg(value=cst.Name("MessageSegment"))],
        body=cst.IndentedBlock(body=new_body),
    )


def collect_generated_message_classes(
    dataclass_module: cst.Module,
    dataclass_definitions: dict[str, cst.ClassDef],
) -> tuple[list[cst.ClassDef], set[str]]:
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
