import subprocess
import tomllib
import re

import libcst as cst

with open("pyproject.toml", "rb") as f:
    pyproject = tomllib.load(f)

typedict_schema_code_path = pyproject["tool"]["datamodel-codegen"]["profiles"]["message-typedict"]["output"]
dataclass_schema_code_path = pyproject["tool"]["datamodel-codegen"]["profiles"]["message-dataclass"]["output"]

subprocess.run(["bun", "scripts/extract-message-schema.ts"], check=True)
subprocess.run(["uv", "run", "datamodel-codegen", "--profile", "message-typedict"], check=True)
subprocess.run(["uv", "run", "datamodel-codegen", "--profile", "message-dataclass"], check=True)

with open(typedict_schema_code_path, "r", encoding="utf-8") as f:
    typedict_content = f.read()

with open(dataclass_schema_code_path, "r", encoding="utf-8") as f:
    dataclass_content = f.read()

pattern = r"(?m)^\s*from\s+typing_extensions\s+import\s+(?:\(\s*)?TypedDict(?:\s*,?\s*)?(?:\)\s*)?.*?\n?"

typedict_content = re.sub(pattern, "from .base import SegmentDataTypeBase, SegmentDataBase, MessageSegment\nfrom dataclasses import dataclass\n", typedict_content)

typedict_content = typedict_content.replace("float", "int").replace(", closed=True", "")

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

module = cst.parse_module(typedict_content)
transformer = ChangeToBase()
modified_module = module.visit(transformer)

typedict_content = modified_module.code

for name in pending_renames:
    typedict_content = typedict_content.replace(name+"(", name + "Type(")

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

module = cst.parse_module(dataclass_content)
transformer = ChangeToBase2()
modified_module = module.visit(transformer)
dataclass_content = modified_module.code

lines = dataclass_content.splitlines()
new_lines = lines.copy()
for i, line in enumerate(lines):
    if line.startswith("class ") and "MessageSegment" in line:
        new_lines[i-1] = "@dataclass(slots=True, frozen=True, kw_only=True, init=False)"

dataclass_content = "\n".join(new_lines)

typedict_content += "\n\n" + dataclass_content

typedict_content = typedict_content.replace("OB11", "")
with open(typedict_schema_code_path, "w", encoding="utf-8") as f:
    f.write(typedict_content)
