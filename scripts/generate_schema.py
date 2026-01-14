import subprocess

subprocess.run(["uv", "run", "datamodel-codegen"], check=True)

with open("src/napcat/types/schemas.py", "r") as f:
    content = f.read()

content = content.replace("type Number207C20string = float | str", "")

content = content.replace("Number207C20string", "float | str")

with open("src/napcat/types/schemas.py", "w") as f:
    f.write(content)

subprocess.run(["uv", "run", "scripts/generate_client_api.py"], check=True)