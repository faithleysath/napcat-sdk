# src/napcat/types/events/notice/base.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Literal

# 假设上层架构
from ..base import NapCatEvent


@dataclass(slots=True, frozen=True, kw_only=True)
class NoticeEvent(NapCatEvent):
    """
    所有通知事件的绝对基类。
    对应 TS: OB11BaseNoticeEvent
    """

    post_type: Literal["notice"] = "notice"
    notice_type: str

    # Python 3.12+: 使用原生 dict 和 type
    _post_type: ClassVar[str] = "notice"
    _notice_registry: ClassVar[dict[str, type[NoticeEvent]]] = {}
    _notify_registry: ClassVar[dict[str, type[NoticeEvent]]] = {}

    def __init_subclass__(cls, **kwargs: Any):
        super().__init_subclass__(**kwargs)

        # 1. 获取 notice_type
        n_type = getattr(cls, "notice_type", None)
        if not n_type or not isinstance(n_type, str):
            return

        # 2. 注册逻辑
        if n_type == "notify":
            s_type = getattr(cls, "sub_type", None)
            if s_type and isinstance(s_type, str):
                NoticeEvent._notify_registry[s_type] = cls
        else:
            NoticeEvent._notice_registry[n_type] = cls

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NoticeEvent:
        n_type = data.get("notice_type")

        if n_type == "notify":
            sub_type = data.get("sub_type")
            if isinstance(sub_type, str):
                target = cls._notify_registry.get(sub_type)
                if target:
                    return target._from_dict(data)
        elif isinstance(n_type, str):
            target = cls._notice_registry.get(n_type)
            if target:
                return target._from_dict(data)

        # 3. 兜底
        return UnknownNoticeEvent(
            time=int(data.get("time", 0)),
            self_id=int(data.get("self_id", 0)),
            notice_type=str(n_type) if n_type else "unknown",
            raw_data=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class UnknownNoticeEvent(NoticeEvent):
    """兜底未知事件"""

    raw_data: dict[str, Any]
    notice_type: str = "unknown"
