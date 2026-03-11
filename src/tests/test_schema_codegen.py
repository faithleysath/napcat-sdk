from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def _load_schema_codegen_module() -> ModuleType:
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "schema-codegen.py"
    spec = importlib.util.spec_from_file_location("test_schema_codegen", script_path)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_collect_paths_for_ruff_formatting_skips_missing_optional_outputs(
    tmp_path: Path,
) -> None:
    schema_codegen = _load_schema_codegen_module()

    generated = tmp_path / "generated.py"
    schemas = tmp_path / "schemas.py"
    messages_init = tmp_path / "messages_init.py"
    events_init = tmp_path / "events_init.py"
    types_init = tmp_path / "types_init.py"
    client_api = tmp_path / "client_api.py"
    matcher_stub = tmp_path / "matcher.pyi"

    cfg = schema_codegen.CodegenConfig(
        generated_output_path=str(generated),
        schemas_output_path=str(schemas),
        messages_init_output_path=str(messages_init),
        events_init_output_path=str(events_init),
        types_init_output_path=str(types_init),
        client_api_output_path=str(client_api),
        matcher_stub_output_path=str(matcher_stub),
        run_client_api_codegen_after_pipeline=False,
        run_matcher_stub_codegen_after_pipeline=False,
    )

    assert schema_codegen._collect_paths_for_ruff_formatting(cfg) == [
        str(generated),
        str(schemas),
        str(messages_init),
        str(events_init),
        str(types_init),
    ]


def test_collect_paths_for_ruff_formatting_keeps_existing_optional_outputs(
    tmp_path: Path,
) -> None:
    schema_codegen = _load_schema_codegen_module()

    generated = tmp_path / "generated.py"
    schemas = tmp_path / "schemas.py"
    messages_init = tmp_path / "messages_init.py"
    events_init = tmp_path / "events_init.py"
    types_init = tmp_path / "types_init.py"
    client_api = tmp_path / "client_api.py"
    matcher_stub = tmp_path / "matcher.pyi"

    client_api.write_text("# generated\n", encoding="utf-8")
    matcher_stub.write_text("# generated\n", encoding="utf-8")

    cfg = schema_codegen.CodegenConfig(
        generated_output_path=str(generated),
        schemas_output_path=str(schemas),
        messages_init_output_path=str(messages_init),
        events_init_output_path=str(events_init),
        types_init_output_path=str(types_init),
        client_api_output_path=str(client_api),
        matcher_stub_output_path=str(matcher_stub),
        run_client_api_codegen_after_pipeline=False,
        run_matcher_stub_codegen_after_pipeline=False,
    )

    assert schema_codegen._collect_paths_for_ruff_formatting(cfg) == [
        str(generated),
        str(schemas),
        str(messages_init),
        str(events_init),
        str(types_init),
        str(client_api),
        str(matcher_stub),
    ]
