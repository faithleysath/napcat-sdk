from __future__ import annotations

from typing import Any

from napcat.types.events import NapCatEvent
from napcat.types.events.base import UnknownEvent
from napcat.types.events.message import GroupMessageEvent, PrivateMessageEvent
from napcat.types.events.meta import HeartbeatEvent, LifecycleMetaEvent
from napcat.types.events.notice.base import UnknownNoticeEvent
from napcat.types.events.notice.GroupUploadNoticeEvent import (
    GroupUploadFile,
    GroupUploadNoticeEvent,
)
from napcat.types.events.notice.MsgEmojiLikeEvent import (
    GroupMsgEmojiLikeEvent,
    MsgEmojiLike,
)
from napcat.types.events.notice.PokeEvent import FriendPokeEvent, GroupPokeEvent
from napcat.types.events.request import FriendRequestEvent, GroupRequestEvent
from napcat.types.messages import Text


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


def test_invalid_post_type_fallback_to_unknown_event() -> None:
    payload = {
        "time": 1,
        "self_id": 10000,
        "post_type": 123,
    }

    event = NapCatEvent.from_dict(payload)

    assert isinstance(event, UnknownEvent)
    assert event.post_type == "123"


def test_unregistered_post_type_fallback_to_unknown_event() -> None:
    payload = {
        "time": 1,
        "self_id": 10000,
        "post_type": "nonexistent_type",
    }

    event = NapCatEvent.from_dict(payload)

    assert isinstance(event, UnknownEvent)
    assert event.post_type == "nonexistent_type"


def test_notice_unknown_type_fallback_to_unknown_notice_event() -> None:
    payload = {
        "time": 1,
        "self_id": 10000,
        "post_type": "notice",
        "notice_type": "totally_unknown_notice",
    }

    event = NapCatEvent.from_dict(payload)

    assert isinstance(event, UnknownNoticeEvent)
    assert event.notice_type == "totally_unknown_notice"


def test_message_private_route() -> None:
    payload: dict[str, Any] = {
        "time": 1,
        "self_id": 10000,
        "post_type": "message",
        "message_type": "private",
        "message_id": 1,
        "message_seq": 2,
        "real_id": 3,
        "user_id": 123,
        "sender": {"user_id": 123, "nickname": "alice"},
        "raw_message": "hello",
        "message": [],
    }

    event = NapCatEvent.from_dict(payload)

    assert isinstance(event, PrivateMessageEvent)
    assert event.message_type == "private"
    assert event.sender.nickname == "alice"


def test_message_group_route() -> None:
    payload: dict[str, Any] = {
        "time": 1,
        "self_id": 10000,
        "post_type": "message",
        "message_type": "group",
        "group_id": 999,
        "message_id": 1,
        "message_seq": 2,
        "real_id": 3,
        "user_id": 123,
        "sender": {"user_id": 123, "nickname": "bob"},
        "raw_message": "hello group",
        "message": [],
    }

    event = NapCatEvent.from_dict(payload)

    assert isinstance(event, GroupMessageEvent)
    assert event.group_id == 999
    assert event.sender.nickname == "bob"


def test_message_segment_text_deserialize() -> None:
    payload: dict[str, Any] = {
        "time": 1,
        "self_id": 10000,
        "post_type": "message",
        "message_type": "private",
        "message_id": 10,
        "message_seq": 20,
        "real_id": 30,
        "user_id": 123,
        "sender": {"user_id": 123, "nickname": "segment-user"},
        "raw_message": "hello text segment",
        "message": [
            {"type": "text", "data": {"text": "hello text segment"}},
        ],
    }

    event = NapCatEvent.from_dict(payload)

    assert isinstance(event, PrivateMessageEvent)
    assert len(event.message) == 1
    assert isinstance(event.message[0], Text)
    assert event.message[0].text == "hello text segment"


def test_message_unknown_message_type_fallback_to_unknown_event() -> None:
    payload: dict[str, Any] = {
        "time": 1,
        "self_id": 10000,
        "post_type": "message",
        "message_type": "weird",
        "message_id": 1,
        "message_seq": 2,
        "real_id": 3,
        "user_id": 123,
        "sender": {"user_id": 123, "nickname": "eve"},
        "raw_message": "x",
        "message": [],
    }

    event = NapCatEvent.from_dict(payload)

    assert isinstance(event, UnknownEvent)
    assert event.post_type == "message"


def test_message_invalid_sender_fallback_to_unknown_event() -> None:
    payload: dict[str, Any] = {
        "time": 1,
        "self_id": 10000,
        "post_type": "message",
        "message_type": "private",
        "message_id": 1,
        "message_seq": 2,
        "real_id": 3,
        "user_id": 123,
        "sender": {"nickname": "missing_user_id"},
        "raw_message": "hello",
        "message": [],
    }

    event = NapCatEvent.from_dict(payload)

    assert isinstance(event, UnknownEvent)
    assert event.post_type == "message"


def test_meta_lifecycle_route() -> None:
    payload = {
        "time": 1,
        "self_id": 10000,
        "post_type": "meta_event",
        "meta_event_type": "lifecycle",
        "sub_type": "connect",
    }

    event = NapCatEvent.from_dict(payload)

    assert isinstance(event, LifecycleMetaEvent)
    assert event.sub_type == "connect"


def test_meta_heartbeat_route() -> None:
    payload = {
        "time": 1,
        "self_id": 10000,
        "post_type": "meta_event",
        "meta_event_type": "heartbeat",
        "interval": 5000,
        "status": {"online": True, "good": True},
    }

    event = NapCatEvent.from_dict(payload)

    assert isinstance(event, HeartbeatEvent)
    assert event.status.good is True
    assert event.interval == 5000


def test_meta_heartbeat_invalid_status_fallback_to_unknown_event() -> None:
    payload = {
        "time": 1,
        "self_id": 10000,
        "post_type": "meta_event",
        "meta_event_type": "heartbeat",
        "interval": 5000,
        "status": "bad_status",
    }

    event = NapCatEvent.from_dict(payload)

    assert isinstance(event, UnknownEvent)
    assert event.post_type == "meta_event"


def test_request_friend_route() -> None:
    payload = {
        "time": 1,
        "self_id": 10000,
        "post_type": "request",
        "request_type": "friend",
        "user_id": 321,
        "comment": "hi",
        "flag": "f1",
    }

    event = NapCatEvent.from_dict(payload)

    assert isinstance(event, FriendRequestEvent)
    assert event.user_id == 321


def test_request_group_route() -> None:
    payload = {
        "time": 1,
        "self_id": 10000,
        "post_type": "request",
        "request_type": "group",
        "group_id": 888,
        "user_id": 321,
        "sub_type": "add",
        "comment": "let me in",
        "flag": "g1",
    }

    event = NapCatEvent.from_dict(payload)

    assert isinstance(event, GroupRequestEvent)
    assert event.group_id == 888


def test_request_unknown_type_fallback_to_unknown_event() -> None:
    payload = {
        "time": 1,
        "self_id": 10000,
        "post_type": "request",
        "request_type": "unknown_request",
    }

    event = NapCatEvent.from_dict(payload)

    assert isinstance(event, UnknownEvent)
    assert event.post_type == "request"
