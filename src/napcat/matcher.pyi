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

class Predicate[T]:
    def __call__(self, value: T, /) -> bool: ...
    def __or__(self, other: Callable[[T], bool] | Predicate[T], /) -> Predicate[T]: ...
    def __ror__(self, other: Callable[[T], bool] | Predicate[T], /) -> Predicate[T]: ...
    def __and__(self, other: Callable[[T], bool] | Predicate[T], /) -> Predicate[T]: ...
    def __rand__(self, other: Callable[[T], bool] | Predicate[T], /) -> Predicate[T]: ...

type PredicateLike[T] = Callable[[T], bool] | Predicate[T]

TRUE: Predicate[Any]
FALSE: Predicate[Any]

class BotOfflineEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: Literal['bot_offline'] | PredicateLike[Literal['bot_offline']]
    user_id: int | PredicateLike[int]
    tag: Literal['BotOfflineEvent'] | str | PredicateLike[Literal['BotOfflineEvent'] | str]
    message: Literal['BotOfflineEvent'] | str | PredicateLike[Literal['BotOfflineEvent'] | str]
class EmojiLikeItemPattern(TypedDict, total=False):
    emoji_id: str | PredicateLike[str]
    emoji_type: str | PredicateLike[str]
    likes_cnt: str | PredicateLike[str]
class FriendAddNoticeEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: Literal['friend_add'] | PredicateLike[Literal['friend_add']]
    user_id: int | PredicateLike[int]
class FriendPokeEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: Literal['notify'] | PredicateLike[Literal['notify']]
    sub_type: Literal['poke'] | PredicateLike[Literal['poke']]
    target_id: int | PredicateLike[int]
    user_id: int | PredicateLike[int]
    raw_info: Any | PredicateLike[Any]
    sender_id: int | PredicateLike[int]
class FriendRecallNoticeEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: Literal['friend_recall'] | PredicateLike[Literal['friend_recall']]
    user_id: int | PredicateLike[int]
    message_id: int | PredicateLike[int]
class FriendRequestEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['request'] | PredicateLike[Literal['request']]
    request_type: Literal['friend'] | PredicateLike[Literal['friend']]
    user_id: int | PredicateLike[int]
    comment: str | PredicateLike[str]
    flag: str | PredicateLike[str]
class GroupAdminNoticeEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: Literal['group_admin'] | PredicateLike[Literal['group_admin']]
    group_id: int | PredicateLike[int]
    user_id: int | PredicateLike[int]
    sub_type: Literal['set', 'unset'] | PredicateLike[Literal['set', 'unset']]
class GroupBanEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: Literal['group_ban'] | PredicateLike[Literal['group_ban']]
    group_id: int | PredicateLike[int]
    user_id: int | PredicateLike[int]
    operator_id: int | PredicateLike[int]
    duration: int | PredicateLike[int]
    sub_type: Literal['ban', 'lift_ban'] | PredicateLike[Literal['ban', 'lift_ban']]
class GroupCardEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: Literal['group_card'] | PredicateLike[Literal['group_card']]
    group_id: int | PredicateLike[int]
    user_id: int | PredicateLike[int]
    card_new: str | PredicateLike[str]
    card_old: str | PredicateLike[str]
class GroupDecreaseEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: Literal['group_decrease'] | PredicateLike[Literal['group_decrease']]
    group_id: int | PredicateLike[int]
    user_id: int | PredicateLike[int]
    sub_type: Literal['leave', 'kick', 'kick_me', 'disband'] | PredicateLike[Literal['leave', 'kick', 'kick_me', 'disband']]
    operator_id: int | PredicateLike[int]
class GroupEssenceEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: Literal['essence'] | PredicateLike[Literal['essence']]
    group_id: int | PredicateLike[int]
    user_id: int | PredicateLike[int]
    message_id: int | PredicateLike[int]
    sender_id: int | PredicateLike[int]
    operator_id: int | PredicateLike[int]
    sub_type: Literal['add', 'delete'] | PredicateLike[Literal['add', 'delete']]
class GroupGrayTipEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: Literal['notify'] | PredicateLike[Literal['notify']]
    sub_type: Literal['gray_tip'] | PredicateLike[Literal['gray_tip']]
    group_id: int | PredicateLike[int]
    user_id: int | PredicateLike[int]
    message_id: int | PredicateLike[int]
    busi_id: str | PredicateLike[str]
    content: str | PredicateLike[str]
    raw_info: Any | PredicateLike[Any]
class GroupIncreaseEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: Literal['group_increase'] | PredicateLike[Literal['group_increase']]
    group_id: int | PredicateLike[int]
    user_id: int | PredicateLike[int]
    operator_id: int | PredicateLike[int]
    sub_type: Literal['approve', 'invite'] | PredicateLike[Literal['approve', 'invite']]
class GroupMessageEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['message', 'message_sent'] | tuple[str, str] | PredicateLike[Literal['message', 'message_sent'] | tuple[str, str]]
    message_id: int | PredicateLike[int]
    user_id: int | str | PredicateLike[int | str]
    message_seq: int | PredicateLike[int]
    real_id: int | PredicateLike[int]
    sender: MessageSenderPattern | PredicateLike[MessageSender]
    raw_message: str | PredicateLike[str]
    message: tuple[Message | UnknownMessageSegment, ...] | PredicateLike[tuple[Message | UnknownMessageSegment, ...]]
    message_format: Literal['array'] | PredicateLike[Literal['array']]
    font: int | PredicateLike[int]
    real_seq: str | None | PredicateLike[str | None]
    message_sent_type: str | None | PredicateLike[str | None]
    sub_type: Literal['normal'] | str | None | PredicateLike[Literal['normal'] | str | None]
    raw: Any | None | PredicateLike[Any | None]
    emoji_likes_list: list[EmojiLikeItem] | None | PredicateLike[list[EmojiLikeItem] | None]
    group_id: int | PredicateLike[int]
    group_name: str | None | PredicateLike[str | None]
    target_id: int | None | PredicateLike[int | None]
    message_type: Literal['group'] | PredicateLike[Literal['group']]
class GroupMsgEmojiLikeEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: Literal['group_msg_emoji_like'] | PredicateLike[Literal['group_msg_emoji_like']]
    group_id: int | PredicateLike[int]
    user_id: int | PredicateLike[int]
    message_id: int | PredicateLike[int]
    likes: list[MsgEmojiLike] | PredicateLike[list[MsgEmojiLike]]
    is_add: bool | PredicateLike[bool]
    message_seq: str | None | PredicateLike[str | None]
class GroupNameEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: Literal['notify'] | PredicateLike[Literal['notify']]
    group_id: int | PredicateLike[int]
    user_id: int | PredicateLike[int]
    sub_type: Literal['group_name'] | PredicateLike[Literal['group_name']]
    name_new: str | PredicateLike[str]
class GroupNoticeEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: str | PredicateLike[str]
    group_id: int | PredicateLike[int]
    user_id: int | PredicateLike[int]
class GroupPokeEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: Literal['notify'] | PredicateLike[Literal['notify']]
    sub_type: Literal['poke'] | PredicateLike[Literal['poke']]
    target_id: int | PredicateLike[int]
    user_id: int | PredicateLike[int]
    group_id: int | PredicateLike[int]
    raw_info: Any | PredicateLike[Any]
class GroupRecallNoticeEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: Literal['group_recall'] | PredicateLike[Literal['group_recall']]
    group_id: int | PredicateLike[int]
    user_id: int | PredicateLike[int]
    operator_id: int | PredicateLike[int]
    message_id: int | PredicateLike[int]
class GroupRequestEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['request'] | PredicateLike[Literal['request']]
    request_type: Literal['group'] | PredicateLike[Literal['group']]
    group_id: int | PredicateLike[int]
    user_id: int | PredicateLike[int]
    sub_type: Literal['add', 'invite'] | str | PredicateLike[Literal['add', 'invite'] | str]
    comment: str | PredicateLike[str]
    flag: str | PredicateLike[str]
class GroupTitleEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: Literal['notify'] | PredicateLike[Literal['notify']]
    group_id: int | PredicateLike[int]
    user_id: int | PredicateLike[int]
    sub_type: Literal['title'] | PredicateLike[Literal['title']]
    title: str | PredicateLike[str]
class GroupUploadFilePattern(TypedDict, total=False):
    id: str | PredicateLike[str]
    name: str | PredicateLike[str]
    size: int | PredicateLike[int]
    busid: int | PredicateLike[int]
class GroupUploadNoticeEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: Literal['group_upload'] | PredicateLike[Literal['group_upload']]
    group_id: int | PredicateLike[int]
    user_id: int | PredicateLike[int]
    file: GroupUploadFilePattern | PredicateLike[GroupUploadFile]
class HeartbeatEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['meta_event'] | PredicateLike[Literal['meta_event']]
    meta_event_type: Literal['heartbeat'] | PredicateLike[Literal['heartbeat']]
    status: HeartbeatStatusPattern | PredicateLike[HeartbeatStatus]
    interval: int | PredicateLike[int]
class HeartbeatStatusPattern(TypedDict, total=False):
    online: bool | None | PredicateLike[bool | None]
    good: bool | PredicateLike[bool]
class InputStatusEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: Literal['notify'] | PredicateLike[Literal['notify']]
    sub_type: Literal['input_status'] | PredicateLike[Literal['input_status']]
    status_text: Literal['对方正在输入...'] | str | PredicateLike[Literal['对方正在输入...'] | str]
    event_type: int | PredicateLike[int]
    user_id: int | PredicateLike[int]
    group_id: int | PredicateLike[int]
class LifecycleMetaEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['meta_event'] | PredicateLike[Literal['meta_event']]
    meta_event_type: Literal['lifecycle'] | PredicateLike[Literal['lifecycle']]
    sub_type: Literal['enable', 'disable', 'connect'] | PredicateLike[Literal['enable', 'disable', 'connect']]
class MessageEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['message', 'message_sent'] | tuple[str, str] | PredicateLike[Literal['message', 'message_sent'] | tuple[str, str]]
    message_id: int | PredicateLike[int]
    user_id: int | str | PredicateLike[int | str]
    message_seq: int | PredicateLike[int]
    real_id: int | PredicateLike[int]
    sender: MessageSenderPattern | PredicateLike[MessageSender]
    raw_message: str | PredicateLike[str]
    message: tuple[Message | UnknownMessageSegment, ...] | PredicateLike[tuple[Message | UnknownMessageSegment, ...]]
    message_format: Literal['array'] | PredicateLike[Literal['array']]
    font: int | PredicateLike[int]
    real_seq: str | None | PredicateLike[str | None]
    message_sent_type: str | None | PredicateLike[str | None]
    sub_type: Literal['friend', 'group', 'normal'] | str | None | PredicateLike[Literal['friend', 'group', 'normal'] | str | None]
    raw: Any | None | PredicateLike[Any | None]
    emoji_likes_list: list[EmojiLikeItem] | None | PredicateLike[list[EmojiLikeItem] | None]
class MessageSenderPattern(TypedDict, total=False):
    user_id: int | str | PredicateLike[int | str]
    nickname: str | PredicateLike[str]
    card: str | None | PredicateLike[str | None]
    role: Literal['owner', 'admin', 'member'] | str | None | PredicateLike[Literal['owner', 'admin', 'member'] | str | None]
    sex: Literal['male', 'female', 'unknown'] | str | None | PredicateLike[Literal['male', 'female', 'unknown'] | str | None]
    age: int | None | PredicateLike[int | None]
    area: str | None | PredicateLike[str | None]
    level: str | None | PredicateLike[str | None]
    title: str | None | PredicateLike[str | None]
class MetaEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['meta_event'] | PredicateLike[Literal['meta_event']]
    meta_event_type: str | PredicateLike[str]
class MsgEmojiLikePattern(TypedDict, total=False):
    emoji_id: str | PredicateLike[str]
    count: int | PredicateLike[int]
class NapCatEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: str | tuple[str, ...] | PredicateLike[str | tuple[str, ...]]
class NoticeEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: str | PredicateLike[str]
class OnlineFileNoticeEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: str | PredicateLike[str]
    peer_id: int | PredicateLike[int]
class OnlineFileReceiveEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: Literal['online_file_receive'] | PredicateLike[Literal['online_file_receive']]
    peer_id: int | PredicateLike[int]
    sub_type: Literal['cancel'] | PredicateLike[Literal['cancel']]
class OnlineFileSendEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: Literal['online_file_send'] | PredicateLike[Literal['online_file_send']]
    peer_id: int | PredicateLike[int]
    sub_type: Literal['receive', 'refuse'] | PredicateLike[Literal['receive', 'refuse']]
class PokeEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: Literal['notify'] | PredicateLike[Literal['notify']]
    sub_type: Literal['poke'] | PredicateLike[Literal['poke']]
    target_id: int | PredicateLike[int]
    user_id: int | PredicateLike[int]
class PrivateMessageEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['message', 'message_sent'] | tuple[str, str] | PredicateLike[Literal['message', 'message_sent'] | tuple[str, str]]
    message_id: int | PredicateLike[int]
    user_id: int | str | PredicateLike[int | str]
    message_seq: int | PredicateLike[int]
    real_id: int | PredicateLike[int]
    sender: MessageSenderPattern | PredicateLike[MessageSender]
    raw_message: str | PredicateLike[str]
    message: tuple[Message | UnknownMessageSegment, ...] | PredicateLike[tuple[Message | UnknownMessageSegment, ...]]
    message_format: Literal['array'] | PredicateLike[Literal['array']]
    font: int | PredicateLike[int]
    real_seq: str | None | PredicateLike[str | None]
    message_sent_type: str | None | PredicateLike[str | None]
    sub_type: Literal['friend', 'group'] | str | None | PredicateLike[Literal['friend', 'group'] | str | None]
    raw: Any | None | PredicateLike[Any | None]
    emoji_likes_list: list[EmojiLikeItem] | None | PredicateLike[list[EmojiLikeItem] | None]
    target_id: int | None | PredicateLike[int | None]
    temp_source: int | None | PredicateLike[int | None]
    group_id: int | str | None | PredicateLike[int | str | None]
    message_type: Literal['private'] | PredicateLike[Literal['private']]
class ProfileLikeEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: Literal['notify'] | PredicateLike[Literal['notify']]
    sub_type: Literal['profile_like'] | PredicateLike[Literal['profile_like']]
    operator_id: int | PredicateLike[int]
    operator_nick: str | PredicateLike[str]
    times: int | PredicateLike[int]
class RequestEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['request'] | PredicateLike[Literal['request']]
    request_type: str | PredicateLike[str]
class UnknownEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: str | PredicateLike[str]
    raw_data: dict[str, Any] | PredicateLike[dict[str, Any]]
class UnknownMessageSegmentPattern(TypedDict, total=False):
    raw_type: str | PredicateLike[str]
    raw_data: dict[str, Any] | PredicateLike[dict[str, Any]]
class UnknownNoticeEventPattern(TypedDict, total=False):
    time: int | PredicateLike[int]
    self_id: int | PredicateLike[int]
    post_type: Literal['notice'] | PredicateLike[Literal['notice']]
    notice_type: str | PredicateLike[str]
    raw_data: dict[str, Any] | PredicateLike[dict[str, Any]]

