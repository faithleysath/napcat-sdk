import libcst as cst

from .assemble import build_generated_message_module, build_schemas_module
from .collectors import ClassCollector
from .io import postprocess_generated_files, read_text, write_text
from .models import CodegenConfig
from .transforms_message import collect_generated_message_classes
from .transforms_typedict import FlattenedClassRemover, ResponseFlattener


def run_pipeline(config: CodegenConfig | None = None) -> None:
    config = config or CodegenConfig()

    typedict_source = read_text(config.typedict_input_path)
    dataclass_source = read_text(config.dataclass_input_path)

    typedict_module = cst.parse_module(typedict_source)
    dataclass_module = cst.parse_module(dataclass_source)

    typedict_collector = ClassCollector()
    typedict_module.visit(typedict_collector)
    dataclass_collector = ClassCollector()
    dataclass_module.visit(dataclass_collector)

    print(f"Collected {len(typedict_collector.definitions)} TypedDict classes.")
    print(f"Collected {len(dataclass_collector.definitions)} Dataclass classes.")

    typedict_flattener = ResponseFlattener(typedict_collector.definitions)
    flattened_typedict_module = typedict_module.visit(typedict_flattener)
    print(
        "Successfully flattened "
        f"{len(typedict_flattener.flattened_classes)} PostResponse classes."
    )

    typedict_remover = FlattenedClassRemover(typedict_flattener.flattened_classes)
    cleaned_typedict_module = flattened_typedict_module.visit(typedict_remover)
    print(
        "Successfully removed "
        f"{typedict_remover.removed_count} flattened class definitions."
    )

    generated_message_classes, flattened_dataclass_names = collect_generated_message_classes(
        dataclass_module,
        dataclass_collector.definitions,
    )

    generated_message_module = build_generated_message_module(
        typedict_module,
        dataclass_module,
        typedict_collector.definitions,
        generated_message_classes,
    )

    write_text(config.generated_output_path, generated_message_module.code)
    print(
        "Successfully generated "
        f"{len(generated_message_classes)} message segment classes to "
        f"{config.generated_output_path}."
    )

    schemas_module, generated_definition_names = build_schemas_module(
        cleaned_typedict_module,
        generated_message_module,
        flattened_dataclass_names,
    )

    write_text(config.schemas_output_path, schemas_module.code)
    print(
        "Successfully generated schemas module to "
        f"{config.schemas_output_path} with {len(generated_definition_names)} generated imports."
    )

    postprocess_generated_files(
        [
            config.generated_output_path,
            config.schemas_output_path,
        ]
    )
