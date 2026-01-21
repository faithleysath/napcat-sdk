# src/napcat/types/events/base.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar, cast

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
        
        # 1. 获取定义的类型 (保持之前的修复)
        pt = cls.__dict__.get("_post_type")
        if pt is None:
            pt = cls.__dict__.get("post_type")

        if not pt or not isinstance(pt, (str, tuple, list)):
            return

        # 统一转为列表处理
        pt_list: list[str]
        if isinstance(pt, str):
            pt_list = [pt]
        else:
            # 显式告知 Pylance 这里是字符串列表/元组
            pt_list = list(cast(list[str] | tuple[str, ...], pt))

        # 3. 注册逻辑 (带 dataclass slots 兼容)
        for t in pt_list:
            if t in NapCatEvent._registry:
                existing_cls = NapCatEvent._registry[t]
                # 核心修复：检查是否为同名同模块的类（说明是 dataclass slots 导致的重建）
                if existing_cls.__name__ == cls.__name__ and existing_cls.__module__ == cls.__module__:
                    # 允许覆盖（用新的 slotted 类替换旧的）
                    pass
                else:
                    raise ValueError(f"Duplicate post_type registered: {t} (Conflict between {existing_cls} and {cls})")
            
            # 写入/更新注册表
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