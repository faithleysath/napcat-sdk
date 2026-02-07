from __future__ import annotations

import logging
from dataclasses import fields, is_dataclass
from typing import Any, ClassVar

logger = logging.getLogger("napcat.from_dict")


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
