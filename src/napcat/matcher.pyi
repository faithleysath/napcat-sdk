# Auto-generated file. Do not modify directly.

from __future__ import annotations

from collections.abc import Callable
from types import UnionType
from typing import Any, Literal, TypedDict, Unpack, overload

from .types.events.base import NapCatEvent, UnknownEvent
from .types.events.message import (
    EmojiLikeItem,
    GroupMessageEvent,
    MessageEvent,
    MessageSender,
    PrivateMessageEvent,
)
from .types.events.meta import (
    HeartbeatEvent,
    HeartbeatStatus,
    LifecycleMetaEvent,
    MetaEvent,
)
from .types.events.notice.base import NoticeEvent, UnknownNoticeEvent
from .types.events.notice.BotOfflineEvent import BotOfflineEvent
from .types.events.notice.FriendAddNoticeEvent import FriendAddNoticeEvent
from .types.events.notice.FriendRecallNoticeEvent import FriendRecallNoticeEvent
from .types.events.notice.GroupAdminNoticeEvent import GroupAdminNoticeEvent
from .types.events.notice.GroupBanEvent import GroupBanEvent
from .types.events.notice.GroupCardEvent import GroupCardEvent
from .types.events.notice.GroupDecreaseEvent import GroupDecreaseEvent
from .types.events.notice.GroupEssenceEvent import GroupEssenceEvent
from .types.events.notice.GroupGrayTipEvent import GroupGrayTipEvent
from .types.events.notice.GroupIncreaseEvent import GroupIncreaseEvent
from .types.events.notice.GroupNameEvent import GroupNameEvent
from .types.events.notice.GroupNoticeEvent import GroupNoticeEvent
from .types.events.notice.GroupRecallNoticeEvent import GroupRecallNoticeEvent
from .types.events.notice.GroupTitleEvent import GroupTitleEvent
from .types.events.notice.GroupUploadNoticeEvent import (
    GroupUploadFile,
    GroupUploadNoticeEvent,
)
from .types.events.notice.InputStatusEvent import InputStatusEvent
from .types.events.notice.MsgEmojiLikeEvent import GroupMsgEmojiLikeEvent, MsgEmojiLike
from .types.events.notice.OnlineFileNoticeEvent import OnlineFileNoticeEvent
from .types.events.notice.OnlineFileReceiveEvent import OnlineFileReceiveEvent
from .types.events.notice.OnlineFileSendEvent import OnlineFileSendEvent
from .types.events.notice.PokeEvent import FriendPokeEvent, GroupPokeEvent, PokeEvent
from .types.events.notice.ProfileLikeEvent import ProfileLikeEvent
from .types.events.request import FriendRequestEvent, GroupRequestEvent, RequestEvent
from .types.messages.base import UnknownMessageSegment
from .types.messages.generated import Message

type Predicate[T] = Callable[[T], bool]

class BotOfflineEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: Literal['bot_offline'] | Predicate[Literal['bot_offline']]
    user_id: int | Predicate[int]
    tag: Literal['BotOfflineEvent'] | str | Predicate[Literal['BotOfflineEvent'] | str]
    message: Literal['BotOfflineEvent'] | str | Predicate[Literal['BotOfflineEvent'] | str]
class EmojiLikeItemPattern(TypedDict, total=False):
    emoji_id: str | Predicate[str]
    emoji_type: str | Predicate[str]
    likes_cnt: str | Predicate[str]
class FriendAddNoticeEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: Literal['friend_add'] | Predicate[Literal['friend_add']]
    user_id: int | Predicate[int]
class FriendPokeEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: Literal['notify'] | Predicate[Literal['notify']]
    sub_type: Literal['poke'] | Predicate[Literal['poke']]
    target_id: int | Predicate[int]
    user_id: int | Predicate[int]
    raw_info: Any | Predicate[Any]
    sender_id: int | Predicate[int]
class FriendRecallNoticeEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: Literal['friend_recall'] | Predicate[Literal['friend_recall']]
    user_id: int | Predicate[int]
    message_id: int | Predicate[int]
class FriendRequestEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['request'] | Predicate[Literal['request']]
    request_type: Literal['friend'] | Predicate[Literal['friend']]
    user_id: int | Predicate[int]
    comment: str | Predicate[str]
    flag: str | Predicate[str]
class GroupAdminNoticeEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: Literal['group_admin'] | Predicate[Literal['group_admin']]
    group_id: int | Predicate[int]
    user_id: int | Predicate[int]
    sub_type: Literal['set', 'unset'] | Predicate[Literal['set', 'unset']]
class GroupBanEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: Literal['group_ban'] | Predicate[Literal['group_ban']]
    group_id: int | Predicate[int]
    user_id: int | Predicate[int]
    operator_id: int | Predicate[int]
    duration: int | Predicate[int]
    sub_type: Literal['ban', 'lift_ban'] | Predicate[Literal['ban', 'lift_ban']]
class GroupCardEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: Literal['group_card'] | Predicate[Literal['group_card']]
    group_id: int | Predicate[int]
    user_id: int | Predicate[int]
    card_new: str | Predicate[str]
    card_old: str | Predicate[str]
class GroupDecreaseEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: Literal['group_decrease'] | Predicate[Literal['group_decrease']]
    group_id: int | Predicate[int]
    user_id: int | Predicate[int]
    sub_type: Literal['leave', 'kick', 'kick_me', 'disband'] | Predicate[Literal['leave', 'kick', 'kick_me', 'disband']]
    operator_id: int | Predicate[int]
class GroupEssenceEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: Literal['essence'] | Predicate[Literal['essence']]
    group_id: int | Predicate[int]
    user_id: int | Predicate[int]
    message_id: int | Predicate[int]
    sender_id: int | Predicate[int]
    operator_id: int | Predicate[int]
    sub_type: Literal['add', 'delete'] | Predicate[Literal['add', 'delete']]
class GroupGrayTipEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: Literal['notify'] | Predicate[Literal['notify']]
    sub_type: Literal['gray_tip'] | Predicate[Literal['gray_tip']]
    group_id: int | Predicate[int]
    user_id: int | Predicate[int]
    message_id: int | Predicate[int]
    busi_id: str | Predicate[str]
    content: str | Predicate[str]
    raw_info: Any | Predicate[Any]
class GroupIncreaseEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: Literal['group_increase'] | Predicate[Literal['group_increase']]
    group_id: int | Predicate[int]
    user_id: int | Predicate[int]
    operator_id: int | Predicate[int]
    sub_type: Literal['approve', 'invite'] | Predicate[Literal['approve', 'invite']]
class GroupMessageEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['message', 'message_sent'] | tuple[str, str] | Predicate[Literal['message', 'message_sent'] | tuple[str, str]]
    message_id: int | Predicate[int]
    user_id: int | str | Predicate[int | str]
    message_seq: int | Predicate[int]
    real_id: int | Predicate[int]
    sender: MessageSenderPattern | Predicate[MessageSender]
    raw_message: str | Predicate[str]
    message: tuple[Message | UnknownMessageSegment, ...] | Predicate[tuple[Message | UnknownMessageSegment, ...]]
    message_format: Literal['array'] | Predicate[Literal['array']]
    font: int | Predicate[int]
    real_seq: str | None | Predicate[str | None]
    message_sent_type: str | None | Predicate[str | None]
    sub_type: Literal['normal'] | str | None | Predicate[Literal['normal'] | str | None]
    raw: Any | None | Predicate[Any | None]
    emoji_likes_list: list[EmojiLikeItem] | None | Predicate[list[EmojiLikeItem] | None]
    group_id: int | Predicate[int]
    group_name: str | None | Predicate[str | None]
    target_id: int | None | Predicate[int | None]
    message_type: Literal['group'] | Predicate[Literal['group']]
class GroupMsgEmojiLikeEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: Literal['group_msg_emoji_like'] | Predicate[Literal['group_msg_emoji_like']]
    group_id: int | Predicate[int]
    user_id: int | Predicate[int]
    message_id: int | Predicate[int]
    likes: list[MsgEmojiLike] | Predicate[list[MsgEmojiLike]]
    is_add: bool | Predicate[bool]
    message_seq: str | None | Predicate[str | None]
class GroupNameEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: Literal['notify'] | Predicate[Literal['notify']]
    group_id: int | Predicate[int]
    user_id: int | Predicate[int]
    sub_type: Literal['group_name'] | Predicate[Literal['group_name']]
    name_new: str | Predicate[str]
class GroupNoticeEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: str | Predicate[str]
    group_id: int | Predicate[int]
    user_id: int | Predicate[int]
class GroupPokeEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: Literal['notify'] | Predicate[Literal['notify']]
    sub_type: Literal['poke'] | Predicate[Literal['poke']]
    target_id: int | Predicate[int]
    user_id: int | Predicate[int]
    group_id: int | Predicate[int]
    raw_info: Any | Predicate[Any]
class GroupRecallNoticeEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: Literal['group_recall'] | Predicate[Literal['group_recall']]
    group_id: int | Predicate[int]
    user_id: int | Predicate[int]
    operator_id: int | Predicate[int]
    message_id: int | Predicate[int]
class GroupRequestEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['request'] | Predicate[Literal['request']]
    request_type: Literal['group'] | Predicate[Literal['group']]
    group_id: int | Predicate[int]
    user_id: int | Predicate[int]
    sub_type: Literal['add', 'invite'] | str | Predicate[Literal['add', 'invite'] | str]
    comment: str | Predicate[str]
    flag: str | Predicate[str]
class GroupTitleEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: Literal['notify'] | Predicate[Literal['notify']]
    group_id: int | Predicate[int]
    user_id: int | Predicate[int]
    sub_type: Literal['title'] | Predicate[Literal['title']]
    title: str | Predicate[str]
class GroupUploadFilePattern(TypedDict, total=False):
    id: str | Predicate[str]
    name: str | Predicate[str]
    size: int | Predicate[int]
    busid: int | Predicate[int]
class GroupUploadNoticeEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: Literal['group_upload'] | Predicate[Literal['group_upload']]
    group_id: int | Predicate[int]
    user_id: int | Predicate[int]
    file: GroupUploadFilePattern | Predicate[GroupUploadFile]
class HeartbeatEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['meta_event'] | Predicate[Literal['meta_event']]
    meta_event_type: Literal['heartbeat'] | Predicate[Literal['heartbeat']]
    status: HeartbeatStatusPattern | Predicate[HeartbeatStatus]
    interval: int | Predicate[int]
class HeartbeatStatusPattern(TypedDict, total=False):
    online: bool | None | Predicate[bool | None]
    good: bool | Predicate[bool]
class InputStatusEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: Literal['notify'] | Predicate[Literal['notify']]
    sub_type: Literal['input_status'] | Predicate[Literal['input_status']]
    status_text: Literal['对方正在输入...'] | str | Predicate[Literal['对方正在输入...'] | str]
    event_type: int | Predicate[int]
    user_id: int | Predicate[int]
    group_id: int | Predicate[int]
class LifecycleMetaEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['meta_event'] | Predicate[Literal['meta_event']]
    meta_event_type: Literal['lifecycle'] | Predicate[Literal['lifecycle']]
    sub_type: Literal['enable', 'disable', 'connect'] | Predicate[Literal['enable', 'disable', 'connect']]
class MessageEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['message', 'message_sent'] | tuple[str, str] | Predicate[Literal['message', 'message_sent'] | tuple[str, str]]
    message_id: int | Predicate[int]
    user_id: int | str | Predicate[int | str]
    message_seq: int | Predicate[int]
    real_id: int | Predicate[int]
    sender: MessageSenderPattern | Predicate[MessageSender]
    raw_message: str | Predicate[str]
    message: tuple[Message | UnknownMessageSegment, ...] | Predicate[tuple[Message | UnknownMessageSegment, ...]]
    message_format: Literal['array'] | Predicate[Literal['array']]
    font: int | Predicate[int]
    real_seq: str | None | Predicate[str | None]
    message_sent_type: str | None | Predicate[str | None]
    sub_type: Literal['friend', 'group', 'normal'] | str | None | Predicate[Literal['friend', 'group', 'normal'] | str | None]
    raw: Any | None | Predicate[Any | None]
    emoji_likes_list: list[EmojiLikeItem] | None | Predicate[list[EmojiLikeItem] | None]
