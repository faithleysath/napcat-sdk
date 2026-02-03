from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, ClassVar, cast
from collections.abc import Iterator


class MessageSegment(ABC):
    _registry: ClassVar[dict[str, type[MessageSegment]]] = {}
    _type: ClassVar[str]
    _valid_fields: ClassVar[set[str]]

    def __init_subclass__(cls, register: bool = True, **kwargs: Any):
        super().__init_subclass__(**kwargs)

        if not is_dataclass(cls):
            raise TypeError(
                f"Class '{cls.__name__}' must be decorated with @dataclass "
                f"to inherit from {MessageSegment.__name__}."
            )
        
        cls._valid_fields = {
            f.name for f in fields(cls) 
            if not f.name.startswith("_")
        }

        if not register:
            return

        if ABC in cls.__bases__:
            return

        if hasattr(cls, "_type"):
            if cls._type in cls._registry:
                raise ValueError(f"Duplicate segment type registered: '{cls._type}' by {cls.__name__}")
            cls._registry[cls._type] = cls
            return
        
        raise TypeError(f"Class {cls.__name__} must define '_type' ClassVar or inherit from ABC.")

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> MessageSegment:
        seg_type = raw.get("type", "unknown")
        data_payload = raw.get("data", {})

        target_cls = cls._registry.get(seg_type)

        if target_cls:
            if isinstance(data_payload, dict):
                filtered_data: dict[str, Any] = {
                    k: v for k, v in cast(dict[str, Any], data_payload).items()
                    if k in target_cls._valid_fields
                }
                return target_cls(**filtered_data)
            return target_cls()
        
        return UnknownMessageSegment(raw_type=seg_type, raw_data=data_payload)
    
    def __iter__(self) -> Iterator[tuple[str, str | dict[str, Any]]]:
        yield "type", self._type
        yield "data", { name: getattr(self, name) for name in self._valid_fields }


@dataclass(slots=True, frozen=True, kw_only=True)
class UnknownMessageSegment(MessageSegment, register=False):
    """表示未知的消息段"""

    _type: ClassVar[str] = "unknown"

    raw_type: str
    raw_data: dict[str, Any]

    def __iter__(self) -> Iterator[tuple[str, str | dict[str, Any]]]:
        yield "type", self.raw_type
        yield "data", self.raw_data