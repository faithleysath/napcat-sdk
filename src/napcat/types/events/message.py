# src/napcat/types/events/message.py

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Literal, NotRequired, TypedDict, cast

from ...exceptions import NapCatProtocolError, NapCatStateError
from ..messages import At, Message, MessageSegment, Reply, Text, UnknownMessageSegment
from ..utils import FromDictMixin
from .base import NapCatEvent

logger = logging.getLogger("napcat.events")


class MessageSenderPayload(TypedDict):
    user_id: int | str
    nickname: str
    card: NotRequired[str]
    role: NotRequired[Literal["owner", "admin", "member"] | str]
    sex: NotRequired[Literal["male", "female", "unknown"] | str]
    age: NotRequired[int]
    area: NotRequired[str]
    level: NotRequired[str]
    title: NotRequired[str]


class EmojiLikeItemPayload(TypedDict):
    emoji_id: str
    emoji_type: str
    likes_cnt: str


@dataclass(slots=True, frozen=True, kw_only=True)
class MessageSender(FromDictMixin):
    """对应 NapCatQQ/packages/napcat-onebot/types/message.ts 中的 OB11Sender"""

    user_id: int | str
    nickname: str
    card: str | None = None
    role: Literal["owner", "admin", "member"] | str | None = None
    sex: Literal["male", "female", "unknown"] | str | None = None
    age: int | None = None
    area: str | None = None
    level: str | None = None
    title: str | None = None

    @classmethod
    def from_dict(cls, data: MessageSenderPayload) -> MessageSender:
        return cls._from_dict(cast(dict[str, Any], data))


@dataclass(slots=True, frozen=True, kw_only=True)
class EmojiLikeItem(FromDictMixin):
    """对应 OB11Message.emoji_likes_list 的单项结构"""

    emoji_id: str
    emoji_type: str
    likes_cnt: str

    @classmethod
    def from_dict(cls, data: EmojiLikeItemPayload) -> EmojiLikeItem:
        return cls._from_dict(cast(dict[str, Any], data))


@dataclass(slots=True, frozen=True, kw_only=True)
class MessageEvent(NapCatEvent):
    # 对应 NapCatQQ/packages/napcat-onebot/types/message.ts 中的 OB11Message
    message_id: int
    user_id: int | str
    message_seq: int
    real_id: int
    sender: MessageSender
    raw_message: str
    message: tuple[Message | UnknownMessageSegment, ...]
    message_format: Literal["array"] = "array"
    font: int = 14

    # --- 新增字段 ---
    real_seq: str | None = None  # 对应 TS real_seq
    message_sent_type: str | None = None  # 对应 TS message_sent_type

    # 子类型，对应文档：friend, group (临时), normal (群普通)
    sub_type: Literal["friend", "group", "normal"] | str | None = None

    # debug=true 时，NapCat 会在上报里注入原始 RawMessage
    raw: Any | None = None

    # 消息表情点赞列表（部分路径如 get_msg/get_history 可能返回）
    emoji_likes_list: list[EmojiLikeItem] | None = None

    post_type: Literal["message", "message_sent"] | tuple[str, str] = (
        "message",
        "message_sent",
    )

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], **kwargs: Any
    ) -> PrivateMessageEvent | GroupMessageEvent:
        msg_type = data.get("message_type")
        raw_message = data.get("message", [])
        raw_sender = data.get("sender")
        raw_emoji_likes_list = data.get("emoji_likes_list")

        if isinstance(raw_message, str):
            logger.critical(
                "Invalid message payload type=str in MessageEvent: message_type=%r payload_keys=%s",
                msg_type,
                sorted(data.keys()),
            )
            raise NapCatProtocolError("Unsupported message payload type: str")
        elif isinstance(raw_message, list):
            parsed_message = tuple(
                MessageSegment.from_dict(seg)
                for seg in cast(list[dict[str, Any]], raw_message)
            )
        else:
            parsed_message = ()

        parsed_sender: MessageSender
        if (
            isinstance(raw_sender, dict)
            and "user_id" in raw_sender
            and "nickname" in raw_sender
        ):
            parsed_sender = MessageSender.from_dict(
                cast(MessageSenderPayload, raw_sender)
            )
        else:
            raise NapCatProtocolError("Invalid sender data in message event")

        parsed_emoji_likes_list: list[EmojiLikeItem] | None
        if isinstance(raw_emoji_likes_list, list):
            parsed_emoji_likes_list = [
                EmojiLikeItem.from_dict(cast(EmojiLikeItemPayload, raw_item))
                for raw_item in cast(list[Any], raw_emoji_likes_list)
                if isinstance(raw_item, dict)
                and "emoji_id" in raw_item
                and "emoji_type" in raw_item
                and "likes_cnt" in raw_item
            ]
        else:
            parsed_emoji_likes_list = None

        # 构建基础数据
        new_data = data | {
            "message": parsed_message,
            "sender": parsed_sender,
            "emoji_likes_list": parsed_emoji_likes_list,
        }

        if msg_type == "group":
            return GroupMessageEvent._from_dict(new_data)
        elif msg_type == "private":
            return PrivateMessageEvent._from_dict(new_data)

        raise NapCatProtocolError(f"Unknown message type: {msg_type}")

    async def send_msg(self, message: str | list[Message] | Message) -> int:
        raise NotImplementedError("send_msg must be implemented in subclasses")

    async def reply(
        self, message: str | list[Message] | Message, at: bool = False
    ) -> int:
        if self._client is None:
            raise NapCatStateError("Event not bound to a client")
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
            raise NapCatStateError("Event not bound to a client")
        resp = await self._client.send_private_msg(
            user_id=str(self.user_id), message=message
        )
        return resp["message_id"]


@dataclass(slots=True, frozen=True, kw_only=True)
class GroupMessageEvent(MessageEvent):
    # 对应 message.group
    group_id: int
    group_name: str | None = None  # TS 中定义了 group_name
    # 自发群消息上报里可能携带 target_id
    target_id: int | None = None
    message_type: Literal["group"] = "group"
    sub_type: Literal["normal"] | str | None = None

    async def send_msg(self, message: str | list[Message] | Message) -> int:
        if self._client is None:
            raise NapCatStateError("Event not bound to a client")
        resp = await self._client.send_group_msg(
            group_id=str(self.group_id), message=message
        )
        return resp["message_id"]
