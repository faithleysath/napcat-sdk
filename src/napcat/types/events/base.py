# src/napcat/types/events/base.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from ...client import NapCatClient
else:
    NapCatClient = Any

from ..utils import IgnoreExtraArgsMixin, TypeValidatorMixin


@dataclass(slots=True, frozen=True, kw_only=True)
class NapCatEvent(TypeValidatorMixin, IgnoreExtraArgsMixin):
    """
    对应 NapCatQQ/packages/napcat-onebot/event/OneBotEvent.ts
    """
    time: int
    self_id: int
    post_type: str
    _client: NapCatClient | None = field(
        init=False, repr=False, hash=False, compare=False, default=None
    )

    # --- 自动注册机制 ---
    _registry: ClassVar[dict[str, type[NapCatEvent]]] = {}

    def __init_subclass__(cls, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        
        # 1. 尝试读取子类显式定义的 _post_type (支持字符串或元组)
        #    这对于一个类处理多个 post_type (如 MessageEvent) 很有用
        pt: str | tuple[str, ...] | list[str] | None = getattr(cls, "_post_type", None)

        # 2. 如果没有 _post_type，尝试读取 dataclass 字段的默认值 post_type
        if pt is None:
            pt = getattr(cls, "post_type", None)

        if not pt:
            return

        # 3. 注册到注册表
        if isinstance(pt, str):
            if pt in NapCatEvent._registry:
                raise ValueError(f"Duplicate post_type registered: {pt}")
            NapCatEvent._registry[pt] = cls
        else:
            for t in pt:
                if t in NapCatEvent._registry:
                    raise ValueError(f"Duplicate post_type registered: {t}")
                NapCatEvent._registry[t] = cls

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NapCatEvent:
        try:
            post_type = data.get("post_type")
            if not isinstance(post_type, str):
                raise ValueError("Missing or invalid 'post_type'")

            # --- 核心变更：从注册表查找类，而不是硬编码 ---
            target_cls = cls._registry.get(post_type)
            
            if target_cls:
                return target_cls.from_dict(data)
            
            # 如果没找到，会在下面抛出或进入兜底逻辑
            # 这里选择显式 raise 以便进入 except 块处理兜底，或者直接返回 Unknown
            
        except (ValueError, TypeError, KeyError):
            pass

        # --- 兜底逻辑 ---
        return UnknownEvent(
            time=int(data.get("time", 0)),
            self_id=int(data.get("self_id", 0)),
            post_type=str(data.get("post_type", "unknown")),
            raw_data=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class UnknownEvent(NapCatEvent):
    """万能兜底事件"""
    raw_data: dict[str, Any]
    post_type: str = "unknown"