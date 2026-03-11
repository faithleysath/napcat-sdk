from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

import pytest

from napcat.matcher import event_match
from napcat.types import (
    GroupMessageEvent,
    MessageSender,
    NapCatEvent,
    PrivateMessageEvent,
    Text,
)
from napcat.types.events.base import UnknownEvent


def make_group_event(
    *,
    raw_message: str = "12",
    user_id: int = 123,
    group_id: int = 456,
    role: str | None = "admin",
) -> GroupMessageEvent:
    return GroupMessageEvent(
        time=1,
        self_id=10000,
        post_type="message",
        message_id=10,
        user_id=user_id,
        message_seq=11,
        real_id=12,
        sender=MessageSender(user_id=user_id, nickname="alice", role=role),
        raw_message=raw_message,
        message=(Text(text=raw_message),),
        group_id=group_id,
    )


def test_event_match_matches_top_level_scalar_fields() -> None:
    event = make_group_event(raw_message="hello", user_id=42, group_id=99)
    matcher = event_match(GroupMessageEvent, user_id=42, group_id=99)

    assert matcher(event) is True


def test_event_match_supports_nested_dataclass_mapping() -> None:
    event = make_group_event()
    matcher = event_match(
        GroupMessageEvent,
        sender={
            "role": "admin",
            "nickname": lambda value: value.startswith("ali"),
        },
    )

    assert matcher(event) is True


def test_event_match_supports_nested_mapping_fields() -> None:
    event = UnknownEvent(
        time=1,
        self_id=10000,
        post_type="unknown",
        raw_data={
            "notice_type": "custom",
            "sender": {"role": "admin", "nickname": "alice"},
        },
    )
    matcher = event_match(
        UnknownEvent,
        raw_data={"sender": {"role": "admin"}},
    )

    assert matcher(event) is True


def test_event_match_supports_callable_message_patterns() -> None:
    event = make_group_event(raw_message="12")
    matcher = event_match(
        GroupMessageEvent,
        message=lambda segments: (
            len(segments) == 1
            and isinstance(segments[0], Text)
            and segments[0].text.isdigit()
        ),
    )

    assert matcher(event) is True


def test_event_match_returns_false_for_missing_field() -> None:
    event = make_group_event()
    pattern: dict[str, Any] = {"does_not_exist": 1}
    matcher: Callable[[NapCatEvent], bool] = event_match(GroupMessageEvent, **pattern)

    assert matcher(event) is False


def test_event_match_supports_multiple_event_types() -> None:
    event = PrivateMessageEvent(
        time=1,
        self_id=10000,
        post_type="message",
        message_id=10,
        user_id=123,
        message_seq=11,
        real_id=12,
        sender=MessageSender(user_id=123, nickname="alice"),
        raw_message="ping",
        message=(Text(text="ping"),),
    )
    matcher: Callable[[NapCatEvent], bool] = event_match(
        GroupMessageEvent | PrivateMessageEvent,
        user_id=123,
        raw_message="ping",
    )

    assert matcher(event) is True


def test_event_match_rejects_tuple_event_types() -> None:
    with pytest.raises(TypeError, match=r"use `A \| B` instead"):
        event_match(cast(Any, (GroupMessageEvent, PrivateMessageEvent)))
