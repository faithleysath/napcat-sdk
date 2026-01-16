# src/napcat/__init__.py

# 1. 暴露版本号 (可选，建议加)
__version__ = "0.2.6"

# 2. 核心功能组件
from .client import NapCatClient
from .server import ReverseWebSocketServer

# 3. 常用类型快捷导入
# 用户经常需要判断事件类型或构建消息，直接放在顶层很方便
from .types import (
    # 事件基类与常用事件
    NapCatEvent,
    MessageEvent,
    GroupMessageEvent,
    PrivateMessageEvent,
    MetaEvent,
    # 消息段构造器
    MessageSegment,
)

# 4. 如果用户需要更深层的类型，可以保留 types 模块本身
from . import types

# 5. 定义 __all__ 控制 `from napcat import *` 的行为
# 这对 IDE 的代码提示也非常友好
__all__ = [
    # Core
    "NapCatClient",
    "ReverseWebSocketServer",
    
    # Common Events
    "NapCatEvent",
    "MessageEvent",
    "GroupMessageEvent",
    "PrivateMessageEvent",
    "MetaEvent",
    
    # Messaging
    "MessageSegment",
    
    # Modules
    "types",
]