"""
Shared input normalization helpers for doc operations.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import cast


def normalize_string_values(
    values: object,
    *,
    invalid_container_message: str,
    empty_message: str,
    invalid_item_message: str,
    allow_single_string: bool = False,
) -> tuple[str, ...]:
    """Normalize a string container into a stripped tuple of values."""

    if allow_single_string and isinstance(values, str):
        raw_values: list[object] = [values]
    elif isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise ValueError(invalid_container_message)
    else:
        raw_values = list(cast(Sequence[object], values))

    if not raw_values:
        raise ValueError(empty_message)

    normalized_values: list[str] = []
    for value in raw_values:
        if not isinstance(value, str):
            raise ValueError(invalid_item_message)

        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError(invalid_item_message)

        normalized_values.append(stripped_value)

    return tuple(normalized_values)
