from __future__ import annotations

from napcat.types.events import NapCatEvent
from napcat.types.events.notice.GroupUploadNoticeEvent import (
    GroupUploadFile,
    GroupUploadNoticeEvent,
)
from napcat.types.events.notice.MsgEmojiLikeEvent import (
    GroupMsgEmojiLikeEvent,
    MsgEmojiLike,
)
from napcat.types.events.notice.PokeEvent import FriendPokeEvent, GroupPokeEvent


def test_notice_group_upload_nested_file_dataclass() -> None:
    payload = {
        "time": 1,
        "self_id": 10000,
        "post_type": "notice",
        "notice_type": "group_upload",
        "group_id": 123,
        "user_id": 456,
        "file": {"id": "f1", "name": "a.txt", "size": 1, "busid": 102},
    }

    event = NapCatEvent.from_dict(payload)
    print(event)

    assert isinstance(event, GroupUploadNoticeEvent)
    assert isinstance(event.file, GroupUploadFile)
    assert event.file.name == "a.txt"


def test_notice_group_msg_emoji_like_nested_list_dataclass() -> None:
    payload = {
        "time": 1,
        "self_id": 10000,
        "post_type": "notice",
        "notice_type": "group_msg_emoji_like",
        "group_id": 123,
        "user_id": 456,
        "message_id": 9,
        "likes": [{"emoji_id": "128077", "count": 3}],
        "is_add": True,
    }

    event = NapCatEvent.from_dict(payload)
    print(event)

    assert isinstance(event, GroupMsgEmojiLikeEvent)
    assert len(event.likes) == 1
    assert isinstance(event.likes[0], MsgEmojiLike)
    assert event.likes[0].count == 3


def test_notify_poke_friend_route() -> None:
    payload = {
        "time": 1,
        "self_id": 10000,
        "post_type": "notice",
        "notice_type": "notify",
        "sub_type": "poke",
        "user_id": 111,
        "target_id": 10000,
        "sender_id": 111,
        "raw_info": {"foo": "bar"},
    }

    event = NapCatEvent.from_dict(payload)
    assert isinstance(event, FriendPokeEvent)


def test_notify_poke_group_route() -> None:
    payload = {
        "time": 1,
        "self_id": 10000,
        "post_type": "notice",
        "notice_type": "notify",
        "sub_type": "poke",
        "group_id": 222,
        "user_id": 111,
        "target_id": 10000,
        "raw_info": {"foo": "bar"},
    }

    event = NapCatEvent.from_dict(payload)
    assert isinstance(event, GroupPokeEvent)
