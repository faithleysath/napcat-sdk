import subprocess
import re
import tomllib
import json
from typing import Any

def snake_to_classname(s: str) -> str:
    if s.startswith("_"):
        s = "field" + s
    if s.startswith("."):
        s = "field_" + s[1:]
    parts = s.split('_')
    return ''.join(word[0].upper() + word[1:] for word in parts if word)

with open("pyproject.toml", "rb") as f:
    pyproject = tomllib.load(f)

api_schema_code_path = pyproject["tool"]["datamodel-codegen"]["profiles"]["api-typedict"]["output"]
api_schema_path = pyproject["tool"]["datamodel-codegen"]["profiles"]["api-typedict"]["input"]

subprocess.run(["bun", "scripts/extract-api-schema.ts"], check=True)
subprocess.run(["uv", "run", "datamodel-codegen", "--profile", "api-typedict"], check=True)

with open(api_schema_code_path, "r", encoding="utf-8") as f:
    content = f.read()

pattern = r"(?m)^\s*from\s+typing_extensions\s+import\s+(?:\(\s*)?TypedDict(?:\s*,?\s*)?(?:\)\s*)?.*?\n?"

content = re.sub(pattern, "\n", content)

content = content.replace("float", "int")

with open(api_schema_path, "r", encoding="utf-8") as f:
    api_schema = json.load(f)

apifox_schema: dict[str, Any] = {}
try:
    with open("schemas/apifox.openapi.json", "r", encoding="utf-8") as f:
        apifox_schema = json.load(f)
except FileNotFoundError:
    pass

docstring_map = {
    path.lstrip("/"): f'        """\n        {data.get("post", {}).get("summary", "")}\n\n        标签: {(data.get("post", {}).get("tags") or [""])[0]}\n        """'
    for path, data in apifox_schema.get("paths", {}).items()
}

typemap = {
    "string": "str",
    "integer": "int",
    "number": "float",
    "boolean": "bool",
    "null": "None",
}

client_api_code = """# Auto-generated file. Do not modify directly.
# 自动生成的文件。请勿直接修改。

from collections.abc import Mapping
from typing import Any, Unpack, Protocol
from .types.schemas import (
"""

api_func_code = ""

for endpoint in api_schema["paths"].values():
    method = endpoint.get("post", {})
    operation_id = method.get("operationId", "")
    RequestClassName = snake_to_classname(operation_id) + "PostRequest"
    ResponseClassName = snake_to_classname(operation_id) + "PostResponse"
    requestSchema = method["requestBody"]["content"]["application/json"]["schema"]
    is_union_request = "oneOf" in requestSchema or "anyOf" in requestSchema

    if not requestSchema:
        client_api_code += f"   {ResponseClassName},\n"
    else:
        client_api_code += f"   {RequestClassName},\n   {ResponseClassName},\n"

    doc_str = docstring_map.get(operation_id, '        \"\"\"\n        未提供描述\n        \"\"\"')
    # 3. 自适应生成函数签名
    if is_union_request:
        # 【模式 A】Payload 模式 (针对 Union 类型)
        # 函数签名: def func(self, payload: UnionType)
        api_func_code += f"""
    async def {operation_id.replace('.', 'dot_')}(self, payload: {RequestClassName}) -> {ResponseClassName}:
{doc_str}
        return await self._client.call_action("{operation_id}", payload)
    """
    elif requestSchema:
        # 【模式 B】Unpack kwargs 模式 (针对普通 TypedDict)
        # 函数签名: def func(self, **kwargs: Unpack[Type])
        api_func_code += f"""
    async def {operation_id.replace('.', 'dot_')}(self, **kwargs: Unpack[{RequestClassName}]) -> {ResponseClassName}:
{doc_str}
        return await self._client.call_action("{operation_id}", kwargs)
    """
    else:
        # 【模式 C】无参数模式
        # 函数签名: def func(self)
        api_func_code += f"""
    async def {operation_id.replace('.', 'dot_')}(self, **kwargs: Any) -> {ResponseClassName}:
{doc_str}
        return await self._client.call_action("{operation_id}", kwargs)
    """
    responseSchema = method["responses"]["200"]["content"]["application/json"]["schema"]
    if not responseSchema:
        content += f"\n\ntype {ResponseClassName} = Any\n"
        continue
    if responseSchema.get("type", "") in typemap:
        content += f"\n\ntype {ResponseClassName} = {typemap[responseSchema['type']]}\n"
        continue

client_api_code += f""")
# 定义一个 Protocol，避免循环导入 Client 类，同时保证类型提示
class CallActionProtocol(Protocol):
    async def call_action(self, action: str, params: Mapping[str, Any] | None = None) -> Any: ...

class NapCatAPI:
    \"\"\"
    NapCat API 命名空间。
    所有自动生成的方法都挂载于此，通过 client.api.xxx 调用。
    \"\"\"

    def __init__(self, client: CallActionProtocol):
        self._client = client

{api_func_code}
"""

with open(api_schema_code_path, "w", encoding="utf-8") as f:
    f.write(content)

with open("src/napcat/client_api.py", "w", encoding="utf-8") as f:
    f.write(client_api_code)