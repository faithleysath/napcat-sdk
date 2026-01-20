import re
import subprocess
import tomllib
from pathlib import Path

import libcst as cst

# --- 配置与常量 ---
PROJECT_ROOT = Path(__file__).parents[1]  # 假设脚本在 scripts/ 目录下
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"
OUTPUT_FILE = PROJECT_ROOT / "src/napcat/types/messages/generated.py"

# 正则替换规则
REGEX_REPLACEMENTS = [
    # 替换 TypedDict 导入
    (
        r"(?m)^\s*from\s+typing_extensions\s+import\s+(?:\(\s*)?TypedDict(?:\s*,?\s*)?(?:\)\s*)?.*?\n?",
        "from .base import SegmentDataTypeBase, SegmentDataBase, MessageSegment\nfrom dataclasses import dataclass\n"
    ),
    # 基础类型修正
    (r"\bfloat\b", "int"),
    (r", closed=True", ""),
    # 补充 typing 导入
    (
        r"from typing import Any, Literal, NotRequired",
        "from typing import Any, Literal, NotRequired, TYPE_CHECKING, ClassVar, Unpack"
    ),
    # 移除无用导入
    (r"from __future__ import annotations\nfrom dataclasses import dataclass\nfrom typing import Any, Literal", ""),
    (r"OB11", ""),
]


# --- AST 转换器 ---

class TypedDictTransformer(cst.CSTTransformer):
    """处理 TypedDict: 修改基类并收集需要重命名的类"""
    
    def __init__(self):
        self.renamed_classes: set[str] = set()

    def leave_TypeAlias(self, original_node: cst.TypeAlias, updated_node: cst.TypeAlias) -> cst.BaseSmallStatement | cst.RemovalSentinel:
        return cst.RemoveFromParent()

    def visit_ClassDef(self, node: cst.ClassDef) -> bool:
        # 如果类名以 Data 结尾，修改基类
        if node.name.value.endswith("Data"):
            self.renamed_classes.add(node.name.value)
            # 在 leave 阶段修改，这里只做标记或直接修改均可，为了逻辑分离放在 leave
        return True

    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.BaseStatement | cst.RemovalSentinel:
        if original_node.name.value.endswith("Data"):
            return updated_node.with_changes(
                bases=[cst.Arg(value=cst.Name("SegmentDataTypeBase"))]
            )
        return cst.RemoveFromParent()


