# src/napcat/types/events/__init__.py

"""统一导出所有事件类"""

from .base import NapCatEvent, UnknownEvent
from .meta import MetaEvent, LifecycleMetaEvent, HeartbeatEvent, HeartbeatStatus
from .message import MessageEvent, PrivateMessageEvent, GroupMessageEvent, MessageSender
from .request import RequestEvent, FriendRequestEvent, GroupRequestEvent
from .notice import (
    # >>> AUTO-GENERATED: NOTICE IMPORTS START
    BotOfflineEvent,
    FriendAddNoticeEvent,
    FriendPokeEvent,
    FriendRecallNoticeEvent,
    GroupAdminNoticeEvent,
    GroupBanEvent,
    GroupCardEvent,
    GroupDecreaseEvent,
    GroupEssenceEvent,
    GroupGrayTipEvent,
    GroupIncreaseEvent,
    GroupMsgEmojiLikeEvent,
    GroupNameEvent,
    GroupNoticeEvent,
    GroupPokeEvent,
    GroupRecallNoticeEvent,
    GroupTitleEvent,
    GroupUploadFile,
    GroupUploadNoticeEvent,
    InputStatusEvent,
    MsgEmojiLike,
    NoticeEvent,
    OnlineFileNoticeEvent,
    OnlineFileReceiveEvent,
    OnlineFileSendEvent,
    PokeEvent,
    ProfileLikeEvent,
    UnknownNoticeEvent,
    # <<< AUTO-GENERATED: NOTICE IMPORTS END
)

__all__ = [
    # Base
    "NapCatEvent",
    "UnknownEvent",
    # Meta Events
    "MetaEvent",
    "LifecycleMetaEvent",
    "HeartbeatEvent",
    "HeartbeatStatus",
    # Message Events
    "MessageEvent",
    "PrivateMessageEvent",
    "GroupMessageEvent",
    "MessageSender",
    # Request Events
    "RequestEvent",
    "FriendRequestEvent",
    "GroupRequestEvent",
    # Notice Events
    # >>> AUTO-GENERATED: NOTICE EXPORTS START
    "BotOfflineEvent",
    "FriendAddNoticeEvent",
    "FriendPokeEvent",
    "FriendRecallNoticeEvent",
    "GroupAdminNoticeEvent",
    "GroupBanEvent",
    "GroupCardEvent",
    "GroupDecreaseEvent",
    "GroupEssenceEvent",
    "GroupGrayTipEvent",
    "GroupIncreaseEvent",
    "GroupMsgEmojiLikeEvent",
    "GroupNameEvent",
    "GroupNoticeEvent",
    "GroupPokeEvent",
    "GroupRecallNoticeEvent",
    "GroupTitleEvent",
    "GroupUploadFile",
    "GroupUploadNoticeEvent",
    "InputStatusEvent",
    "MsgEmojiLike",
    "NoticeEvent",
    "OnlineFileNoticeEvent",
    "OnlineFileReceiveEvent",
    "OnlineFileSendEvent",
    "PokeEvent",
    "ProfileLikeEvent",
    "UnknownNoticeEvent",
    # <<< AUTO-GENERATED: NOTICE EXPORTS END
]
