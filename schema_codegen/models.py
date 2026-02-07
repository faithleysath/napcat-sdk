from dataclasses import dataclass


@dataclass(frozen=True)
class CodegenConfig:
    typedict_input_path: str = "api_typedict.py"
    dataclass_input_path: str = "api_dataclass.py"
    generated_output_path: str = "src/napcat/types/messages/generated.py"
    schemas_output_path: str = "src/napcat/types/schemas.py"
