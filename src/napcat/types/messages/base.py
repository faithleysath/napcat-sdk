from __future__ import annotations
import builtins
from abc import ABC
from dataclasses import dataclass
from typing import (
    Any,
    ClassVar,
    LiteralString,
    TypedDict,
    Unpack,
    cast,
    get_type_hints,
)

from ..utils import IgnoreExtraArgsMixin, TypeValidatorMixin

@dataclass(slots=True, frozen=True, kw_only=True)
class SegmentDataBase(TypeValidatorMixin, IgnoreExtraArgsMixin):
    pass


class SegmentDataTypeBase(TypedDict):
    pass

@dataclass(slots=True, frozen=True, kw_only=True)
class UnknownData(SegmentDataBase):
    """用于存放未知消息段的原始数据"""

    raw: dict[str, Any]

    # 覆盖 from_dict，直接把整个字典塞进 raw，不进行过滤
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UnknownData:
        return cls(raw=data)
    
class UnknownDataType(SegmentDataTypeBase):
    raw: dict[str, Any]

@dataclass(slots=True, frozen=True, kw_only=True)
class MessageSegment[
    T_Type: LiteralString | str,
    T_Data: SegmentDataBase,
    T_DataType: SegmentDataTypeBase,
](ABC):
    type: T_Type
    data: T_Data

    _data_class: ClassVar[builtins.type[SegmentDataBase]]
    _registry: ClassVar[dict[str, builtins.type[MessageSegment[LiteralString | str, SegmentDataBase, SegmentDataTypeBase]]]] = {}

    def __init_subclass__(cls, **kwargs: Any):
        hints = get_type_hints(cls)
        data_cls = hints.get("data")

        if not data_cls:
            raise TypeError(f"Class {cls.__name__} missing type hint for 'data'")
        cls._data_class = data_cls

        _MISSING = object()
        type_val = getattr(cls, "type", _MISSING)

        if type_val is _MISSING:
            return

        if not isinstance(type_val, str):
            return

        if type_val in MessageSegment._registry:
            raise ValueError(f"Duplicate message type registered: {type_val}")

        MessageSegment._registry[type_val] = cls

    def __init__(self, **kwargs: Unpack[T_DataType]):  # type: ignore
        type_field = self.__class__.__dataclass_fields__["type"]
        object.__setattr__(self, "type", type_field.default)

        data_cls = self.__class__._data_class
        if not data_cls:
            raise ValueError(
                f"Class {self.__class__.__name__} missing type hint for 'data'"
            )

        data_inst = data_cls.from_dict(cast(dict[str, Any], kwargs))
        object.__setattr__(self, "data", data_inst)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> MessageSegment[Any, Any, Any]:
        seg_type = raw.get("type")
        if not isinstance(seg_type, str):
            raise ValueError("Invalid or missing 'type' field in message segment")
        data_payload = raw.get("data", {})
        if not isinstance(data_payload, dict):
            raise ValueError("Invalid message segment data")

        data_payload = cast(dict[str, Any], data_payload)

        target_cls = cls._registry.get(seg_type)
        if not target_cls:
            return UnknownMessageSegment(
                type=seg_type, data=UnknownData(raw=data_payload)
            )

        return target_cls(**data_payload)


@dataclass(slots=True, frozen=True, kw_only=True)
class UnknownMessageSegment(MessageSegment[str, UnknownData, UnknownDataType]):
    """表示未知的消息段"""

    type: str  # 这里不再是 Literal，而是动态字符串
    data: UnknownData  # 存放原始数据