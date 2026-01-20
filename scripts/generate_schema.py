import subprocess
import re
import tomllib

with open("pyproject.toml", "rb") as f:
    pyproject = tomllib.load(f)

api_schema_path = pyproject["tool"]["datamodel-codegen"]["profiles"]["api-typedict"]["output"]

subprocess.run(["uv", "run", "datamodel-codegen", "--profile", "api-typedict"], check=True)

with open(api_schema_path, "r") as f:
    content = f.read()

pattern = r"(?m)^\s*from\s+typing_extensions\s+import\s+(?:\(\s*)?TypedDict(?:\s*,?\s*)?(?:\)\s*)?.*?\n?"

content = re.sub(pattern, "\n", content)



with open(api_schema_path, "w") as f:
    f.write(content)
