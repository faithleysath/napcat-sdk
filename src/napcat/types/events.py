# src/napcat/types/events.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal, cast

if TYPE_CHECKING:
    from ..client import NapCatClient
else:
    NapCatClient = Any

from .messages import MessageSegment, MessageText, MessageReply, MessageAt
from .utils import IgnoreExtraArgsMixin, TypeValidatorMixin

# --- Base ---

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
                    return MetaEvent.from_dict(data)
                case "message" | "message_sent":
                    # message_sent 结构与 message 一致
                    return MessageEvent.from_dict(data)
                # 未来在此处添加 notice / request
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


# --- Meta Events ---

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


# --- Message Events ---

@dataclass(slots=True, frozen=True, kw_only=True)
class MessageSender(TypeValidatorMixin, IgnoreExtraArgsMixin):
    # 对应 NapCatQQ/packages/napcat-onebot/types/data.ts 中的 OB11Sender
    user_id: int
    nickname: str
    sex: Literal["male", "female", "unknown"] | None = None
    age: int | None = None
    card: str | None = None
    level: str | None = None  # TS定义为string
    role: Literal["owner", "admin", "member"] | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class MessageEvent(NapCatEvent):
    # 对应 NapCatQQ/packages/napcat-onebot/types/message.ts 中的 OB11Message
    message_id: int
    user_id: int | str
    message_seq: int | None = None
    real_id: int | None = None
    sender: MessageSender
    raw_message: str
    message: tuple[MessageSegment]
    message_format: Literal["array"] = "array"
    font: int | None = None

    # --- 新增字段 ---
    real_seq: str | None = None  # 对应 TS real_seq
    message_sent_type: str | None = None # 对应 TS message_sent_type
    
    # 子类型，对应文档：friend, group (临时), normal (群普通)
    sub_type: Literal["friend", "group", "normal"] | str | None = None
    
    post_type: Literal["message", "message_sent"]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MessageEvent:
        msg_type = data.get("message_type")
        raw_segments = data.get("message", [])
        
        if not isinstance(raw_segments, list):
            # 容错处理：如果 format 是 string，可能这里还是 string，虽然 OneBot11 推荐 array
            raw_segments = [] 

        # 构建基础数据
        new_data = data | {
            "message": tuple(MessageSegment.from_dict(seg) for seg in cast(list[dict[str, Any]], raw_segments)),
            "sender": MessageSender.from_dict(data.get("sender", {})),
        }

        if msg_type == "group":
            return GroupMessageEvent._from_dict(new_data)
        elif msg_type == "private":
            return PrivateMessageEvent._from_dict(new_data)

        raise ValueError(f"Unknown message type: {msg_type}")
    
    async def send_msg(self, message: str | list[MessageSegment]) -> int:
        raise NotImplementedError("send_msg must be implemented in subclasses")
    
    async def reply(self, message: str | list[MessageSegment], at: bool = False) -> int:
        if self._client is None:
            raise RuntimeError("Event not bound to a client")
        
        if isinstance(message, str):
            message = [MessageText(text=message)]

        segments: list[MessageSegment] = [MessageReply(id=str(self.message_id))]
        if at:
            segments.append(MessageAt(qq=str(self.user_id)))
        
        return await self.send_msg(segments + message)


@dataclass(slots=True, frozen=True, kw_only=True)
class PrivateMessageEvent(MessageEvent):
    # 对应 message.private
    target_id: int | None = None  # TS 中定义了 target_id?: number
    # 如果是群临时会话 (sub_type='group')，TS 中定义了 temp_source
    temp_source: int | None = None 
    message_type: Literal["private"] = "private"
    sub_type: Literal["friend", "group"] | str | None = None

    async def send_msg(self, message: str | list[MessageSegment]) -> int:
        if self._client is None:
            raise RuntimeError("Event not bound to a client")
        return await self._client.send_private_msg(
            user_id=int(self.user_id),
            message=message
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class GroupMessageEvent(MessageEvent):
    # 对应 message.group
    group_id: int | str
    group_name: str | None = None # TS 中定义了 group_name
    message_type: Literal["group"] = "group"
    sub_type: Literal["normal"] | str | None = None

    async def send_msg(self, message: str | list[MessageSegment]) -> int:
        if self._client is None:
            raise RuntimeError("Event not bound to a client")
        return await self._client.send_group_msg(
            group_id=int(self.group_id),
            message=message
        )