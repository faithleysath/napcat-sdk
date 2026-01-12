from dataclasses import dataclass
from typing import Any, Literal, LiteralString

from .messages import MessageSegment
from .utils import IgnoreExtraArgsMixin, TypeValidatorMixin

# --- Base ---


@dataclass(slots=True, frozen=True, kw_only=True)
class NapCatEvent(TypeValidatorMixin, IgnoreExtraArgsMixin):
    time: int
    self_id: int
    post_type: LiteralString | str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NapCatEvent:
        # 尝试按照已知逻辑解析
        try:
            post_type = data.get("post_type")
            match post_type:
                case "meta_event":
                    return MetaEvent.from_dict(data)
                case "message" | "message_sent":
                    return MessageEvent.from_dict(data)
                # 未来加 notice / request 也是写在这里
                case _:
                    # 只有在这里显式抛出 ValueError，才能跳到下面的 except
                    # 如果不抛出，就需要在这里直接 return UnknownEvent(...)
                    raise ValueError(f"Unknown post type: {post_type}")

        except (ValueError, TypeError, KeyError):
            # 记录日志可以在这里做，或者静默处理
            pass

        # --- 兜底逻辑：所有解析失败或未知的类型都走这里 ---
        return UnknownEvent(
            time=int(data.get("time", 0)),
            self_id=int(data.get("self_id", 0)),
            post_type=str(data.get("post_type", "unknown")),
            raw_data=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class UnknownEvent(NapCatEvent):
    """万能兜底事件：当 post_type 未知或解析失败时返回此对象"""

    raw_data: dict[str, Any]
    post_type: str = "unknown"  # 覆盖父类可能的类型限制，允许任意字符串


# --- Meta Events ---


@dataclass(slots=True, frozen=True, kw_only=True)
class HeartbeatStatus(TypeValidatorMixin, IgnoreExtraArgsMixin):
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
class MessageSender(TypeValidatorMixin, IgnoreExtraArgsMixin):
    user_id: int
    nickname: str
    card: str | None = None
    # 使用 Literal 约束角色，私聊消息可能没有 role 字段，所以设为 None
    role: Literal["owner", "admin", "member"] | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class MessageEvent(NapCatEvent):
    user_id: int
    message_id: int
    sender: MessageSender | None = None
    raw_message: str
    message: list[MessageSegment]
    message_format: Literal["array"] = "array"
    post_type: Literal["message", "message_sent"]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MessageEvent:
        msg_type = data.get("message_type")

        raw_segments = data.get("message", [])
        if not isinstance(raw_segments, list):
            raise ValueError("Invalid message format")

        new_data = data | {
            "message": [MessageSegment.from_dict(seg) for seg in raw_segments],
            "sender": data.get("sender", None)
            and MessageSender.from_dict(data["sender"]),
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
