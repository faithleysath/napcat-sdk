from __future__ import annotations

from napcat.cli.doc.models import (
    ApiDetailItem,
    ApiIndexItem,
    CodeFileItem,
    DocProblem,
    OperationResult,
)
from napcat.cli.doc.render import (
    render_api_details_text,
    render_api_index_text,
    render_code_files_text,
    render_json_result,
)


def test_render_json_result_serializes_nested_problems() -> None:
    result = OperationResult(
        ok=False,
        items=(
            ApiDetailItem(
                name="missing_api",
                found=False,
                signature=None,
                description=None,
                response_type=None,
                problems=(
                    DocProblem(
                        kind="not_found",
                        message="API not found: missing_api",
                        target="missing_api",
                    ),
                ),
            ),
        ),
        problems=(
            DocProblem(kind="internal", message="lookup failed", target=None),
        ),
    )

    payload = render_json_result(result)

    assert payload["ok"] is False
    assert payload["problems"][0]["message"] == "lookup failed"
    assert payload["items"][0]["problems"][0]["kind"] == "not_found"


def test_render_code_files_text_wraps_real_source_content() -> None:
    result = OperationResult(
        ok=True,
        items=(
            CodeFileItem(
                path="client_api.py",
                found=True,
                content="class NapCatAPIMixin:\n    pass",
            ),
        ),
    )

    text = render_code_files_text(result)

    assert text.startswith("# client_api.py")
    assert "```python" in text
    assert "class NapCatAPIMixin" in text


def test_render_text_uses_top_level_problems_when_present() -> None:
    result: OperationResult[ApiIndexItem] = OperationResult(
        ok=False,
        items=(),
        problems=(
            DocProblem(kind="internal", message="unexpected failure", target=None),
        ),
    )

    text = render_api_index_text(result)

    assert text == "# Error\n\nunexpected failure"


def test_render_api_details_text_marks_missing_items() -> None:
    result = OperationResult(
        ok=False,
        items=(
            ApiDetailItem(
                name="missing_api",
                found=False,
                signature=None,
                description=None,
                response_type=None,
            ),
        ),
    )

    text = render_api_details_text(result)

    assert text == "## missing_api\n(API not found)"
