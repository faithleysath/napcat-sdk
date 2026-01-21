from __future__ import annotations
import builtins
from abc import ABC
from dataclasses import dataclass, MISSING
from functools import lru_cache
from typing import (
    Any,
    ClassVar,
    Literal,
    LiteralString,
    TypedDict,
    cast,
    get_type_hints,
    get_args,     # <--- 新增
    get_origin,   # <--- 新增
)

from ..utils import IgnoreExtraArgsMixin, TypeValidatorMixin


@lru_cache(maxsize=256)
def _cached_get_type_hints(cls: type) -> dict[str, Any]:
    """缓存 get_type_hints 结果，避免重复的反射开销"""
    return get_type_hints(cls)

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
class MessageSegment(ABC):
    type: LiteralString | str
    data: SegmentDataBase

    _data_class: ClassVar[builtins.type[SegmentDataBase]]
    _registry: ClassVar[dict[str, builtins.type[MessageSegment]]] = {}

    def __init_subclass__(cls, **kwargs: Any):
        # 1. 提取 'data' 字段的类型
        hints = _cached_get_type_hints(cls)
        data_cls = hints.get("data")

        if not data_cls:
            # 如果没有 data 定义，可能是抽象基类，直接跳过
            # 原代码是 raise TypeError，为了安全起见这里保留原逻辑，但建议加上 hasattr 检查
            if ABC in cls.__bases__:
                return
            raise TypeError(f"Class {cls.__name__} missing type hint for 'data'")
        
        cls._data_class = data_cls

        # 2. 尝试获取 'type' 的值
        _MISSING = object()
        
        # 优先尝试直接获取类属性 (type = "text")
        type_val = getattr(cls, "type", _MISSING)

        # 核心修复 A: 如果类属性不存在，尝试从类型注解 (type: Literal["text"]) 中提取
        if type_val is _MISSING:
            type_hint = hints.get("type")
            # 检查类型提示是否为 Literal
            if type_hint and get_origin(type_hint) is Literal:
                args = get_args(type_hint)
                # 取 Literal 的第一个参数作为值
                if args and isinstance(args[0], str):
                    type_val = args[0]

        # 如果还是没找到，或者类型不是字符串，说明这不是一个具体的实现类，跳过注册
        if type_val is _MISSING or not isinstance(type_val, str):
            return

        # 3. 注册逻辑 (带 slots 兼容)
        if type_val in MessageSegment._registry:
            existing_cls = MessageSegment._registry[type_val]
            
            # 核心修复 B: 检查是否为同名同模块的类（dataclass slots 重建导致的）
            if existing_cls.__name__ == cls.__name__ and existing_cls.__module__ == cls.__module__:
                # 是同一个类的重建版本，允许覆盖
                pass
            else:
                # 真正的重复注册，抛出异常
                raise ValueError(f"Duplicate message type registered: {type_val} (Conflict between {existing_cls} and {cls})")

        MessageSegment._registry[type_val] = cls

    def __init__(self, **kwargs: Any):
        # 从类型注解的 Literal 中提取 type 值
        hints = _cached_get_type_hints(self.__class__)
        type_hint = hints.get("type")
        type_val = None
        
        if type_hint and get_origin(type_hint) is Literal:
            args = get_args(type_hint)
            if args and isinstance(args[0], str):
                type_val = args[0]
        
        # 如果无法从 Literal 提取，尝试从字段默认值获取
        if type_val is None:
            type_field = self.__class__.__dataclass_fields__["type"]
            if type_field.default is not MISSING:
                type_val = type_field.default
            elif type_field.default_factory is not MISSING:
                type_val = type_field.default_factory()
        
        if type_val is None:
            raise ValueError(
                f"Class {self.__class__.__name__} has no default type value"
            )
        
        object.__setattr__(self, "type", type_val)

        data_cls = self.__class__._data_class
        if not data_cls:
            raise ValueError(
                f"Class {self.__class__.__name__} missing type hint for 'data'"
            )

        data_inst = data_cls.from_dict(kwargs)
        object.__setattr__(self, "data", data_inst)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> MessageSegment:
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
class UnknownMessageSegment(MessageSegment):
    """表示未知的消息段"""

    type: str  # 这里不再是 Literal，而是动态字符串
    data: UnknownData  # 存放原始数据