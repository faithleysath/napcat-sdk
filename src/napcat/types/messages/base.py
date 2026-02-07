from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, ClassVar, cast
from collections.abc import Iterator


class MessageSegment(ABC):
    _registry: ClassVar[dict[str, type[MessageSegment]]] = {}
    _type: ClassVar[str]
    _valid_fields: ClassVar[set[str]]
    __segment_register__: ClassVar[bool]

    def __init_subclass__(cls, register: bool = True, **kwargs: Any):
        super().__init_subclass__(**kwargs)

        # Persist the explicit `register=` decision across potential class
        # recreation by @dataclass(slots=True, ...).
        saved_register = cls.__dict__.get("__segment_register__")
        if saved_register is None:
            cls.__segment_register__ = register
            effective_register = register
        else:
            effective_register = bool(saved_register)

        if not is_dataclass(cls):
            # NOTE:
            # dataclass(slots=True, ...) may recreate the class object, causing
            # __init_subclass__ to be called once before @dataclass is applied.
            # Skip that early phase and let the dataclass-processed class handle
            # registration and field cache initialization.
            return
        
        cls._valid_fields = {
            f.name for f in fields(cls) 
            if not f.name.startswith("_")
        }

        if not effective_register:
            return

        if ABC in cls.__bases__:
            return

        if hasattr(cls, "_type"):
            if cls._type in MessageSegment._registry:
                raise ValueError(f"Duplicate segment type registered: '{cls._type}' by {cls.__name__}")
            MessageSegment._registry[cls._type] = cls
            return
        
        raise TypeError(f"Class {cls.__name__} must define '_type' ClassVar or inherit from ABC.")

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> MessageSegment:
        seg_type = raw.get("type", "unknown")
        data_payload = raw.get("data", {})

        target_cls = MessageSegment._registry.get(seg_type)

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