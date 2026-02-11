"""
类型辅助工具

提供用于处理 Dataclass 和 TypedDict 的辅助函数和 Mixin 类。
FromDictMixin 用于安全地将字典转换为 Dataclass 实例，忽略多余字段。
"""

from __future__ import annotations

import logging
from dataclasses import MISSING, fields, is_dataclass
from typing import Any, ClassVar

logger = logging.getLogger("napcat.from_dict")


def get_dataclass_field_default(
    cls: type[Any],
    field_name: str,
    *,
    declared_only: bool = False,
) -> Any | None:
    """Read a dataclass field default value in a slots-safe way.

    Returns ``None`` when:
    - ``cls`` is not a dataclass class
    - field does not exist
    - field has no default value

    Args:
        declared_only: When ``True``, only read fields declared on ``cls`` itself
            (exclude inherited dataclass fields).
    """

    if not is_dataclass(cls):
        return None

    own_annotations = cls.__dict__.get("__annotations__", {})

    for field in fields(cls):
        if field.name != field_name:
            continue

        if declared_only and field.name not in own_annotations:
            return None

        if field.default is not MISSING:
            return field.default

        return None

    return None


class FromDictMixin:
    """Safe dataclass constructor with cached field names.

    - Drops unknown keys to avoid ``unexpected keyword`` errors.
    - Logs dropped keys with warning level.
    - Caches init-field names per class to reduce runtime overhead.
    """

    _field_cache: ClassVar[dict[type[Any], frozenset[str]]] = {}

    @classmethod
    def _cached_field_names(cls) -> frozenset[str]:
        cached = FromDictMixin._field_cache.get(cls)
        if cached is not None:
            return cached

        if not is_dataclass(cls):
            raise TypeError(f"{cls.__name__} is not a dataclass")

        allowed = frozenset(f.name for f in fields(cls) if f.init)
        FromDictMixin._field_cache[cls] = allowed
        return allowed

    @classmethod
    def _from_dict(cls, data: dict[str, Any]):
        allowed = cls._cached_field_names()
        extra_keys = set(data.keys()) - set(allowed)
        if extra_keys:
            logger.warning(
                "Extra fields dropped for %s: %s",
                cls.__name__,
                sorted(extra_keys),
            )

        payload = {k: v for k, v in data.items() if k in allowed}
        return cls(**payload)
