import subprocess
import tomllib
import re
import os

import libcst as cst

with open("pyproject.toml", "rb") as f:
    pyproject = tomllib.load(f)

typedict_schema_code_path = pyproject["tool"]["datamodel-codegen"]["profiles"]["message-typedict"]["output"]
dataclass_schema_code_path = pyproject["tool"]["datamodel-codegen"]["profiles"]["message-dataclass"]["output"]

subprocess.run(["bun", "scripts/extract-message-schema.ts"], check=True)
subprocess.run(["uv", "run", "datamodel-codegen", "--profile", "message-typedict"], check=True)
subprocess.run(["uv", "run", "datamodel-codegen", "--profile", "message-dataclass"], check=True)

with open(typedict_schema_code_path, "r", encoding="utf-8") as f:
    gencode_content = f.read()

with open(dataclass_schema_code_path, "r", encoding="utf-8") as f:
    dataclass_content = f.read()

pattern = r"(?m)^\s*from\s+typing_extensions\s+import\s+(?:\(\s*)?TypedDict(?:\s*,?\s*)?(?:\)\s*)?.*?\n?"

gencode_content = re.sub(pattern, "from .base import SegmentDataTypeBase, SegmentDataBase, MessageSegment\nfrom dataclasses import dataclass\n", gencode_content)

gencode_content = gencode_content.replace("float", "int").replace(", closed=True", "")
gencode_content = gencode_content.replace("from typing import Any, Literal, NotRequired",
                                            "from typing import Any, Literal, NotRequired, TYPE_CHECKING, ClassVar, Unpack")

pending_renames: set[str] = set()
class ChangeToBase(cst.CSTTransformer):
    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.BaseStatement | cst.FlattenSentinel[cst.BaseStatement] | cst.RemovalSentinel:
        # 如果类名以Data结尾，则修改其基类为 SegmentDataTypeBase
        if original_node.name.value.endswith("Data"):
            pending_renames.add(original_node.name.value)
            new_bases = [
                cst.Arg(value=cst.Name("SegmentDataTypeBase"))
            ]
            return updated_node.with_changes(bases=new_bases)
        return cst.RemoveFromParent()
    
    def leave_TypeAlias(self, original_node: cst.TypeAlias, updated_node: cst.TypeAlias) -> cst.BaseSmallStatement | cst.FlattenSentinel[cst.BaseSmallStatement] | cst.RemovalSentinel:
        return cst.RemoveFromParent()

module = cst.parse_module(gencode_content)
transformer = ChangeToBase()
modified_module = module.visit(transformer)

gencode_content = modified_module.code

for name in pending_renames:
    gencode_content = gencode_content.replace(name+"(", name + "Type(")

dataclass_content = dataclass_content.replace("@dataclass", "@dataclass(slots=True, frozen=True, kw_only=True)")
dataclass_content = dataclass_content.replace("""from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Literal""", "")
dataclass_content = dataclass_content.replace("float", "int")

class ChangeToBase2(cst.CSTTransformer):
    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.BaseStatement | cst.FlattenSentinel[cst.BaseStatement] | cst.RemovalSentinel:
        # 如果类名以Data结尾，则修改其基类为 SegmentDataBase
        if original_node.name.value.endswith("Data"):
            new_bases = [
                cst.Arg(value=cst.Name("SegmentDataBase"))
            ]
            return updated_node.with_changes(bases=new_bases)
        # 如果类名不包含Data，则修改其基类为 MessageSegment
        elif "Data" not in original_node.name.value:
            new_bases = [
                cst.Arg(value=cst.Name("MessageSegment"))
            ]
            return updated_node.with_changes(bases=new_bases)
        return updated_node

class InjectInitTypeChecking(cst.CSTTransformer):
    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.BaseStatement:
        # 1. 检查是否继承自 MessageSegment
        is_segment = False
        for base in original_node.bases:
            if getattr(base.value, 'value', '') == 'MessageSegment':
                is_segment = True
                break

        if not is_segment:
            return updated_node

        # 2. 查找 'data' 字段的类型注解 (例如: MessageReplyData)
        data_class_name = None
        for statement in original_node.body.body:
            # 匹配: data: Annotation
            if isinstance(statement, cst.AnnAssign) and \
               isinstance(statement.target, cst.Name) and \
               statement.target.value == 'data':
                
                # 提取注解名称
                annotation = statement.annotation.annotation
                if isinstance(annotation, cst.Name):
                    data_class_name = annotation.value
                break
        
        print(data_class_name)
        if not data_class_name:
            return updated_node

        # 3. 构建对应的 TypeDict 名称 (例如: MessageReplyDataType)
        typedict_name = data_class_name + "Type"

        # 4. 构建要注入的 if TYPE_CHECKING 代码块
        if_type_checking_node = cst.If(
            test=cst.Name("TYPE_CHECKING"),
            body=cst.IndentedBlock(
                body=[
                    # 修复点：AnnAssign 必须包裹在 SimpleStatementLine 中
                    cst.SimpleStatementLine(
                        body=[
                            cst.AnnAssign(
                                target=cst.Name("_data_class"),
                                annotation=cst.Annotation(
                                    annotation=cst.parse_expression(f"ClassVar[type[{data_class_name}]]")
                                ),
                                value=None
                            )
                        ]
                    ),
                    # def __init__(self, **kwargs: Unpack[MessageReplyDataType]): ...
                    # FunctionDef 是复合语句，可以直接作为 Block 的元素
                    cst.FunctionDef(
                        name=cst.Name("__init__"),
                        params=cst.Parameters(
                            params=[cst.Param(name=cst.Name("self"))],
                            star_kwarg=cst.Param(
                                name=cst.Name("kwargs"),
                                annotation=cst.Annotation(
                                    annotation=cst.parse_expression(f"Unpack[{typedict_name}]")
                                )
                            )
                        ),
                        body=cst.IndentedBlock(
                            body=[cst.SimpleStatementLine(body=[cst.Expr(value=cst.Ellipsis())])]
                        )
                    )
                ]
            )
        )

        # 5. 将新节点追加到类体中
        new_body_content = list(updated_node.body.body)
        new_body_content.append(if_type_checking_node)

        return updated_node.with_changes(
            body=updated_node.body.with_changes(body=new_body_content)
        )

module = cst.parse_module(dataclass_content)
transformer = ChangeToBase2()
modified_module = module.visit(transformer)
transformer_inject = InjectInitTypeChecking()
modified_module = modified_module.visit(transformer_inject)
dataclass_content = modified_module.code

lines = dataclass_content.splitlines()
new_lines = lines.copy()
for i, line in enumerate(lines):
    if line.startswith("class ") and "MessageSegment" in line:
        new_lines[i-1] = "@dataclass(slots=True, frozen=True, kw_only=True, init=False)"

dataclass_content = "\n".join(new_lines)

gencode_content += "\n\n" + dataclass_content

gencode_content = gencode_content.replace("OB11", "")
with open("src/napcat/types/messages/generated.py", "w", encoding="utf-8") as f:
    f.write(gencode_content)

os.remove(typedict_schema_code_path)
os.remove(dataclass_schema_code_path)