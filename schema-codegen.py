import libcst as cst
import libcst.matchers as m
from libcst import BaseStatement, FlattenSentinel, RemovalSentinel
from typing import cast
from collections.abc import Sequence
import ast

class ClassCollector(cst.CSTVisitor):
    """
    第一步：扫描全文件，收集类定义
    """
    def __init__(self):
        self.definitions: dict[str, cst.ClassDef] = {}

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        self.definitions[node.name.value] = node


class NameCollector(cst.CSTVisitor):
    def __init__(self) -> None:
        self.names: set[str] = set()

    def visit_Name(self, node: cst.Name) -> None:
        self.names.add(node.value)

class ResponseFlattener(cst.CSTTransformer):
    """
    第二步：展平 PostResponse 类
    """
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

        # === 场景 A: 嵌套类 (Data50) ===
        if isinstance(data_annotation, cst.Name) and data_annotation.value in self.definitions and data_annotation.value.startswith("Data"):
            ref_class_name = data_annotation.value
            ref_class_node = self.definitions[ref_class_name]
            
            # 【修复 1】：显式声明为 list[BaseStatement]，这是 IndentedBlock 唯一接受的类型
            new_body_list: list[BaseStatement] = []

            docstring_pattern = m.SimpleStatementLine(
                body=[m.Expr(value=m.SimpleString() | m.ConcatenatedString())]
            )

            # (1) 处理宿主类 Docstring
            if original_node.body.body and m.matches(original_node.body.body[0], docstring_pattern):
                # cast 确保 Pylance 知道这一定是 BaseStatement
                doc_stmt = cast(BaseStatement, original_node.body.body[0])
                new_body_list.append(doc_stmt)

            # (2) 处理引用类 Body
            # 【修复 2】：使用 cast 告诉 Pylance "我保证这里面全是 BaseStatement"
            # 这样就可以安全地 extend 到 new_body_list 里了
            source_stmts = cast(Sequence[BaseStatement], ref_class_node.body.body)
            ref_body_stmts = list(source_stmts)

            if ref_body_stmts and m.matches(ref_body_stmts[0], docstring_pattern):
                ref_body_stmts.pop(0)

            # 现在类型完全匹配：list[BaseStatement] extend list[BaseStatement]
            new_body_list.extend(ref_body_stmts)

            self.flattened_classes.append(ref_class_name)

            return updated_node.with_changes(
                bases=[cst.Arg(value=cst.Name("TypedDict"))],
                # 这里就不会报错了，因为 new_body_list 严格符合类型
                body=cst.IndentedBlock(
                    body=new_body_list
                )
            )

        # === 场景 B: 基本类型 (Type Alias) ===
        else:
            type_alias_node = cst.TypeAlias(
                name=original_node.name,
                value=data_annotation
            )
            return cst.SimpleStatementLine(
                body=[type_alias_node],
                leading_lines=original_node.leading_lines
            )

class FlattenedClassRemover(cst.CSTTransformer):
    """
    第三步：移除已被展平到 PostResponse 类中的引用类定义
    """
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
    """
    按名称移除顶层定义（ClassDef / TypeAlias）。
    """
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


def is_docstring_stmt(stmt: BaseStatement) -> bool:
    return m.matches(
        stmt,
        m.SimpleStatementLine(
            body=[m.Expr(value=m.SimpleString() | m.ConcatenatedString())]
        ),
    )


def is_dataclass_class(class_node: cst.ClassDef) -> bool:
    for decorator in class_node.decorators:
        d = decorator.decorator
        if isinstance(d, cst.Name) and d.value == "dataclass":
            return True
        if isinstance(d, cst.Call) and isinstance(d.func, cst.Name) and d.func.value == "dataclass":
            return True
    return False


def get_field_blocks(
    class_node: cst.ClassDef,
) -> list[tuple[str, cst.AnnAssign, list[BaseStatement]]]:
    """
    提取字段块：AnnAssign + 紧随其后的字段 docstring。
    """
    body = list(class_node.body.body)
    result: list[tuple[str, cst.AnnAssign, list[BaseStatement]]] = []

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
            block: list[BaseStatement] = [stmt]

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
    """
    从 Literal["xxx"] 中提取 xxx。
    """
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
    """
    从消息段类的注解依赖中，递归收集 typedict 辅助类。
    """
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


def collect_selected_type_alias_blocks(
    module: cst.Module,
    target_alias_names: set[str],
) -> list[cst.SimpleStatementLine]:
    """
    从模块顶层提取指定名称的 TypeAlias 语句块（包含紧随其后的 docstring）。
    """
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


def is_import_statement(stmt: BaseStatement) -> bool:
    if not isinstance(stmt, cst.SimpleStatementLine):
        return False
    for small_stmt in stmt.body:
        if isinstance(small_stmt, cst.Import) or isinstance(small_stmt, cst.ImportFrom):
            return True
    return False


def postprocess_generated_files(paths: Sequence[str]) -> None:
    """
    生成完成后的纯文本全局替换（不使用 libcst）：
    1) OB11MessageData -> Message
    2) OB11Message -> ""
    """
    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()

        replaced = source.replace("OB11MessageData", "Message")
        replaced = replaced.replace("OB11Message", "")

        if replaced != source:
            with open(path, "w", encoding="utf-8") as f:
                f.write(replaced)

        print(f"Post-processed replacements for {path}.")


