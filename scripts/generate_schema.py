import subprocess
import re
import tomllib
import json

def snake_to_classname(s: str) -> str:
    parts = s.split('_')
    return ''.join(word[0].upper() + word[1:] for word in parts if word)

with open("pyproject.toml", "rb") as f:
    pyproject = tomllib.load(f)

api_schema_code_path = pyproject["tool"]["datamodel-codegen"]["profiles"]["api-typedict"]["output"]
api_schema_path = pyproject["tool"]["datamodel-codegen"]["profiles"]["api-typedict"]["input"]

subprocess.run(["uv", "run", "datamodel-codegen", "--profile", "api-typedict"], check=True)

with open(api_schema_code_path, "r") as f:
    content = f.read()

pattern = r"(?m)^\s*from\s+typing_extensions\s+import\s+(?:\(\s*)?TypedDict(?:\s*,?\s*)?(?:\)\s*)?.*?\n?"

content = re.sub(pattern, "\n", content)

with open(api_schema_path, "r") as f:
    api_schema = json.load(f)

for endpoint in api_schema["paths"].values():
    method = endpoint.get("post", {})
    operation_id = method.get("operationId", "")
    RequestClassName = snake_to_classname(operation_id) + "PostRequest"
    ResponseClassName = snake_to_classname(operation_id) + "PostResponse"
    if not method["requestBody"]["content"]["application/json"]["schema"]:
        content += f"\n\nclass {RequestClassName}(TypedDict):\n    pass\n"
        continue
    if not method["responses"]["200"]["content"]["application/json"]["schema"]:
        content += f"\n\ntype {ResponseClassName} = Any\n"
        continue
    if method["responses"]["200"]["content"]["application/json"]["schema"].get("type", "") == "null":
        content += f"\n\ntype {ResponseClassName} = None\n"
        continue

    

with open(api_schema_code_path, "w") as f:
    f.write(content)
