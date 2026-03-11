"""Helpers for building event predicates."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from types import UnionType
from typing import Any, cast, get_args

from .types import NapCatEvent

__all__ = ["FALSE", "Predicate", "TRUE", "event_match"]

_MISSING: object = object()
type EventType = type[NapCatEvent] | UnionType


class Predicate[T]:
    """Composable callable predicate."""

    __slots__ = ("_func",)

    def __init__(self, func: Callable[[T], bool]) -> None:
        self._func = func

    def __call__(self, value: T, /) -> bool:
        return bool(self._func(value))

    def __or__(self, other: PredicateLike[T], /) -> Predicate[T]:
        other_predicate = _coerce_predicate(other)
        return Predicate(lambda value: self(value) or other_predicate(value))

    def __ror__(self, other: PredicateLike[T], /) -> Predicate[T]:
        other_predicate = _coerce_predicate(other)
        return Predicate(lambda value: other_predicate(value) or self(value))

    def __and__(self, other: PredicateLike[T], /) -> Predicate[T]:
        other_predicate = _coerce_predicate(other)
        return Predicate(lambda value: self(value) and other_predicate(value))

    def __rand__(self, other: PredicateLike[T], /) -> Predicate[T]:
        other_predicate = _coerce_predicate(other)
        return Predicate(lambda value: other_predicate(value) and self(value))


type PredicateLike[T] = Callable[[T], bool] | Predicate[T]
type EventPredicate = Predicate[NapCatEvent]


def _coerce_predicate[T](predicate: PredicateLike[T]) -> Predicate[T]:
    if isinstance(predicate, Predicate):
        return cast(Predicate[T], predicate)
    return Predicate(predicate)


def _always_true(_: Any) -> bool:
    return True


def _always_false(_: Any) -> bool:
    return False


TRUE: Predicate[Any] = Predicate(_always_true)
FALSE: Predicate[Any] = Predicate(_always_false)


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

    return Predicate(_predicate)
