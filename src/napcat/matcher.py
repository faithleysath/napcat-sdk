"""Helpers for building event predicates."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from types import UnionType
from typing import Any, cast, get_args

from .types import NapCatEvent

__all__ = ["event_match"]

_MISSING: object = object()
type EventType = type[NapCatEvent] | UnionType
type EventPredicate = Callable[[NapCatEvent], bool]


def _get_member(value: Any, name: str) -> Any:
    if isinstance(value, Mapping):
        mapping = cast(Mapping[object, Any], value)
        return mapping[name] if name in mapping else _MISSING
    return getattr(value, name, _MISSING)


def _match_value(actual: Any, expected: Any) -> bool:
    if callable(expected):
        predicate = cast(Callable[[Any], object], expected)
        return bool(predicate(actual))

    if isinstance(expected, Mapping):
        return _match_mapping(actual, cast(Mapping[str, Any], expected))

    return actual == expected


def _match_mapping(actual: Any, expected: Mapping[str, Any]) -> bool:
    for key, sub_expected in expected.items():
        sub_actual = _get_member(actual, key)
        if sub_actual is _MISSING:
            return False
        if not _match_value(sub_actual, sub_expected):
            return False
    return True


def _normalize_event_type(event_type: object) -> EventType:
    if isinstance(event_type, tuple):
        raise TypeError("event_type tuples are unsupported; use `A | B` instead")

    if isinstance(event_type, type):
        if issubclass(event_type, NapCatEvent):
            return event_type
        raise TypeError("event_type must be a NapCatEvent subclass or `A | B` union")

    if isinstance(event_type, UnionType):
        members = get_args(event_type)
        if members and all(
            isinstance(member, type) and issubclass(member, NapCatEvent)
            for member in members
        ):
            return event_type
        raise TypeError("event_type unions must contain only NapCatEvent subclasses")

    raise TypeError("event_type must be a NapCatEvent subclass or `A | B` union")


def event_match(
    event_type: EventType,
    /,
    **pattern: Any,
) -> EventPredicate:
    """Build a predicate that matches event type plus partial field patterns."""
    normalized_event_type = _normalize_event_type(event_type)

    def _predicate(event: NapCatEvent) -> bool:
        if not isinstance(event, normalized_event_type):
            return False

        for name, expected in pattern.items():
            actual = _get_member(event, name)
            if actual is _MISSING:
                return False
            if not _match_value(actual, expected):
                return False

        return True

    return _predicate
