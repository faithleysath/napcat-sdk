# src/napcat/types/events/message.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Literal, cast

from ..messages import MessageSegment, MessageText, MessageReply, MessageAt, MessageSegmentType
from ..utils import IgnoreExtraArgsMixin, TypeValidatorMixin
from .base import NapCatEvent


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
    message: tuple[MessageSegmentType]
    message_format: Literal["array"] = "array"
    font: int | None = None

    # --- 新增字段 ---
    real_seq: str | None = None  # 对应 TS real_seq
    message_sent_type: str | None = None # 对应 TS message_sent_type
    
    # 子类型，对应文档：friend, group (临时), normal (群普通)
    sub_type: Literal["friend", "group", "normal"] | str | None = None
    
    post_type: Literal["message", "message_sent"]
    _post_type = ("message", "message_sent")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PrivateMessageEvent | GroupMessageEvent:
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
    
    async def send_msg(self, message: str | list[MessageSegmentType]) -> int:
        raise NotImplementedError("send_msg must be implemented in subclasses")
    
    async def reply(self, message: str | list[MessageSegmentType], at: bool = False) -> int:
        if self._client is None:
            raise RuntimeError("Event not bound to a client")
        
        if isinstance(message, str):
            message = [MessageText(text=message)]

        segments: list[MessageSegmentType] = [MessageReply(id=str(self.message_id))]
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

    async def send_msg(self, message: str | list[MessageSegmentType]) -> int:
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

    async def send_msg(self, message: str | list[MessageSegmentType]) -> int:
        if self._client is None:
            raise RuntimeError("Event not bound to a client")
        return await self._client.send_group_msg(
            group_id=int(self.group_id),
            message=message
        )