class MessageSenderPattern(TypedDict, total=False):
    user_id: int | str | Predicate[int | str]
    nickname: str | Predicate[str]
    card: str | None | Predicate[str | None]
    role: Literal['owner', 'admin', 'member'] | str | None | Predicate[Literal['owner', 'admin', 'member'] | str | None]
    sex: Literal['male', 'female', 'unknown'] | str | None | Predicate[Literal['male', 'female', 'unknown'] | str | None]
    age: int | None | Predicate[int | None]
    area: str | None | Predicate[str | None]
    level: str | None | Predicate[str | None]
    title: str | None | Predicate[str | None]
class MetaEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['meta_event'] | Predicate[Literal['meta_event']]
    meta_event_type: str | Predicate[str]
class MsgEmojiLikePattern(TypedDict, total=False):
    emoji_id: str | Predicate[str]
    count: int | Predicate[int]
class NapCatEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: str | tuple[str, ...] | Predicate[str | tuple[str, ...]]
class NoticeEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: str | Predicate[str]
class OnlineFileNoticeEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: str | Predicate[str]
    peer_id: int | Predicate[int]
class OnlineFileReceiveEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: Literal['online_file_receive'] | Predicate[Literal['online_file_receive']]
    peer_id: int | Predicate[int]
    sub_type: Literal['cancel'] | Predicate[Literal['cancel']]
class OnlineFileSendEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: Literal['online_file_send'] | Predicate[Literal['online_file_send']]
    peer_id: int | Predicate[int]
    sub_type: Literal['receive', 'refuse'] | Predicate[Literal['receive', 'refuse']]
class PokeEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: Literal['notify'] | Predicate[Literal['notify']]
    sub_type: Literal['poke'] | Predicate[Literal['poke']]
    target_id: int | Predicate[int]
    user_id: int | Predicate[int]
class PrivateMessageEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['message', 'message_sent'] | tuple[str, str] | Predicate[Literal['message', 'message_sent'] | tuple[str, str]]
    message_id: int | Predicate[int]
    user_id: int | str | Predicate[int | str]
    message_seq: int | Predicate[int]
    real_id: int | Predicate[int]
    sender: MessageSenderPattern | Predicate[MessageSender]
    raw_message: str | Predicate[str]
    message: tuple[Message | UnknownMessageSegment, ...] | Predicate[tuple[Message | UnknownMessageSegment, ...]]
    message_format: Literal['array'] | Predicate[Literal['array']]
    font: int | Predicate[int]
    real_seq: str | None | Predicate[str | None]
    message_sent_type: str | None | Predicate[str | None]
    sub_type: Literal['friend', 'group'] | str | None | Predicate[Literal['friend', 'group'] | str | None]
    raw: Any | None | Predicate[Any | None]
    emoji_likes_list: list[EmojiLikeItem] | None | Predicate[list[EmojiLikeItem] | None]
    target_id: int | None | Predicate[int | None]
    temp_source: int | None | Predicate[int | None]
    group_id: int | str | None | Predicate[int | str | None]
    message_type: Literal['private'] | Predicate[Literal['private']]
class ProfileLikeEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: Literal['notify'] | Predicate[Literal['notify']]
    sub_type: Literal['profile_like'] | Predicate[Literal['profile_like']]
    operator_id: int | Predicate[int]
    operator_nick: str | Predicate[str]
    times: int | Predicate[int]
class RequestEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['request'] | Predicate[Literal['request']]
    request_type: str | Predicate[str]
class UnknownEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: str | Predicate[str]
    raw_data: dict[str, Any] | Predicate[dict[str, Any]]
class UnknownMessageSegmentPattern(TypedDict, total=False):
    raw_type: str | Predicate[str]
    raw_data: dict[str, Any] | Predicate[dict[str, Any]]
class UnknownNoticeEventPattern(TypedDict, total=False):
    time: int | Predicate[int]
    self_id: int | Predicate[int]
    post_type: Literal['notice'] | Predicate[Literal['notice']]
    notice_type: str | Predicate[str]
    raw_data: dict[str, Any] | Predicate[dict[str, Any]]

