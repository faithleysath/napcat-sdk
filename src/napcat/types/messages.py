from __future__ import annotations
import builtins
from abc import ABC
import sys
from dataclasses import dataclass
from enum import IntEnum
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    ClassVar,
    Literal,
    LiteralString,
    NotRequired,
    TypedDict,
    Unpack,
    cast,
    get_type_hints,
)

from .utils import IgnoreExtraArgsMixin, TypeValidatorMixin


class ImageSubType(IntEnum):
    """图片子类型"""

    NORMAL = 0  # 普通图片
    MEME = 1  # 表情包/斗图


@dataclass(slots=True, frozen=True, kw_only=True)
class SegmentDataBase(TypeValidatorMixin, IgnoreExtraArgsMixin):
    pass


class SegmentDataTypeBase(TypedDict):
    pass


@dataclass(slots=True, frozen=True, kw_only=True)
class UnknownData(SegmentDataBase):
    """用于存放未知消息段的原始数据"""

    raw: dict[str, Any]

    # 覆盖 from_dict，直接把整个字典塞进 raw，不进行过滤
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UnknownData:
        return cls(raw=data)


class UnknownDataType(SegmentDataTypeBase):
    raw: dict[str, Any]


@dataclass(slots=True, frozen=True, kw_only=True)
class TextData(SegmentDataBase):
    text: str


class TextDataType(SegmentDataTypeBase):
    text: str


@dataclass(slots=True, frozen=True, kw_only=True)
class ReplyData(SegmentDataBase):
    id: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReplyData:
        # 1. 先准备好数据，这样这部分逻辑不用写两遍
        new_data = data | {"id": int(data["id"])}

        # 2. 根据 Python 版本自动切换
        if sys.version_info >= (3, 14):
            # 3.14+: 优雅写法
            return super().from_dict(new_data)
        else:
            # <3.14: 丑陋写法 (兼容 3.12 Bug)
            return IgnoreExtraArgsMixin.from_dict.__func__(cls, new_data)


class ReplyDataType(SegmentDataTypeBase):
    id: int


@dataclass(slots=True, frozen=True, kw_only=True)
class ImageData(SegmentDataBase):
    file: Annotated[
        str,
        '如果是接收，则通常是MD5.jpg。如果是发送，"file://D:/a.jpg"、"http://xxx.png"、"base64://xxxxxxxx"',
    ]
    sub_type: ImageSubType = ImageSubType.NORMAL
    url: Annotated[str | None, "如果是发送，可以省略此项"] = None
    file_size: Annotated[int | None, "如果是发送，可以省略此项"] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ImageData:
        new_data = data | {
            "sub_type": ImageSubType(data.get("sub_type", 0)),
            "file_size": int(data.get("file_size", 0)),
        }

        if sys.version_info >= (3, 14):
            return super().from_dict(new_data)
        else:
            return IgnoreExtraArgsMixin.from_dict.__func__(cls, new_data)


class ImageDataType(SegmentDataTypeBase):
    file: str
    sub_type: NotRequired[int]
    url: NotRequired[str | None]
    file_size: NotRequired[int | None]


@dataclass(slots=True, frozen=True, kw_only=True)
class VideoData(SegmentDataBase):
    file: Annotated[
        str,
        '如果是接收，则通常是MD5.mp4。如果是发送，"file://D:/a.mp4"、"http://xxx.mp4"',
    ]
    url: Annotated[str | None, "如果是发送，可以省略此项"] = None
    file_size: Annotated[int | None, "如果是发送，可以省略此项"] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VideoData:
        new_data = data | {
            "file_size": int(data.get("file_size", 0)),
        }

        if sys.version_info >= (3, 14):
            return super().from_dict(new_data)
        else:
            return IgnoreExtraArgsMixin.from_dict.__func__(cls, new_data)


class VideoDataType(SegmentDataTypeBase):
    file: str
    url: NotRequired[str | None]
    file_size: NotRequired[int | None]


@dataclass(slots=True, frozen=True, kw_only=True)
class FileData(SegmentDataBase):
    file: str
    file_id: str
    url: Annotated[str | None, "私聊没有群聊有"] = None


class FileDataType(SegmentDataTypeBase):
    file: str
    file_id: str
    url: NotRequired[str | None]


@dataclass(slots=True, frozen=True, kw_only=True)
class AtData(SegmentDataBase):
    qq: int | Literal["all"]


class AtDataType(SegmentDataTypeBase):
    qq: int | Literal["all"]


@dataclass(slots=True, frozen=True, kw_only=True)
class ForwardData(SegmentDataBase):
    id: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ForwardData:
        new_data = data | {
            "id": str(data.get("id", 0)),
        }

        if sys.version_info >= (3, 14):
            return super().from_dict(new_data)
        else:
            return IgnoreExtraArgsMixin.from_dict.__func__(cls, new_data)


class ForwardDataType(SegmentDataTypeBase):
    id: str


