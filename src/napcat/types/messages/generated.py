"""
OneBot 11 Message Segments

自动生成的消息段定义 (dataclass)。
包含所有支持的消息段类型，例如 Text, Image, Face 等。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Literal, TypedDict

from .base import MessageSegment


class JsonDataConfig(TypedDict):
    token: str
    """
    token
    """


class NodeInlineDataNew(TypedDict):
    text: str
    """
    新闻文本
    """


@dataclass(slots=True, frozen=True, kw_only=True)
class At(MessageSegment):
    """
    @消息段
    """

    _type: ClassVar[str] = "at"
    qq: str
    """
    QQ号或all
    """
    name: str | None = None
    """
    显示名称
    """


@dataclass(slots=True, frozen=True, kw_only=True)
class Contact(MessageSegment):
    """
    联系人消息段
    """

    _type: ClassVar[str] = "contact"
    type: Literal["qq", "group"]
    """
    联系人类型
    """
    id: str
    """
    联系人ID
    """


@dataclass(slots=True, frozen=True, kw_only=True)
class CustomMusic(MessageSegment, register=False):
    """
    自定义音乐消息段
    """

    _type: ClassVar[str] = "music"
    type: Literal["qq", "163", "kugou", "migu", "kuwo", "custom"]
    """
    音乐平台类型
    """
    id: None
    url: str
    """
    点击后跳转URL
    """
    image: str
    """
    封面图片URL
    """
    audio: str | None = None
    """
    音频URL
    """
    title: str | None = None
    """
    音乐标题
    """
    content: str | None = None
    """
    音乐简介
    """


@dataclass(slots=True, frozen=True, kw_only=True)
class Dice(MessageSegment):
    """
    骰子消息段
    """

    _type: ClassVar[str] = "dice"
    result: int | str
    """
    骰子结果
    """


@dataclass(slots=True, frozen=True, kw_only=True)
class Face(MessageSegment):
    """
    QQ表情消息段
    """

    _type: ClassVar[str] = "face"
    id: str
    """
    表情ID
    """
    resultId: str | None = None
    """
    结果ID
    """
    chainCount: int | None = None
    """
    连击数
    """


@dataclass(slots=True, frozen=True, kw_only=True)
class File(MessageSegment):
    """
    文件消息段
    """

    _type: ClassVar[str] = "file"

    file: str
    """
    文件路径/URL/file:///
    """
    path: str | None = None
    """
    文件路径
    """
    url: str | None = None
    """
    文件URL
    """
    name: str | None = None
    """
    文件名
    """
    thumb: str | None = None
    """
    缩略图
    """


@dataclass(slots=True, frozen=True, kw_only=True)
class FlashTransfer(MessageSegment):
    """
    QQ闪传消息段
    """

    _type: ClassVar[str] = "flashtransfer"
    fileSetId: str
    """
    文件集ID
    """


@dataclass(slots=True, frozen=True, kw_only=True)
class Forward(MessageSegment):
    """
    合并转发消息段
    """

    _type: ClassVar[str] = "forward"
    id: str
    """
    合并转发ID
    """
    content: dict[str, Any] | None = None
    """
    消息内容 (OB11Message[])
    """


@dataclass(slots=True, frozen=True, kw_only=True)
class IdMusic(MessageSegment):
    """
    ID音乐消息段
    """

    _type: ClassVar[str] = "music"
    type: Literal["qq", "163", "kugou", "migu", "kuwo"]
    """
    音乐平台类型
    """
    id: str | int
    """
    音乐ID
    """


@dataclass(slots=True, frozen=True, kw_only=True)
class Image(MessageSegment):
    """
    图片消息段
    """

    _type: ClassVar[str] = "image"
    file: str
    """
    文件路径/URL/file:///
    """
    path: str | None = None
    """
    文件路径
    """
    url: str | None = None
    """
    文件URL
    """
    name: str | None = None
    """
    文件名
    """
    thumb: str | None = None
    """
    缩略图
    """
    summary: str | None = None
    """
    图片摘要
    """
    sub_type: int | None = None
    """
    图片子类型
    """


@dataclass(slots=True, frozen=True, kw_only=True)
class Json(MessageSegment):
    """
    JSON消息段
    """

    _type: ClassVar[str] = "json"
    data: str | dict[str, Any]
    """
    JSON数据
    """
    config: JsonDataConfig | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class Location(MessageSegment):
    """
    位置消息段
    """

    _type: ClassVar[str] = "location"
    lat: str | float
    """
    纬度
    """
    lon: str | float
    """
    经度
    """
    title: str | None = None
    """
    标题
    """
    content: str | None = None
    """
    内容
    """


@dataclass(slots=True, frozen=True, kw_only=True)
class MFace(MessageSegment):
    """
    商城表情消息段
    """

    _type: ClassVar[str] = "mface"
    emoji_package_id: int
    """
    表情包ID
    """
    emoji_id: str
    """
    表情ID
    """
    key: str
    """
    表情key
    """
    summary: str
    """
    表情摘要
    """


@dataclass(slots=True, frozen=True, kw_only=True)
class Markdown(MessageSegment):
    """
    Markdown消息段
    """

    _type: ClassVar[str] = "markdown"
    content: str
    """
    Markdown内容
    """


@dataclass(slots=True, frozen=True, kw_only=True)
class MiniApp(MessageSegment):
    """
    小程序消息段
    """

    _type: ClassVar[str] = "miniapp"
    data: str
    """
    小程序数据
    """


@dataclass(slots=True, frozen=True, kw_only=True)
class NodeReference(MessageSegment, register=False):
    """
    引用已有消息的合并转发节点
    """

    _type: ClassVar[str] = "node"
    id: str
    """
    转发消息ID
    """


@dataclass(slots=True, frozen=True, kw_only=True)
class NodeInline(MessageSegment, register=False):
    """
    内联合并转发消息节点
    """

    _type: ClassVar[str] = "node"
    content: dict[str, Any]
    """
    消息内容 (OB11MessageMixType)
    """
    user_id: int | str | None = None
    """
    发送者QQ号
    """
    uin: int | str | None = None
    """
    发送者QQ号(兼容go-cqhttp)
    """
    nickname: str | None = None
    """
    发送者昵称
    """
    name: str | None = None
    """
    发送者昵称(兼容go-cqhttp)
    """
    source: str | None = None
    """
    消息来源
    """
    news: list[NodeInlineDataNew] | None = None
    summary: str | None = None
    """
    摘要
    """
    prompt: str | None = None
    """
    提示
    """
    time: str | int | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class OnlineFile(MessageSegment):
    """
    在线文件消息段
    """

    _type: ClassVar[str] = "onlinefile"
    msgId: str
    """
    消息ID
    """
    elementId: str
    """
    元素ID
    """
    fileName: str
    """
    文件名
    """
    fileSize: str
    """
    文件大小
    """
    isDir: bool
    """
    是否为目录
    """


@dataclass(slots=True, frozen=True, kw_only=True)
class Poke(MessageSegment):
    """
    戳一戳消息段
    """

    _type: ClassVar[str] = "poke"
    type: str
    """
    戳一戳类型
    """
    id: str
    """
    戳一戳ID
    """


@dataclass(slots=True, frozen=True, kw_only=True)
class RPS(MessageSegment):
    """
    猜拳消息段
    """

    _type: ClassVar[str] = "rps"
    result: int | str
    """
    猜拳结果
    """


@dataclass(slots=True, frozen=True, kw_only=True)
class Record(MessageSegment):
    """
    语音消息段
    """

    _type: ClassVar[str] = "record"

    file: str
    """
    文件路径/URL/file:///
    """
    path: str | None = None
    """
    文件路径
    """
    url: str | None = None
    """
    文件URL
    """
    name: str | None = None
    """
    文件名
    """
    thumb: str | None = None
    """
    缩略图
    """


@dataclass(slots=True, frozen=True, kw_only=True)
class Reply(MessageSegment):
    """
    回复消息段
    """

    _type: ClassVar[str] = "reply"
    id: str | None = None
    """
    消息ID的短ID映射
    """
    seq: int | None = None
    """
    消息序列号，优先使用
    """


@dataclass(slots=True, frozen=True, kw_only=True)
class Text(MessageSegment):
    """
    纯文本消息段
    """

    _type: ClassVar[str] = "text"
    text: str
    """
    纯文本内容
    """


@dataclass(slots=True, frozen=True, kw_only=True)
class Video(MessageSegment):
    """
    视频消息段
    """

    _type: ClassVar[str] = "video"

    file: str
    """
    文件路径/URL/file:///
    """
    path: str | None = None
    """
    文件路径
    """
    url: str | None = None
    """
    文件URL
    """
    name: str | None = None
    """
    文件名
    """
    thumb: str | None = None
    """
    缩略图
    """


@dataclass(slots=True, frozen=True, kw_only=True)
class Xml(MessageSegment):
    """
    XML消息段
    """

    _type: ClassVar[str] = "xml"
    data: str
    """
    XML数据
    """


type Node = NodeReference | NodeInline
"""
合并转发消息节点
"""


type Message = (
    Text
    | Face
    | MFace
    | At
    | Reply
    | Image
    | Record
    | Video
    | File
    | IdMusic
    | CustomMusic
    | Poke
    | Dice
    | RPS
    | Contact
    | Location
    | Json
    | Xml
    | Markdown
    | MiniApp
    | Node
    | Forward
    | OnlineFile
    | FlashTransfer
)
"""
OneBot 11 消息段
"""
