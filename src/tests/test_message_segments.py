from __future__ import annotations

from typing import Any

import pytest

from napcat.types.messages import (
    At,
    Face,
    IdMusic,
    Image,
    Json,
    MessageSegment,
    Reply,
    Text,
    UnknownMessageSegment,
)


@pytest.mark.parametrize(
    ("raw", "expected_cls", "field", "expected_value"),
    [
        ({"type": "text", "data": {"text": "hello", "extra": "ignored"}}, Text, "text", "hello"),
        ({"type": "at", "data": {"qq": "all", "name": "全体成员"}}, At, "qq", "all"),
        ({"type": "reply", "data": {"seq": 1001}}, Reply, "seq", 1001),
        ({"type": "face", "data": {"id": "14"}}, Face, "id", "14"),
        ({"type": "image", "data": {"file": "https://a.b/c.png"}}, Image, "file", "https://a.b/c.png"),
        ({"type": "json", "data": {"data": {"k": "v"}}}, Json, "data", {"k": "v"}),
    ],
)
def test_message_segment_from_dict_known_types(
    raw: dict[str, Any],
    expected_cls: type[Any],
    field: str,
    expected_value: Any,
) -> None:
    seg = MessageSegment.from_dict(raw)

    assert isinstance(seg, expected_cls)
    assert getattr(seg, field) == expected_value


def test_message_segment_music_route_to_id_music() -> None:
    raw = {"type": "music", "data": {"type": "qq", "id": 12345}}

    seg = MessageSegment.from_dict(raw)

    assert isinstance(seg, IdMusic)
    assert seg.type == "qq"
    assert seg.id == 12345


def test_message_segment_unknown_type_fallback() -> None:
    raw = {"type": "unknown_x", "data": {"foo": "bar"}}

    seg = MessageSegment.from_dict(raw)

    assert isinstance(seg, UnknownMessageSegment)
    assert seg.raw_type == "unknown_x"
    assert seg.raw_data == {"foo": "bar"}


def test_message_segment_invalid_data_payload_fallback() -> None:
    raw = {"type": "text", "data": ["not", "a", "dict"]}

    seg = MessageSegment.from_dict(raw)

    assert isinstance(seg, UnknownMessageSegment)
    assert seg.raw_type == "text"
    assert seg.raw_data == ["not", "a", "dict"]


def test_message_segment_missing_required_field_raises() -> None:
    raw: dict[str, Any] = {"type": "text", "data": {}}

    with pytest.raises(TypeError):
        MessageSegment.from_dict(raw)


def test_message_segment_iter_for_known_segment() -> None:
    seg = Text(text="iter-check")

    assert dict(seg) == {
        "type": "text",
        "data": {"text": "iter-check"},
    }


def test_message_segment_iter_for_unknown_segment() -> None:
    seg = UnknownMessageSegment(raw_type="mystery", raw_data={"x": 1})

    assert dict(seg) == {
        "type": "mystery",
        "data": {"x": 1},
    }
