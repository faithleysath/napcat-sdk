import libcst as cst
import libcst.matchers as m
from libcst import BaseStatement, FlattenSentinel, RemovalSentinel
from typing import cast
from collections.abc import Sequence

class ClassCollector(cst.CSTVisitor):
    """
    第一步：扫描全文件，收集类定义
    """
    def __init__(self):
        self.definitions: dict[str, cst.ClassDef] = {}

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        self.definitions[node.name.value] = node

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

with open("api_typedict.py", "r", encoding="utf-8") as f:
    typedict_source = f.read()

with open("api_dataclass.py", "r", encoding="utf-8") as f:
    dataclass_source = f.read()

# 1. 解析
typedict_module = cst.parse_module(typedict_source)
dataclass_module = cst.parse_module(dataclass_source)

# 2. 收集
typedict_collector = ClassCollector()
typedict_module.visit(typedict_collector)
dataclass_collector = ClassCollector()
dataclass_module.visit(dataclass_collector)

print(f"Collected {len(typedict_collector.definitions)} TypedDict classes.")
print(f"Collected {len(dataclass_collector.definitions)} Dataclass classes.")

# 3. Typedict PostResponseTypedDict展平化
typedict_flattener = ResponseFlattener(typedict_collector.definitions)
flattened_typedict_module = typedict_module.visit(typedict_flattener)
print(f"Successfully flattened {len(typedict_flattener.flattened_classes)} PostResponse classes.")

# 4. 移除被展平的类定义
typedict_remover = FlattenedClassRemover(typedict_flattener.flattened_classes)
cleaned_typedict_module = flattened_typedict_module.visit(typedict_remover)
print(f"Successfully removed {typedict_remover.removed_count} flattened class definitions.")

# 5. 写出
with open("api_typedict_flatten.py", "w", encoding="utf-8") as f:
    f.write(cleaned_typedict_module.code)