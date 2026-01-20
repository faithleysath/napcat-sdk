import subprocess
import tomllib

with open("pyproject.toml", "rb") as f:
    pyproject = tomllib.load(f)

message_schema_code_path = pyproject["tool"]["datamodel-codegen"]["profiles"]["api-typedict"]["output"]