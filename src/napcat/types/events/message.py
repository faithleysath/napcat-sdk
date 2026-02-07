# src/napcat/types/events/message.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Literal, cast

from ..messages import MessageSegment, Text, Reply, At, Message, UnknownMessageSegment
from .base import NapCatEvent

from ..schemas import OB11Sender as MessageSender

@dataclass(slots=True, frozen=True, kw_only=True)
class MessageEvent(NapCatEvent):
    # 对应 NapCatQQ/packages/napcat-onebot/types/message.ts 中的 OB11Message
    message_id: int
    user_id: int | str
    message_seq: int | None = None
    real_id: int | None = None
    sender: MessageSender
    raw_message: str
    message: tuple[Message | UnknownMessageSegment, ...] | str
    message_format: Literal["array", "string"] | str = "array"
    font: int | None = None

    # --- 新增字段 ---
    real_seq: str | None = None  # 对应 TS real_seq
    message_sent_type: str | None = None # 对应 TS message_sent_type
    
    # 子类型，对应文档：friend, group (临时), normal (群普通)
    sub_type: Literal["friend", "group", "normal"] | str | None = None

    # debug=true 时，NapCat 会在上报里注入原始 RawMessage
    raw: Any | None = None
    
    post_type: Literal["message", "message_sent"] | tuple[str, str] = ("message", "message_sent")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PrivateMessageEvent | GroupMessageEvent:
        msg_type = data.get("message_type")
        raw_message = data.get("message", [])

        if isinstance(raw_message, str):
            parsed_message: tuple[Message | UnknownMessageSegment, ...] | str = raw_message
        elif isinstance(raw_message, list):
            parsed_message = tuple(
                MessageSegment.from_dict(seg)
                for seg in cast(list[dict[str, Any]], raw_message)
            )
        else:
            parsed_message = ()

        # 构建基础数据
        new_data = data | {"message": parsed_message}

        if msg_type == "group":
            return GroupMessageEvent(**new_data)
        elif msg_type == "private":
            return PrivateMessageEvent(**new_data)

        raise ValueError(f"Unknown message type: {msg_type}")
    
    async def send_msg(self, message: str | list[Message] | Message) -> int:
        raise NotImplementedError("send_msg must be implemented in subclasses")
    
    async def reply(self, message: str | list[Message] | Message, at: bool = False) -> int:
        if self._client is None:
            raise RuntimeError("Event not bound to a client")
        
        if isinstance(message, str):
            message = Text(text=message)

        if not isinstance(message, list):
            message = [message]

        segments: list[Message] = [Reply(id=str(self.message_id))]

        if at:
            segments.append(At(qq=str(self.user_id)))
        
        return await self.send_msg(segments + message)


@dataclass(slots=True, frozen=True, kw_only=True)
class PrivateMessageEvent(MessageEvent):
    # 对应 message.private
    target_id: int | None = None  # TS 中定义了 target_id?: number
    # 如果是群临时会话 (sub_type='group')，TS 中定义了 temp_source
    temp_source: int | None = None 
    # 临时会话私聊上报里可能携带 group_id
    group_id: int | str | None = None
    message_type: Literal["private"] = "private"
    sub_type: Literal["friend", "group"] | str | None = None

    async def send_msg(self, message: str | list[Message] | Message) -> int:
        if self._client is None:
            raise RuntimeError("Event not bound to a client")
        return await self._client.send_private_msg(
            user_id=int(self.user_id),
            message=message
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class GroupMessageEvent(MessageEvent):
    # 对应 message.group
    group_id: int
    group_name: str | None = None # TS 中定义了 group_name
    # 自发群消息上报里可能携带 target_id
    target_id: int | None = None
    message_type: Literal["group"] = "group"
    sub_type: Literal["normal"] | str | None = None

    async def send_msg(self, message: str | list[Message] | Message) -> int:
        if self._client is None:
            raise RuntimeError("Event not bound to a client")
        return await self._client.send_group_msg(
            group_id=self.group_id,
            message=message
        )