def collect_dataclass_fields_with_inheritance(
    class_name: str,
    definitions: dict[str, cst.ClassDef],
    visiting: set[str] | None = None,
) -> list[tuple[str, list[BaseStatement]]]:
    """
    递归收集 dataclass 字段（父类 -> 子类），同名字段由子类覆盖。
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


def transform_message_segment_class(
    class_node: cst.ClassDef,
    definitions: dict[str, cst.ClassDef],
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

    # 保留类 docstring
    original_body = list(class_node.body.body)
    if original_body and is_docstring_stmt(cast(BaseStatement, original_body[0])):
        new_body.append(cast(BaseStatement, original_body[0]))

    # type -> _type
    type_stmt = cst.parse_statement(f'_type: ClassVar[str] = "{type_literal}"\n')
    new_body.append(type_stmt)

    # 展平 data
    data_field = field_map.get("data")
    if data_field:
        data_ann, _ = data_field
        data_annotation = data_ann.annotation.annotation
        if isinstance(data_annotation, cst.Name):
            flattened_fields = collect_dataclass_fields_with_inheritance(
                data_annotation.value,
                definitions,
            )
            for _, block in flattened_fields:
                new_body.extend(block)

    # 追加宿主类其他字段
    for name, _, block in field_blocks:
        if name in {"type", "data"}:
            continue
        new_body.extend(block)

    return class_node.with_changes(
        bases=[cst.Arg(value=cst.Name("MessageSegment"))],
        body=cst.IndentedBlock(body=new_body),
    )

with open("api_typedict.py", "r", encoding="utf-8") as f:
    typedict_source = f.read()

with open("api_dataclass.py", "r", encoding="utf-8") as f:
    dataclass_source = f.read()

# 0. 解析
typedict_module = cst.parse_module(typedict_source)
dataclass_module = cst.parse_module(dataclass_source)

# 1. 收集
typedict_collector = ClassCollector()
typedict_module.visit(typedict_collector)
dataclass_collector = ClassCollector()
dataclass_module.visit(dataclass_collector)

print(f"Collected {len(typedict_collector.definitions)} TypedDict classes.")
print(f"Collected {len(dataclass_collector.definitions)} Dataclass classes.")

# 2. Typedict PostResponseTypedDict展平化
typedict_flattener = ResponseFlattener(typedict_collector.definitions)
flattened_typedict_module = typedict_module.visit(typedict_flattener)
print(f"Successfully flattened {len(typedict_flattener.flattened_classes)} PostResponse classes.")

# 3. 移除被展平的类定义
typedict_remover = FlattenedClassRemover(typedict_flattener.flattened_classes)
cleaned_typedict_module = flattened_typedict_module.visit(typedict_remover)
print(f"Successfully removed {typedict_remover.removed_count} flattened class definitions.")

# 4. 从 dataclass_module 提取并生成 MessageSegment 模块
generated_message_classes: list[cst.ClassDef] = []

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

    transformed = transform_message_segment_class(stmt, dataclass_collector.definitions)
    if transformed is None:
        continue
    generated_message_classes.append(transformed)

helper_typedict_classes = collect_typedict_helper_classes(
    generated_message_classes,
    typedict_module,
    typedict_collector.definitions,
)

typing_import_names = ["Any", "Literal", "ClassVar"]
if helper_typedict_classes:
    typing_import_names.append("TypedDict")

has_not_required = False
for helper_cls in helper_typedict_classes:
    if "NotRequired" in collect_annotation_names_from_class(helper_cls):
        has_not_required = True
        break
if has_not_required:
    typing_import_names.append("NotRequired")

generated_message_alias_blocks = collect_selected_type_alias_blocks(
    dataclass_module,
    {"OB11MessageData"},
)

generated_header = cst.parse_module(
    f"""
# generated by schema-codegen.py

from __future__ import annotations
from .base import MessageSegment
from dataclasses import dataclass
from typing import {", ".join(typing_import_names)}
"""
)

generated_message_module = cst.Module(
    body=[
        *generated_header.body,
        *helper_typedict_classes,
        *generated_message_classes,
        *generated_message_alias_blocks,
    ]
)

generated_output_path = "src/napcat/types/messages/generated.py"
with open(generated_output_path, "w", encoding="utf-8") as f:
    f.write(generated_message_module.code)

print(f"Successfully generated {len(generated_message_classes)} message segment classes to {generated_output_path}.")

# 5. 生成 schemas.py：从 generated 导入所有定义，并删除 typedict 同名定义
generated_definition_names = sorted(collect_top_level_definition_names(generated_message_module))

typedict_remover_for_schemas = DefinitionNameRemover(set(generated_definition_names))
schemas_typedict_module = typedict_module.visit(typedict_remover_for_schemas)

generated_import_module = cst.parse_module(
    "from .messages.generated import (\n"
    + "".join(f"    {name},\n" for name in generated_definition_names)
    + ")\n"
)

schemas_body = list(schemas_typedict_module.body)
insert_index = 0
for i, stmt in enumerate(schemas_body):
    if is_import_statement(stmt):
        insert_index = i + 1
        continue
    break

schemas_module = cst.Module(
    body=[
        *schemas_body[:insert_index],
        *generated_import_module.body,
        *schemas_body[insert_index:],
    ]
)

schemas_output_path = "src/napcat/types/schemas.py"
with open(schemas_output_path, "w", encoding="utf-8") as f:
    f.write(schemas_module.code)

print(
    "Successfully generated schemas module to "
    f"{schemas_output_path} with {len(generated_definition_names)} generated imports."
)

# 6. 生成完成后对两个文件做全局替换（纯文本）
postprocess_generated_files(
    [
        generated_output_path,
        schemas_output_path,
    ]
)