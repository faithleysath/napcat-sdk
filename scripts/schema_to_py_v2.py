import json
import re
from urllib.parse import unquote

# 占位符：实际使用时请替换为你的数据加载逻辑
def load_data():
    pass 

class SchemaGenerator:
    def __init__(self, schemas):
        self.schemas = schemas.copy()
        
        # 1. 全局类名映射表：Original Key -> Valid Python Identifier
        self.class_map = {}
        
        # 2. 待处理队列：存放 (NewClassName, SchemaDict)
        self.queue = []
        self.processed_names = set()
        
        # 3. 初始化：预处理顶层 Key，建立映射
        self._init_top_level_mapping()

    def _clean_name(self, name):
        """
        核心清洗逻辑：将任意字符串转换为合法的 Python 标识符
        """
        name = unquote(name) # 解码 URL
        
        # --- 特殊硬编码规则 ---
        if name == "number | string":
            return "NumberOrString"
        
        # --- 通用规则 ---
        # 1. 处理数组后缀 [] -> List
        if name.endswith("[]"):
            name = name[:-2] + "List"
        
        # 2. 替换非法符号
        name = name.replace("|", "Or")
        name = name.replace(" ", "")
        name = name.replace("-", "_").replace(".", "_")
        
        # 3. 移除非单词字符（保留中文、字母、数字、下划线）
        # Python 3 允许中文作为标识符
        name = re.sub(r'[^\w\u4e00-\u9fa5]', '', name)
        
        # 4. 如果开头是数字，加前缀
        if name and name[0].isdigit():
            name = f"Type_{name}"
            
        return name

    def _init_top_level_mapping(self):
        """预扫描所有顶层 Key，生成合法的 Python 变量名"""
        for original_name, schema in self.schemas.items():
            safe_name = self._clean_name(original_name)
            self.class_map[original_name] = safe_name
            # 将清洗后的名字和对应的 schema 加入处理队列
            self.queue.append((safe_name, schema))
            self.processed_names.add(safe_name)

    def _get_ref_name(self, ref):
        """解析 $ref 并返回清洗后的名字"""
        # ref 格式通常是 "#/components/schemas/Name"
        original_name = ref.split('/')[-1]
        original_name = unquote(original_name)
        
        # 如果这个 Ref 指向的名字我们在顶层映射里有，直接用
        if original_name in self.class_map:
            return self.class_map[original_name]
        
        # 如果没有（极少情况），临时清洗一下
        return self._clean_name(original_name)

    def _register_nested_class(self, parent_name, field_name, schema):
        """注册嵌套类，返回新生成的类名"""
        # 组合新名字：Parent_field
        clean_field = self._clean_name(field_name)
        new_class_name = f"{parent_name}_{clean_field}"
        
        # 避免重复处理
        if new_class_name not in self.processed_names:
            self.queue.append((new_class_name, schema))
            self.processed_names.add(new_class_name)
            
        return new_class_name

    def _parse_type(self, schema, current_class_name="", field_context=""):
        """递归解析类型字符串"""
        if "$ref" in schema:
            return self._get_ref_name(schema["$ref"])
        
        # 处理 Union (oneOf, anyOf)
        if "oneOf" in schema or "anyOf" in schema:
            options = schema.get("oneOf", []) + schema.get("anyOf", [])
            types = []
            for i, opt in enumerate(options):
                # 为联合类型里的匿名对象生成唯一后缀
                suffix = f"{field_context}_{i}" if field_context else f"Union_{i}"
                types.append(self._parse_type(opt, current_class_name, suffix))
            
            unique_types = sorted(list(set(types)), key=lambda x: str(x))
            return " | ".join(unique_types)

        if "const" in schema:
            return f"Literal[{repr(schema['const'])}]"

        if "enum" in schema:
            # 过滤非法 enum
            enums = [repr(e) for e in schema['enum']]
            return f"Literal[{', '.join(enums)}]"

        schema_type = schema.get("type")

        # === 对象类型：提取为新类 ===
        if schema_type == "object":
            if "properties" in schema:
                # 只有当它是 properties 定义时才提取，否则只是 dict
                return self._register_nested_class(current_class_name, field_context, schema)
            return "dict[str, Any]"

        # === 数组类型 ===
        if schema_type == "array":
            items = schema.get("items", {})
            item_type = self._parse_type(items, current_class_name, field_context)
            return f"list[{item_type}]"

        # === 基础类型 ===
        if schema_type == "string":
            return "str"
        if schema_type in ["number", "integer"]:
            return "float" if schema_type == "number" else "int"
        if schema_type == "boolean":
            return "bool"

        return "Any"

    def generate(self):
        lines = []
        lines.append("from __future__ import annotations")
        lines.append("from typing import TypedDict, Literal, NotRequired, Any")
        lines.append("")
        
        # 使用 while 循环，因为 queue 在处理过程中会追加新元素
        idx = 0
        while idx < len(self.queue):
            class_name, schema = self.queue[idx]
            idx += 1
            
            # 判定是 TypedDict 还是 Type Alias
            is_object_def = (schema.get("type") == "object" and "properties" in schema)
            
            if is_object_def:
                # === 生成 TypedDict ===
                lines.append(f"class {class_name}(TypedDict):")
                if "description" in schema:
                    desc = schema["description"].replace("\n", " ")
                    lines.append(f'    """{desc}"""')
                
                required_fields = set(schema.get("required", []))
                properties = schema.get("properties", {})
                
                if not properties:
                    lines.append("    pass")
                
                for prop_name, prop_schema in properties.items():
                    # 递归解析，传入当前类名作为上下文
                    py_type = self._parse_type(prop_schema, class_name, prop_name)
                    
                    if prop_schema.get("nullable") is True:
                        py_type = f"{py_type} | None"
                    
                    comment = ""
                    if "description" in prop_schema:
                        desc = prop_schema["description"].replace('\n', ' ')
                        comment = f"  # {desc}"

                    # 生成字段
                    if prop_name in required_fields:
                        lines.append(f"    {prop_name}: {py_type}{comment}")
                    else:
                        lines.append(f"    {prop_name}: NotRequired[{py_type}]{comment}")
                lines.append("") 
            
            else:
                # === 生成 Type Alias (使用 Python 3.12 type 语法) ===
                # 注意：顶层别名不需要 field_context
                py_type = self._parse_type(schema, class_name, "")
                
                if schema.get("nullable") is True:
                    py_type = f"{py_type} | None"
                
                desc = schema.get("description", "")
                comment = f" # {desc}" if desc else ""
                
                # 使用 type 关键字
                lines.append(f"type {class_name} = {py_type}{comment}")
                lines.append("")

        return "\n".join(lines)

# ================= 使用入口 =================

if __name__ == "__main__":
    try:
        # 读取文件
        with open("默认模块.openapi.json", "r", encoding="utf-8") as f:
            full_json = json.load(f)
            
            # 定位到 schemas 字典
            if "components" in full_json and "schemas" in full_json["components"]:
                schemas_data = full_json["components"]["schemas"]
            elif "schemas" in full_json:
                schemas_data = full_json["schemas"]
            else:
                schemas_data = full_json

            # 生成代码
            generator = SchemaGenerator(schemas_data)
            output_code = generator.generate()
            
            # 写入文件
            with open("types_output.py", "w", encoding="utf-8") as out:
                out.write(output_code)
                
            print("✅ 代码生成成功！已使用 Python 3.12+ type 语法。")
            
    except FileNotFoundError:
        print("❌ 未找到 schema.json 文件，请将 JSON 数据保存为 schema.json 后重试。")