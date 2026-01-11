from abc import ABC
from dataclasses import dataclass
from enum import IntEnum
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    ClassVar,
    Literal,
    NotRequired,
    TypedDict,
    Unpack,
    get_type_hints,
)

from .utils import IgnoreExtraArgsMixin


class ImageSubType(IntEnum):
    """图片子类型"""

    NORMAL = 0  # 普通图片
    MEME = 1  # 表情包/斗图


# --- Data Objects (对应你定义的 *Data) ---


class SegmentDataTypeBase(TypedDict):
    pass


@dataclass(slots=True, frozen=True, kw_only=True)
class TextData(IgnoreExtraArgsMixin):
    text: str


class TextDataType(SegmentDataTypeBase):
    text: str


@dataclass(slots=True, frozen=True, kw_only=True)
class ReplyData(IgnoreExtraArgsMixin):
    id: int


class ReplyDataType(SegmentDataTypeBase):
    id: int


@dataclass(slots=True, frozen=True, kw_only=True)
class ImageData(IgnoreExtraArgsMixin):
    file: Annotated[
        str,
        '如果是接收，则通常是MD5.jpg。如果是发送，"file://D:/a.jpg"、"http://xxx.png"、"base64://xxxxxxxx"',
    ]
    sub_type: ImageSubType = ImageSubType.NORMAL
    url: Annotated[str | None, "如果是发送，可以省略此项"] = None
    file_size: Annotated[int | None, "如果是发送，可以省略此项"] = None

    @classmethod
    def from_dict(cls, data: dict) -> ImageData:
        return super().from_dict(
            data | {"sub_type": ImageSubType(data.get("sub_type", 0))}
        )


class ImageDataType(SegmentDataTypeBase):
    file: str
    sub_type: NotRequired[int]
    url: NotRequired[str | None]
    file_size: NotRequired[int | None]


@dataclass(slots=True, frozen=True, kw_only=True)
class VideoData(IgnoreExtraArgsMixin):
    file: Annotated[
        str,
        '如果是接收，则通常是MD5.mp4。如果是发送，"file://D:/a.mp4"、"http://xxx.mp4"',
    ]
    url: Annotated[str | None, "如果是发送，可以省略此项"] = None
    file_size: Annotated[int | None, "如果是发送，可以省略此项"] = None


class VideoDataType(SegmentDataTypeBase):
    file: str
    url: NotRequired[str | None]
    file_size: NotRequired[int | None]


@dataclass(slots=True, frozen=True, kw_only=True)
class FileData(IgnoreExtraArgsMixin):
    file: str
    file_id: str
    url: Annotated[str | None, "私聊没有群聊有"] = None


class FileDataType(SegmentDataTypeBase):
    file: str
    file_id: str
    url: NotRequired[str | None]


@dataclass(slots=True, frozen=True, kw_only=True)
class AtData(IgnoreExtraArgsMixin):
    qq: int | Literal["all"]


class AtDataType(SegmentDataTypeBase):
    qq: int | Literal["all"]


@dataclass(slots=True, frozen=True, kw_only=True)
class ForwardData(IgnoreExtraArgsMixin):
    id: int


class ForwardDataType(SegmentDataTypeBase):
    id: int


# --- Segment Objects (对应你定义的 *MessageSegment) ---

type SegmentDataType = (
    TextData | ReplyData | AtData | ForwardData | ImageData | VideoData | FileData
)


@dataclass(slots=True, frozen=True, kw_only=True)
class MessageSegment[T_Data: SegmentDataTypeBase](ABC):
    type: Literal["text", "reply", "at", "forward", "image", "video", "file"]
    data: SegmentDataType

    _data_class: ClassVar[type[SegmentDataType]]
    _registry: ClassVar[dict[str, type[MessageSegment]]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
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

    def __init__(self, **kwargs: Unpack[T_Data]):  # type: ignore
        object.__setattr__(self, "type", self.__class__.type)

        data_cls = self.__class__._data_class
        if not data_cls:
            raise ValueError(
                f"Class {self.__class__.__name__} missing type hint for 'data'"
            )

        data_inst = data_cls.from_dict(kwargs)
        object.__setattr__(self, "data", data_inst)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> MessageSegment:
        seg_type = raw.get("type")
        if not isinstance(seg_type, str):
            raise ValueError("Invalid or missing 'type' field in message segment")
        data_payload = raw.get("data", {})
        if not isinstance(data_payload, dict):
            raise ValueError("Invalid message segment data")

        target_cls = cls._registry.get(seg_type)
        if not target_cls:
            raise ValueError(f"Unknown segment type: {seg_type}")

        return target_cls(**data_payload)


@dataclass(slots=True, frozen=True, kw_only=True, init=False)
class TextMessageSegment(MessageSegment[TextDataType]):
    data: TextData
    type: Literal["text"] = "text"

    if TYPE_CHECKING:

        def __init__(self, **kwargs: Unpack[TextDataType]): ...


@dataclass(slots=True, frozen=True, kw_only=True, init=False)
class ReplyMessageSegment(MessageSegment[ReplyDataType]):
    data: ReplyData
    type: Literal["reply"] = "reply"

    if TYPE_CHECKING:

        def __init__(self, **kwargs: Unpack[ReplyDataType]): ...


@dataclass(slots=True, frozen=True, kw_only=True, init=False)
class ImageMessageSegment(MessageSegment[ImageDataType]):
    data: ImageData
    type: Literal["image"] = "image"

    if TYPE_CHECKING:

        def __init__(self, **kwargs: Unpack[ImageDataType]): ...


@dataclass(slots=True, frozen=True, kw_only=True, init=False)
class VideoMessageSegment(MessageSegment[VideoDataType]):
    data: VideoData
    type: Literal["video"] = "video"

    if TYPE_CHECKING:

        def __init__(self, **kwargs: Unpack[VideoDataType]): ...


@dataclass(slots=True, frozen=True, kw_only=True, init=False)
class FileMessageSegment(MessageSegment[FileDataType]):
    data: FileData
    type: Literal["file"] = "file"

    if TYPE_CHECKING:

        def __init__(self, **kwargs: Unpack[FileDataType]): ...


@dataclass(slots=True, frozen=True, kw_only=True, init=False)
class AtMessageSegment(MessageSegment[AtDataType]):
    data: AtData
    type: Literal["at"] = "at"

    if TYPE_CHECKING:

        def __init__(self, **kwargs: Unpack[AtDataType]): ...


@dataclass(slots=True, frozen=True, kw_only=True, init=False)
class ForwardMessageSegment(MessageSegment[ForwardDataType]):
    data: ForwardData
    type: Literal["forward"] = "forward"

    if TYPE_CHECKING:

        def __init__(self, **kwargs: Unpack[ForwardDataType]): ...
