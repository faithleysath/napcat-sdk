# src/napcat/types/events/meta.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Literal

from ..utils import IgnoreExtraArgsMixin, TypeValidatorMixin
from .base import NapCatEvent


@dataclass(slots=True, frozen=True, kw_only=True)
class HeartbeatStatus(TypeValidatorMixin, IgnoreExtraArgsMixin):
    # 对应 NapCatQQ/packages/napcat-onebot/event/meta/OB11HeartbeatEvent.ts
    online: bool | None = None
    good: bool


@dataclass(slots=True, frozen=True, kw_only=True)
class MetaEvent(NapCatEvent):
    # 对应 NapCatQQ/packages/napcat-onebot/event/meta/OB11BaseMetaEvent.ts
    post_type: Literal["meta_event"] = "meta_event"
    meta_event_type: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MetaEvent:
        meta_type = data.get("meta_event_type")
        if meta_type == "lifecycle":
            return LifecycleMetaEvent._from_dict(data)
        elif meta_type == "heartbeat":
            return HeartbeatEvent._from_dict(
                data | {"status": HeartbeatStatus.from_dict(data["status"])}
            )
        raise ValueError(f"Unknown meta event type: {meta_type}")


@dataclass(slots=True, frozen=True, kw_only=True)
class LifecycleMetaEvent(MetaEvent):
    # 对应 NapCatQQ/packages/napcat-onebot/event/meta/OB11LifeCycleEvent.ts
    # 虽然文档目前只标注了 connect 可用，但源码定义了 enable/disable，补全以防万一
    sub_type: Literal["enable", "disable", "connect"]
    meta_event_type: Literal["lifecycle"] = "lifecycle"


@dataclass(slots=True, frozen=True, kw_only=True)
class HeartbeatEvent(MetaEvent):
    # 对应 NapCatQQ/packages/napcat-onebot/event/meta/OB11HeartbeatEvent.ts
    status: HeartbeatStatus
    interval: int
    meta_event_type: Literal["heartbeat"] = "heartbeat"
