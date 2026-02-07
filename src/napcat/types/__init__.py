# src/napcat/types/__init__.py

"""Top-level typed exports.

This file should expose the most complete public surface:
- all events (from .events.__all__)
- all message segments (from .messages.__all__)
"""

from .events import *
from .messages import *

__all__ = [
    # >>> AUTO-GENERATED: EVENTS EXPORTS START
    "NapCatEvent",
    "UnknownEvent",
    "MetaEvent",
    "LifecycleMetaEvent",
    "HeartbeatEvent",
    "HeartbeatStatus",
    "MessageEvent",
    "PrivateMessageEvent",
    "GroupMessageEvent",
    "MessageSender",
    "RequestEvent",
    "FriendRequestEvent",
    "GroupRequestEvent",
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
    # <<< AUTO-GENERATED: EVENTS EXPORTS END
    # >>> AUTO-GENERATED: MESSAGE EXPORTS START
    "MessageSegment",
    "UnknownMessageSegment",
    "At",
    "Contact",
    "CustomMusic",
    "Dice",
    "Face",
    "File",
    "FlashTransfer",
    "Forward",
    "IdMusic",
    "Image",
    "Json",
    "Location",
    "MFace",
    "Markdown",
    "Message",
    "MiniApp",
    "Node",
    "OnlineFile",
    "Poke",
    "RPS",
    "Record",
    "Reply",
    "Text",
    "Video",
    "Xml",
    # <<< AUTO-GENERATED: MESSAGE EXPORTS END
]
