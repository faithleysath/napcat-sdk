from __future__ import annotations

from napcat.cli.doc.service import DocService


def test_doc_service_marks_missing_api_as_partial_failure() -> None:
    service = DocService()

    result = service.get_api_details(["__not_existing_api_for_test__"])

    assert result.ok is False
    assert len(result.items) == 1
    assert result.items[0].name == "__not_existing_api_for_test__"
    assert result.items[0].found is False
    assert result.items[0].problems[0].kind == "not_found"


def test_doc_service_rejects_invalid_code_path() -> None:
    service = DocService()

    result = service.get_code_files(["../pyproject.toml"])

    assert result.ok is False
    assert len(result.items) == 1
    assert result.items[0].found is False
    assert result.items[0].problems[0].kind == "invalid_input"


def test_doc_service_lists_code_files_with_categories() -> None:
    service = DocService()

    result = service.list_code_files()

    assert result.ok is True
    categories = {item.path: item.category for item in result.items}
    assert categories["client_api.py"] == "api-definitions"
    assert categories["types/schemas.py"] == "typed-dicts"


def test_doc_service_reads_generated_api_source_file() -> None:
    service = DocService()

    result = service.get_code_files(["client_api.py"])

    assert result.ok is True
    assert result.items[0].found is True
    assert "class NapCatAPIMixin" in (result.items[0].content or "")


def test_doc_service_normalizes_whitespace_for_direct_calls() -> None:
    service = DocService()

    api_result = service.get_api_details([" send_private_msg "])
    code_result = service.get_code_files([" client.py "])

    assert api_result.ok is True
    assert api_result.items[0].name == "send_private_msg"
    assert api_result.items[0].found is True
    assert code_result.ok is True
    assert code_result.items[0].path == "client.py"
    assert code_result.items[0].found is True


def test_doc_service_marks_missing_class_as_partial_failure() -> None:
    service = DocService()

    result = service.get_class_definitions([" __NotExistingClassForTest__ "])

    assert result.ok is False
    assert len(result.items) == 1
    assert result.items[0].name == "__NotExistingClassForTest__"
    assert result.items[0].found is False
    assert result.items[0].problems[0].kind == "not_found"
