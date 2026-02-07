from collections.abc import Sequence
from typing import cast

import libcst as cst
import libcst.matchers as m
from libcst import BaseStatement, FlattenSentinel, RemovalSentinel


class ResponseFlattener(cst.CSTTransformer):
    def __init__(self, definitions: dict[str, cst.ClassDef]):
        self.definitions = definitions
        self.flattened_classes: list[str] = []

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> BaseStatement | FlattenSentinel[BaseStatement] | RemovalSentinel:
        if not original_node.name.value.endswith("PostResponse"):
            return updated_node

        data_annotation: cst.BaseExpression | None = None
        data_field_pattern = m.SimpleStatementLine(
            body=[m.AnnAssign(target=m.Name(value="data"))]
        )

        for stmt in original_node.body.body:
            if m.matches(stmt, data_field_pattern):
                simple_stmt = cast(cst.SimpleStatementLine, stmt)
                ann_assign = cast(cst.AnnAssign, simple_stmt.body[0])
                data_annotation = ann_assign.annotation.annotation
                break

        if not data_annotation:
            return updated_node

        if (
            isinstance(data_annotation, cst.Name)
            and data_annotation.value in self.definitions
            and data_annotation.value.startswith("Data")
        ):
            ref_class_name = data_annotation.value
            ref_class_node = self.definitions[ref_class_name]

            new_body_list: list[BaseStatement] = []
            docstring_pattern = m.SimpleStatementLine(
                body=[m.Expr(value=m.SimpleString() | m.ConcatenatedString())]
            )

            if original_node.body.body and m.matches(original_node.body.body[0], docstring_pattern):
                doc_stmt = cast(BaseStatement, original_node.body.body[0])
                new_body_list.append(doc_stmt)

            source_stmts = cast(Sequence[BaseStatement], ref_class_node.body.body)
            ref_body_stmts = list(source_stmts)
            if ref_body_stmts and m.matches(ref_body_stmts[0], docstring_pattern):
                ref_body_stmts.pop(0)

            new_body_list.extend(ref_body_stmts)
            self.flattened_classes.append(ref_class_name)

            return updated_node.with_changes(
                bases=[cst.Arg(value=cst.Name("TypedDict"))],
                body=cst.IndentedBlock(body=new_body_list),
            )

        type_alias_node = cst.TypeAlias(name=original_node.name, value=data_annotation)
        return cst.SimpleStatementLine(
            body=[type_alias_node],
            leading_lines=original_node.leading_lines,
        )


class FlattenedClassRemover(cst.CSTTransformer):
    def __init__(self, flattened_classes: Sequence[str]):
        self.flattened_class_set = set(flattened_classes)
        self.removed_count = 0

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> BaseStatement | FlattenSentinel[BaseStatement] | RemovalSentinel:
        if original_node.name.value in self.flattened_class_set:
            self.removed_count += 1
            return cst.RemoveFromParent()
        return updated_node


class DefinitionNameRemover(cst.CSTTransformer):
    def __init__(self, names_to_remove: set[str]):
        self.names_to_remove = names_to_remove

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> BaseStatement | FlattenSentinel[BaseStatement] | RemovalSentinel:
        if original_node.name.value in self.names_to_remove:
            return cst.RemoveFromParent()
        return updated_node

    def leave_SimpleStatementLine(
        self,
        original_node: cst.SimpleStatementLine,
        updated_node: cst.SimpleStatementLine,
    ) -> BaseStatement | FlattenSentinel[BaseStatement] | RemovalSentinel:
        for small_stmt in original_node.body:
            if isinstance(small_stmt, cst.TypeAlias) and small_stmt.name.value in self.names_to_remove:
                return cst.RemoveFromParent()
        return updated_node
