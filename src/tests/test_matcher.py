from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

import pytest

from napcat.matcher import FALSE, TRUE, event_match
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


def test_event_match_predicates_support_or_composition() -> None:
    event = make_group_event(raw_message="hello", user_id=42, group_id=99)
    pred1 = event_match(GroupMessageEvent, raw_message="hello")
    pred2 = event_match(GroupMessageEvent, user_id=0)
    matcher = pred1 | pred2

    assert matcher(event) is True


def test_event_match_predicates_support_and_composition_with_lambda() -> None:
    event = make_group_event(raw_message="hello", user_id=42, group_id=99)
    pred1 = event_match(GroupMessageEvent, group_id=99)

    def has_expected_text(current: NapCatEvent) -> bool:
        return isinstance(current, GroupMessageEvent) and current.raw_message == "hello"

    matcher = pred1 & has_expected_text

    assert matcher(event) is True


def test_true_constant_enables_composition_for_plain_functions() -> None:
    event = make_group_event(raw_message="hello", user_id=42, group_id=99)

    def has_expected_text(current: NapCatEvent) -> bool:
        return isinstance(current, GroupMessageEvent) and current.raw_message == "hello"

    def has_expected_user(current: NapCatEvent) -> bool:
        return isinstance(current, GroupMessageEvent) and current.user_id == 42

    matcher = TRUE & has_expected_text & has_expected_user

    assert matcher(event) is True


def test_false_constant_enables_or_chaining_for_plain_functions() -> None:
    event = make_group_event(raw_message="hello", user_id=42, group_id=99)

    def impossible(_: NapCatEvent) -> bool:
        return False

    def has_expected_group(current: NapCatEvent) -> bool:
        return isinstance(current, GroupMessageEvent) and current.group_id == 99

    matcher = FALSE | impossible | has_expected_group

    assert matcher(event) is True


def test_event_match_rejects_tuple_event_types() -> None:
    with pytest.raises(TypeError, match=r"use `A \| B` instead"):
        event_match(cast(Any, (GroupMessageEvent, PrivateMessageEvent)))