class DataclassTransformer(cst.CSTTransformer):
    """处理 Dataclass: 修改基类、注入 init 类型检查、修改装饰器"""

    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.BaseStatement | cst.RemovalSentinel:
        class_name = original_node.name.value
        is_data_class = class_name.endswith("Data")
        
        # 1. 修改继承关系
        if is_data_class:
            updated_node = updated_node.with_changes(
                bases=[cst.Arg(value=cst.Name("SegmentDataBase"))]
            )
        elif "Data" not in class_name:
            # 这是 MessageSegment 的实现类
            updated_node = updated_node.with_changes(
                bases=[cst.Arg(value=cst.Name("MessageSegment"))]
            )
            # 注入 TYPE_CHECKING 和 Unpack 逻辑
            updated_node = self._inject_type_checking(updated_node, original_node)
            # 修改装饰器添加 init=False
            updated_node = self._update_decorator(updated_node)
            
        return updated_node

    def _update_decorator(self, node: cst.ClassDef) -> cst.ClassDef:
        """为 MessageSegment 子类添加 init=False 到 @dataclass 装饰器"""
        # 注意：这里假设只有一个 decorator 且是 @dataclass
        # 更加稳健的做法是查找名为 dataclass 的 decorator
        new_decorators: list[cst.Decorator] = []
        for decorator in node.decorators:
            if isinstance(decorator.decorator, cst.Call) and isinstance(decorator.decorator.func, cst.Name) and decorator.decorator.func.value == "dataclass":
                # 复制现有的 args 并添加 init=False
                new_args = list(decorator.decorator.args)
                new_args.append(cst.Arg(keyword=cst.Name("init"), value=cst.Name("False")))
                
                new_decorators.append(
                    decorator.with_changes(
                        decorator=decorator.decorator.with_changes(args=new_args)
                    )
                )
            else:
                new_decorators.append(decorator)
        
        return node.with_changes(decorators=new_decorators)

    def _inject_type_checking(self, node: cst.ClassDef, original_node: cst.ClassDef) -> cst.ClassDef:
        """注入 if TYPE_CHECKING 块"""
        # 查找 data 字段的类型注解
        data_class_name = None
        for stmt in original_node.body.body:
            if isinstance(stmt, cst.SimpleStatementLine):
                for small_stmt in stmt.body:
                    if isinstance(small_stmt, cst.AnnAssign):
                        if isinstance(small_stmt.target, cst.Name) and small_stmt.target.value == "data":
                            if isinstance(small_stmt.annotation.annotation, cst.Name):
                                data_class_name = small_stmt.annotation.annotation.value
                        break
            if data_class_name:
                break
        
        if not data_class_name:
            return node

        typedict_name = data_class_name + "Type"
        
        # 构建注入的代码块
        # if TYPE_CHECKING:
        #     _data_class: ClassVar[type[MessageTextData]]
        #     def __init__(self, **kwargs: Unpack[MessageTextDataType]): ...
        type_checking_block = cst.If(
            test=cst.Name("TYPE_CHECKING"),
            body=cst.IndentedBlock(
                body=[
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
        
        # 追加到类体末尾
        return node.with_changes(
            body=node.body.with_changes(body=list(node.body.body) + [type_checking_block])
        )


# --- 核心流程函数 ---

def load_config_paths() -> tuple[Path, Path]:
    with open(PYPROJECT_PATH, "rb") as f:
        pyproject = tomllib.load(f)
    
    profiles = pyproject["tool"]["datamodel-codegen"]["profiles"]
    return (
        Path(profiles["message-typedict"]["output"]),
        Path(profiles["message-dataclass"]["output"])
    )

def run_codegen_tools():
    print("Running extract-message-schema.ts...")
    subprocess.run(["bun", "scripts/extract-message-schema.ts"], check=True)
    
    print("Running datamodel-codegen (typedict)...")
    subprocess.run(["uv", "run", "datamodel-codegen", "--profile", "message-typedict"], check=True)
    
    print("Running datamodel-codegen (dataclass)...")
    subprocess.run(["uv", "run", "datamodel-codegen", "--profile", "message-dataclass"], check=True)

def process_typedicts(file_path: Path) -> tuple[str, set[str]]:
    content = file_path.read_text(encoding="utf-8")
    
    # 1. 正则预处理
    for pattern, replacement in REGEX_REPLACEMENTS:
        if "TypedDict" in pattern or "float" in pattern or "TYPE_CHECKING" in replacement or "closed" in pattern:
            content = re.sub(pattern, replacement, content)
    # 2. CST 处理
    module = cst.parse_module(content)
    transformer = TypedDictTransformer()
    modified_module = module.visit(transformer)
    content = modified_module.code
    
    # 3. 字符串后处理 (Pending Renames)
    for name in transformer.renamed_classes:
        # 替换类似 MessageTextData( 为 MessageTextDataType(
        content = content.replace(f"{name}(", f"{name}Type(")
        
    return content, transformer.renamed_classes

def process_dataclasses(file_path: Path) -> str:
    content = file_path.read_text(encoding="utf-8")
    
    # 1. 正则预处理
    # 统一替换 dataclass 装饰器参数 (不包含 init=False，这部分现在由 AST 处理)
    content = content.replace("@dataclass", "@dataclass(slots=True, frozen=True, kw_only=True)")
    
    for pattern, replacement in REGEX_REPLACEMENTS:
        if "future" in pattern or "float" in pattern: # 只应用部分规则
            content = re.sub(pattern, replacement, content)

    # 2. CST 处理 (包含基类修改、Inject TypeChecking 和 添加 init=False)
    module = cst.parse_module(content)
    transformer = DataclassTransformer()
    modified_module = module.visit(transformer)
    
    return modified_module.code

def generate_init_file(content: str):
    """生成 messages/__init__.py"""
    init_file = PROJECT_ROOT / "src/napcat/types/messages/__init__.py"
    
    # 1. 提取所有继承自 MessageSegment 的类名
    # 匹配模式: class ClassName(MessageSegment):
    classes = re.findall(r"class\s+(\w+)\(MessageSegment\):", content)
    
    # 2. 提取关键的类型别名 (MessageData, Model)
    # 匹配模式: type MessageData = ...
    types = re.findall(r"^type\s+(MessageData|Model)\s+=", content, re.MULTILINE)
    
    # 合并并排序，去重
    generated_exports = sorted(list(set(classes + types)))
    
    # 3. 构建文件内容
    lines = [
        "from .base import MessageSegment, UnknownMessageSegment",
        "from .generated import (",
    ]
    
    # 添加 from .generated import ...
    for name in generated_exports:
        lines.append(f"    {name},")
    lines.append(")")
    
    lines.append("")
    
    # 添加 __all__
    lines.append("__all__ = [")
    lines.append('    "MessageSegment",')
    lines.append('    "UnknownMessageSegment",')
    for name in generated_exports:
        lines.append(f'    "{name}",')
    lines.append("]")
    
    # 4. 写入文件
    init_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Successfully generated: {init_file}")

def main():
    try:
        # 1. 准备路径和运行生成器
        typedict_path, dataclass_path = load_config_paths()
        run_codegen_tools()
        
        # 2. 处理代码
        print("Processing TypedDicts...")
        typedict_code, _ = process_typedicts(typedict_path)
        
        print("Processing Dataclasses...")
        dataclass_code = process_dataclasses(dataclass_path)
        
        # 3. 合并与清理
        final_content = typedict_code + "\n\n" + dataclass_code
        final_content = final_content.replace("OB11", "")
        
        # 4. 写入最终文件
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_text(final_content, encoding="utf-8")
        print(f"Successfully generated: {OUTPUT_FILE}")

        # --- 新增：生成 __init__.py ---
        print("Generating __init__.py...")
        generate_init_file(final_content)
        # ---------------------------
        
        # 5. 清理临时文件
        typedict_path.unlink(missing_ok=True)
        dataclass_path.unlink(missing_ok=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Error during codegen execution: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    main()