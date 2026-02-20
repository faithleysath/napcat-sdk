"""
NapCat Python SDK

NapCat SDK 是一个用于与 NapCatQQ (OneBot 11) 进行交互的 Python SDK。
它提供了基于 WebSocket 的客户端和反向 WebSocket 服务器实现，以及完整的类型定义。

主要组件:
- NapCatClient: 主动连接 NapCat 的客户端
- ReverseWebSocketServer: 接收 NapCat 反向连接的服务器
- types: 包含所有 OneBot 11 事件和消息类型的定义
"""

# src/napcat/__init__.py

__version__ = "0.6.4"

from . import types
from .client import NapCatClient
from .exceptions import (
    NapCatAPIError,
    NapCatError,
    NapCatProtocolError,
    NapCatStateError,
)
from .server import ReverseWebSocketServer

# 统一透传 types 的全量导出（自动更新）
from .types import *

__all__ = [
    "NapCatClient",
    "ReverseWebSocketServer",
    "NapCatError",
    "NapCatAPIError",
    "NapCatProtocolError",
    "NapCatStateError",
    # >>> AUTO-GENERATED: TYPES EXPORTS START
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
    # <<< AUTO-GENERATED: TYPES EXPORTS END
    "types",
]
