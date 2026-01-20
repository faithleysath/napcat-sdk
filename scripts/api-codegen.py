import subprocess
import re
import tomllib
import json

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

subprocess.run(["bun", "scripts/generate-api-schema.ts"], check=True)
subprocess.run(["uv", "run", "datamodel-codegen", "--profile", "api-typedict"], check=True)

with open(api_schema_code_path, "r") as f:
    content = f.read()

pattern = r"(?m)^\s*from\s+typing_extensions\s+import\s+(?:\(\s*)?TypedDict(?:\s*,?\s*)?(?:\)\s*)?.*?\n?"

content = re.sub(pattern, "\n", content)

with open(api_schema_path, "r") as f:
    api_schema = json.load(f)

typemap = {
    "string": "str",
    "number": "float",
    "boolean": "bool",
    "null": "None",
}

for endpoint in api_schema["paths"].values():
    method = endpoint.get("post", {})
    operation_id = method.get("operationId", "")
    RequestClassName = snake_to_classname(operation_id) + "PostRequest"
    ResponseClassName = snake_to_classname(operation_id) + "PostResponse"
    requestSchema = method["requestBody"]["content"]["application/json"]["schema"]
    if not requestSchema:
        content += f"\n\nclass {RequestClassName}(TypedDict):\n    pass\n"
    responseSchema = method["responses"]["200"]["content"]["application/json"]["schema"]
    if not responseSchema:
        content += f"\n\ntype {ResponseClassName} = Any\n"
        continue
    if responseSchema.get("type", "") in typemap:
        content += f"\n\ntype {ResponseClassName} = {typemap[responseSchema['type']]}\n"
        continue

with open(api_schema_code_path, "w") as f:
    f.write(content)
