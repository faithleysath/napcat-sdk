from dataclasses import dataclass
from typing import Any, Literal, Self

from .messages import MessageSegment
from .utils import IgnoreExtraArgsMixin

# --- Base ---


@dataclass(slots=True, frozen=True, kw_only=True)
class NapCatEvent(IgnoreExtraArgsMixin):
    time: int
    self_id: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NapCatEvent:
        post_type = data.get("post_type")
        match post_type:
            case "meta_event":
                return MetaEvent.from_dict(data)
            case "message" | "message_sent":
                return MessageEvent.from_dict(data)
            case _:
                raise ValueError(f"Unknown post type: {post_type}")


# --- Meta Events ---


@dataclass(slots=True, frozen=True, kw_only=True)
class HeartbeatStatus(IgnoreExtraArgsMixin):
    online: bool
    good: bool


@dataclass(slots=True, frozen=True, kw_only=True)
class MetaEvent(NapCatEvent):
    post_type: Literal["meta_event"] = "meta_event"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MetaEvent:
        meta_type = data.get("meta_event_type")
        if meta_type == "lifecycle":
            # LifecycleMetaEvent / ConnectEvent
            return LifecycleMetaEvent._from_dict(data)
        elif meta_type == "heartbeat":
            # HeartbeatEvent
            return HeartbeatEvent._from_dict(
                data | {"status": HeartbeatStatus.from_dict(data["status"])}
            )
        raise ValueError(f"Unknown meta event type: {meta_type}")


@dataclass(slots=True, frozen=True, kw_only=True)
class LifecycleMetaEvent(MetaEvent):
    sub_type: Literal["connect"] = "connect"
    meta_event_type: Literal["lifecycle"] = "lifecycle"


@dataclass(slots=True, frozen=True, kw_only=True)
class HeartbeatEvent(MetaEvent):
    status: HeartbeatStatus
    interval: int
    meta_event_type: Literal["heartbeat"] = "heartbeat"


# --- Message Events ---


@dataclass(slots=True, frozen=True, kw_only=True)
class MessageEvent(NapCatEvent):
    user_id: int
    message_id: int
    raw_message: str
    message: list[MessageSegment]
    message_format: Literal["array"] = "array"
    post_type: Literal["message", "message_sent"] = "message"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MessageEvent:
        msg_type = data.get("message_type")

        raw_segments = data.get("message", [])
        new_data = data | {
            "message": [MessageSegment.from_dict(seg) for seg in raw_segments]
        }

        if msg_type == "group":
            return GroupMessageEvent._from_dict(new_data)
        elif msg_type == "private":
            return PrivateMessageEvent._from_dict(new_data)

        raise ValueError(f"Unknown message type: {msg_type}")


@dataclass(slots=True, frozen=True, kw_only=True)
class PrivateMessageEvent(MessageEvent):
    target_id: int
    message_type: Literal["private"] = "private"


@dataclass(slots=True, frozen=True, kw_only=True)
class GroupMessageEvent(MessageEvent):
    group_id: int
    message_type: Literal["group"] = "group"