@overload
def event_match(
    event_type: type[BotOfflineEvent],
    /,
    **pattern: Unpack[BotOfflineEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[FriendAddNoticeEvent],
    /,
    **pattern: Unpack[FriendAddNoticeEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[FriendPokeEvent],
    /,
    **pattern: Unpack[FriendPokeEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[FriendRecallNoticeEvent],
    /,
    **pattern: Unpack[FriendRecallNoticeEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[FriendRequestEvent],
    /,
    **pattern: Unpack[FriendRequestEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[GroupAdminNoticeEvent],
    /,
    **pattern: Unpack[GroupAdminNoticeEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[GroupBanEvent],
    /,
    **pattern: Unpack[GroupBanEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[GroupCardEvent],
    /,
    **pattern: Unpack[GroupCardEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[GroupDecreaseEvent],
    /,
    **pattern: Unpack[GroupDecreaseEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[GroupEssenceEvent],
    /,
    **pattern: Unpack[GroupEssenceEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[GroupGrayTipEvent],
    /,
    **pattern: Unpack[GroupGrayTipEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[GroupIncreaseEvent],
    /,
    **pattern: Unpack[GroupIncreaseEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[GroupMessageEvent],
    /,
    **pattern: Unpack[GroupMessageEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[GroupMsgEmojiLikeEvent],
    /,
    **pattern: Unpack[GroupMsgEmojiLikeEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[GroupNameEvent],
    /,
    **pattern: Unpack[GroupNameEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[GroupNoticeEvent],
    /,
    **pattern: Unpack[GroupNoticeEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[GroupPokeEvent],
    /,
    **pattern: Unpack[GroupPokeEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[GroupRecallNoticeEvent],
    /,
    **pattern: Unpack[GroupRecallNoticeEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[GroupRequestEvent],
    /,
    **pattern: Unpack[GroupRequestEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[GroupTitleEvent],
    /,
    **pattern: Unpack[GroupTitleEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[GroupUploadNoticeEvent],
    /,
    **pattern: Unpack[GroupUploadNoticeEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[HeartbeatEvent],
    /,
    **pattern: Unpack[HeartbeatEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[InputStatusEvent],
    /,
    **pattern: Unpack[InputStatusEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[LifecycleMetaEvent],
    /,
    **pattern: Unpack[LifecycleMetaEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[MessageEvent],
    /,
    **pattern: Unpack[MessageEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[MetaEvent],
    /,
    **pattern: Unpack[MetaEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[NapCatEvent],
    /,
    **pattern: Unpack[NapCatEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[NoticeEvent],
    /,
    **pattern: Unpack[NoticeEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[OnlineFileNoticeEvent],
    /,
    **pattern: Unpack[OnlineFileNoticeEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[OnlineFileReceiveEvent],
    /,
    **pattern: Unpack[OnlineFileReceiveEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[OnlineFileSendEvent],
    /,
    **pattern: Unpack[OnlineFileSendEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[PokeEvent],
    /,
    **pattern: Unpack[PokeEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[PrivateMessageEvent],
    /,
    **pattern: Unpack[PrivateMessageEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[ProfileLikeEvent],
    /,
    **pattern: Unpack[ProfileLikeEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[RequestEvent],
    /,
    **pattern: Unpack[RequestEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[UnknownEvent],
    /,
    **pattern: Unpack[UnknownEventPattern],
) -> Callable[[NapCatEvent], bool]: ...
@overload
def event_match(
    event_type: type[UnknownNoticeEvent],
    /,
    **pattern: Unpack[UnknownNoticeEventPattern],
) -> Callable[[NapCatEvent], bool]: ...

@overload
def event_match(
    event_type: type[NapCatEvent],
    /,
    **pattern: Any,
) -> Callable[[NapCatEvent], bool]: ...

@overload
def event_match(
    event_type: UnionType,
    /,
    **pattern: Any,
) -> Callable[[NapCatEvent], bool]: ...

def event_match(
    event_type: type[NapCatEvent] | UnionType,
    /,
    **pattern: Any,
) -> Callable[[NapCatEvent], bool]: ...