@overload
def event_match(
    event_type: type[BotOfflineEvent],
    /,
    **pattern: Unpack[BotOfflineEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[FriendAddNoticeEvent],
    /,
    **pattern: Unpack[FriendAddNoticeEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[FriendPokeEvent],
    /,
    **pattern: Unpack[FriendPokeEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[FriendRecallNoticeEvent],
    /,
    **pattern: Unpack[FriendRecallNoticeEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[FriendRequestEvent],
    /,
    **pattern: Unpack[FriendRequestEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[GroupAdminNoticeEvent],
    /,
    **pattern: Unpack[GroupAdminNoticeEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[GroupBanEvent],
    /,
    **pattern: Unpack[GroupBanEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[GroupCardEvent],
    /,
    **pattern: Unpack[GroupCardEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[GroupDecreaseEvent],
    /,
    **pattern: Unpack[GroupDecreaseEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[GroupEssenceEvent],
    /,
    **pattern: Unpack[GroupEssenceEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[GroupGrayTipEvent],
    /,
    **pattern: Unpack[GroupGrayTipEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[GroupIncreaseEvent],
    /,
    **pattern: Unpack[GroupIncreaseEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[GroupMessageEvent],
    /,
    **pattern: Unpack[GroupMessageEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[GroupMsgEmojiLikeEvent],
    /,
    **pattern: Unpack[GroupMsgEmojiLikeEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[GroupNameEvent],
    /,
    **pattern: Unpack[GroupNameEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[GroupNoticeEvent],
    /,
    **pattern: Unpack[GroupNoticeEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[GroupPokeEvent],
    /,
    **pattern: Unpack[GroupPokeEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[GroupRecallNoticeEvent],
    /,
    **pattern: Unpack[GroupRecallNoticeEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[GroupRequestEvent],
    /,
    **pattern: Unpack[GroupRequestEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[GroupTitleEvent],
    /,
    **pattern: Unpack[GroupTitleEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[GroupUploadNoticeEvent],
    /,
    **pattern: Unpack[GroupUploadNoticeEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[HeartbeatEvent],
    /,
    **pattern: Unpack[HeartbeatEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[InputStatusEvent],
    /,
    **pattern: Unpack[InputStatusEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[LifecycleMetaEvent],
    /,
    **pattern: Unpack[LifecycleMetaEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[MessageEvent],
    /,
    **pattern: Unpack[MessageEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[MetaEvent],
    /,
    **pattern: Unpack[MetaEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[NapCatEvent],
    /,
    **pattern: Unpack[NapCatEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[NoticeEvent],
    /,
    **pattern: Unpack[NoticeEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[OnlineFileNoticeEvent],
    /,
    **pattern: Unpack[OnlineFileNoticeEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[OnlineFileReceiveEvent],
    /,
    **pattern: Unpack[OnlineFileReceiveEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[OnlineFileSendEvent],
    /,
    **pattern: Unpack[OnlineFileSendEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[PokeEvent],
    /,
    **pattern: Unpack[PokeEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[PrivateMessageEvent],
    /,
    **pattern: Unpack[PrivateMessageEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[ProfileLikeEvent],
    /,
    **pattern: Unpack[ProfileLikeEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[RequestEvent],
    /,
    **pattern: Unpack[RequestEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[UnknownEvent],
    /,
    **pattern: Unpack[UnknownEventPattern],
) -> Predicate[NapCatEvent]: ...
@overload
def event_match(
    event_type: type[UnknownNoticeEvent],
    /,
    **pattern: Unpack[UnknownNoticeEventPattern],
) -> Predicate[NapCatEvent]: ...

@overload
def event_match(
    event_type: type[NapCatEvent],
    /,
    **pattern: Any,
) -> Predicate[NapCatEvent]: ...

@overload
def event_match(
    event_type: UnionType,
    /,
    **pattern: Any,
) -> Predicate[NapCatEvent]: ...

def event_match(
    event_type: type[NapCatEvent] | UnionType,
    /,
    **pattern: Any,
) -> Predicate[NapCatEvent]: ...
