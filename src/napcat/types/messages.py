from abc import ABC
from dataclasses import dataclass
from enum import IntEnum
from typing import Annotated, Any, Literal

from .utils import IgnoreExtraArgsMixin


class ImageSubType(IntEnum):
    """图片子类型"""

    NORMAL = 0  # 普通图片
    MEME = 1  # 表情包/斗图


# --- Data Objects (对应你定义的 *Data) ---


@dataclass(slots=True, frozen=True, kw_only=True)
class TextData(IgnoreExtraArgsMixin):
    text: str


@dataclass(slots=True, frozen=True, kw_only=True)
class ReplyData(IgnoreExtraArgsMixin):
    id: int


@dataclass(slots=True, frozen=True, kw_only=True)
class ImageData(IgnoreExtraArgsMixin):
    file: Annotated[
        str,
        '如果是接收，则通常是MD5.jpg。如果是发送，"file://D:/a.jpg"、"http://xxx.png"、"base64://xxxxxxxx"',
    ]
    sub_type: int | ImageSubType
    url: str | None = None
    file_size: Annotated[int | None, "如果是发送，可以省略此项"] = None


@dataclass(slots=True, frozen=True, kw_only=True)
class VideoData(IgnoreExtraArgsMixin):
    file: Annotated[
        str,
        '如果是接收，则通常是MD5.mp4。如果是发送，"file://D:/a.mp4"、"http://xxx.mp4"',
    ]
    url: str | None = None
    file_size: Annotated[int | None, "如果是发送，可以省略此项"] = None


@dataclass(slots=True, frozen=True, kw_only=True)
class FileData(IgnoreExtraArgsMixin):
    file: str
    file_id: str
    url: Annotated[str | None, "私聊没有群聊有"] = None


@dataclass(slots=True, frozen=True, kw_only=True)
class AtData(IgnoreExtraArgsMixin):
    qq: int | Literal["all"]


@dataclass(slots=True, frozen=True, kw_only=True)
class ForwardData(IgnoreExtraArgsMixin):
    id: int


# --- Segment Objects (对应你定义的 *MessageSegment) ---

type SegmentDataType = (
    TextData | ReplyData | AtData | ForwardData | ImageData | VideoData | FileData
)


@dataclass(slots=True, frozen=True, kw_only=True)
class MessageSegment(ABC):
    type: Literal["text", "reply", "at", "forward", "image", "video", "file"]
    data: SegmentDataType

    @staticmethod
    def from_dict(raw: dict[str, Any]) -> MessageSegment:
        seg_type = raw.get("type")
        data = raw.get("data", {})
        if not isinstance(data, dict):
            raise ValueError("Invalid message segment data")

        match seg_type:
            case "text":
                return TextMessageSegment(data=TextData.from_dict(data))
            case "reply":
                return ReplyMessageSegment(data=ReplyData.from_dict(data))
            case "at":
                return AtMessageSegment(data=AtData.from_dict(data))
            case "forward":
                return ForwardMessageSegment(data=ForwardData.from_dict(data))
            case "video":
                return VideoMessageSegment(data=VideoData.from_dict(data))
            case "file":
                return FileMessageSegment(data=FileData.from_dict(data))
            case "image":
                return ImageMessageSegment(
                    data=ImageData.from_dict(
                        data | {"sub_type": ImageSubType(data["sub_type"])}
                    )
                )
            case _:
                raise ValueError(f"Unknown segment type: {seg_type}")


@dataclass(slots=True, frozen=True, kw_only=True)
class TextMessageSegment(MessageSegment):
    data: TextData
    type: Literal["text"] = "text"


@dataclass(slots=True, frozen=True, kw_only=True)
class ReplyMessageSegment(MessageSegment):
    data: ReplyData
    type: Literal["reply"] = "reply"


@dataclass(slots=True, frozen=True, kw_only=True)
class ImageMessageSegment(MessageSegment):
    data: ImageData
    type: Literal["image"] = "image"


@dataclass(slots=True, frozen=True, kw_only=True)
class VideoMessageSegment(MessageSegment):
    data: VideoData
    type: Literal["video"] = "video"


@dataclass(slots=True, frozen=True, kw_only=True)
class FileMessageSegment(MessageSegment):
    data: FileData
    type: Literal["file"] = "file"


@dataclass(slots=True, frozen=True, kw_only=True)
class AtMessageSegment(MessageSegment):
    data: AtData
    type: Literal["at"] = "at"


@dataclass(slots=True, frozen=True, kw_only=True)
class ForwardMessageSegment(MessageSegment):
    data: ForwardData
    type: Literal["forward"] = "forward"