@dataclass(slots=True, frozen=True, kw_only=True)
class MessageSegment[
    T_Type: LiteralString | str,
    T_Data: SegmentDataBase,
    T_DataType: SegmentDataTypeBase,
](ABC):
    type: T_Type
    data: T_Data

    _data_class: ClassVar[builtins.type[SegmentDataBase]]
    _registry: ClassVar[dict[str, builtins.type[MessageSegment[LiteralString | str, SegmentDataBase, SegmentDataTypeBase]]]] = {}

    def __init_subclass__(cls, **kwargs: Any):
        hints = get_type_hints(cls)
        data_cls = hints.get("data")

        if not data_cls:
            raise TypeError(f"Class {cls.__name__} missing type hint for 'data'")
        cls._data_class = data_cls

        _MISSING = object()
        type_val = getattr(cls, "type", _MISSING)

        if type_val is _MISSING:
            return

        if not isinstance(type_val, str):
            return

        if type_val in MessageSegment._registry:
            raise ValueError(f"Duplicate message type registered: {type_val}")

        MessageSegment._registry[type_val] = cls

    def __init__(self, **kwargs: Unpack[T_DataType]):  # type: ignore
        type_field = self.__class__.__dataclass_fields__["type"]
        object.__setattr__(self, "type", type_field.default)

        data_cls = self.__class__._data_class
        if not data_cls:
            raise ValueError(
                f"Class {self.__class__.__name__} missing type hint for 'data'"
            )

        data_inst = data_cls.from_dict(cast(dict[str, Any], kwargs))
        object.__setattr__(self, "data", data_inst)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> MessageSegment[Any, Any, Any]:
        seg_type = raw.get("type")
        if not isinstance(seg_type, str):
            raise ValueError("Invalid or missing 'type' field in message segment")
        data_payload = raw.get("data", {})
        if not isinstance(data_payload, dict):
            raise ValueError("Invalid message segment data")

        data_payload = cast(dict[str, Any], data_payload)

        target_cls = cls._registry.get(seg_type)
        if not target_cls:
            return UnknownMessageSegment(
                type=seg_type, data=UnknownData(raw=data_payload)
            )

        return target_cls(**data_payload)


@dataclass(slots=True, frozen=True, kw_only=True)
class UnknownMessageSegment(MessageSegment[str, UnknownData, UnknownDataType]):
    """表示未知的消息段"""

    type: str  # 这里不再是 Literal，而是动态字符串
    data: UnknownData  # 存放原始数据


@dataclass(slots=True, frozen=True, kw_only=True, init=False)
class TextMessageSegment(MessageSegment[Literal["text"], TextData, TextDataType]):
    data: TextData
    type: Literal["text"] = "text"

    if TYPE_CHECKING:
        _data_class: ClassVar[type[TextData]]

        def __init__(self, **kwargs: Unpack[TextDataType]): ...


@dataclass(slots=True, frozen=True, kw_only=True, init=False)
class ReplyMessageSegment(MessageSegment[Literal["reply"], ReplyData, ReplyDataType]):
    data: ReplyData
    type: Literal["reply"] = "reply"

    if TYPE_CHECKING:
        _data_class: ClassVar[type[ReplyData]]

        def __init__(self, **kwargs: Unpack[ReplyDataType]): ...


@dataclass(slots=True, frozen=True, kw_only=True, init=False)
class ImageMessageSegment(MessageSegment[Literal["image"], ImageData, ImageDataType]):
    data: ImageData
    type: Literal["image"] = "image"

    if TYPE_CHECKING:
        _data_class: ClassVar[type[ImageData]]

        def __init__(self, **kwargs: Unpack[ImageDataType]): ...


@dataclass(slots=True, frozen=True, kw_only=True, init=False)
class VideoMessageSegment(MessageSegment[Literal["video"], VideoData, VideoDataType]):
    data: VideoData
    type: Literal["video"] = "video"

    if TYPE_CHECKING:
        _data_class: ClassVar[type[VideoData]]

        def __init__(self, **kwargs: Unpack[VideoDataType]): ...


@dataclass(slots=True, frozen=True, kw_only=True, init=False)
class FileMessageSegment(MessageSegment[Literal["file"], FileData, FileDataType]):
    data: FileData
    type: Literal["file"] = "file"

    if TYPE_CHECKING:
        _data_class: ClassVar[type[FileData]]

        def __init__(self, **kwargs: Unpack[FileDataType]): ...


@dataclass(slots=True, frozen=True, kw_only=True, init=False)
class AtMessageSegment(MessageSegment[Literal["at"], AtData, AtDataType]):
    data: AtData
    type: Literal["at"] = "at"

    if TYPE_CHECKING:
        _data_class: ClassVar[type[AtData]]

        def __init__(self, **kwargs: Unpack[AtDataType]): ...


@dataclass(slots=True, frozen=True, kw_only=True, init=False)
class ForwardMessageSegment(
    MessageSegment[Literal["forward"], ForwardData, ForwardDataType]
):
    data: ForwardData
    type: Literal["forward"] = "forward"

    if TYPE_CHECKING:
        _data_class: ClassVar[type[ForwardData]]

        def __init__(self, **kwargs: Unpack[ForwardDataType]): ...
