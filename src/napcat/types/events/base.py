# src/napcat/types/events/base.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NapCatEvent:
        try:
            post_type = data.get("post_type")
            match post_type:
                case "meta_event":
                    from .meta import MetaEvent
                    return MetaEvent.from_dict(data)
                case "message" | "message_sent":
                    # message_sent 结构与 message 一致
                    from .message import MessageEvent
                    return MessageEvent.from_dict(data)
                case "request":
                    from .request import RequestEvent
                    return RequestEvent.from_dict(data)
                # 未来在此处添加 notice
                case _:
                    # 显式抛出异常以触发兜底逻辑
                    raise ValueError(f"Unknown post type: {post_type}")

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
