from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

from napcat.types.events import NapCatEvent
from napcat.types.events.base import UnknownEvent
from napcat.types.events.message import GroupMessageEvent, PrivateMessageEvent
from napcat.types.events.request import FriendRequestEvent

# --- 辅助数据 ---


def _private_msg_payload() -> dict[str, Any]:
    return {
        "time": 1,
        "self_id": 10000,
        "post_type": "message",
        "message_type": "private",
        "message_id": 42,
        "message_seq": 1,
        "real_id": 1,
        "user_id": 123,
        "sender": {"user_id": 123, "nickname": "alice"},
        "raw_message": "hello",
        "message": [{"type": "text", "data": {"text": "hello"}}],
    }


def _group_msg_payload() -> dict[str, Any]:
    return {
        "time": 2,
        "self_id": 10000,
        "post_type": "message",
        "message_type": "group",
        "group_id": 999,
        "message_id": 43,
        "message_seq": 2,
        "real_id": 2,
        "user_id": 456,
        "sender": {"user_id": 456, "nickname": "bob"},
        "raw_message": "hi group",
        "message": [],
    }


def _friend_request_payload() -> dict[str, Any]:
    return {
        "time": 3,
        "self_id": 10000,
        "post_type": "request",
        "request_type": "friend",
        "user_id": 789,
        "comment": "add me",
        "flag": "f1",
    }


def _make_mock_client() -> Any:
    """创建一个 mock client，模拟 NapCatClient 的关键属性。"""
    return AsyncMock()


# === to_dict 往返一致性 ===


def test_to_dict_roundtrip_private_message() -> None:
    payload = _private_msg_payload()
    event = NapCatEvent.from_dict(payload)
    result = event.to_dict()

    assert isinstance(event, PrivateMessageEvent)
    # 原始 payload 字段应全部保留
    for key in payload:
        assert key in result, f"Missing key: {key}"
        assert result[key] == payload[key], f"Mismatch on key: {key}"


def test_to_dict_roundtrip_group_message() -> None:
    payload = _group_msg_payload()
    event = NapCatEvent.from_dict(payload)
    result = event.to_dict()

    assert isinstance(event, GroupMessageEvent)
    for key in payload:
        assert key in result
        assert result[key] == payload[key]


def test_to_dict_roundtrip_friend_request() -> None:
    payload = _friend_request_payload()
    event = NapCatEvent.from_dict(payload)
    result = event.to_dict()

    assert isinstance(event, FriendRequestEvent)
    for key in payload:
        assert key in result
        assert result[key] == payload[key]


def test_to_dict_roundtrip_unknown_event() -> None:
    payload = {
        "time": 1,
        "self_id": 10000,
        "post_type": "nonexistent",
    }
    event = NapCatEvent.from_dict(payload)
    result = event.to_dict()

    assert isinstance(event, UnknownEvent)
    for key in payload:
        assert key in result


# === bind 方法 ===


def test_bind_returns_self() -> None:
    payload = _private_msg_payload()
    event = NapCatEvent.from_dict(payload)
    client = _make_mock_client()

    result = event.bind(client)
    assert result is event


def test_bind_sets_client() -> None:
    payload = _private_msg_payload()
    event = NapCatEvent.from_dict(payload)
    assert event.client is None

    client = _make_mock_client()
    event.bind(client)
    assert event.client is client


# === from_dict 带 client 参数 ===


def test_from_dict_with_client() -> None:
    payload = _private_msg_payload()
    client = _make_mock_client()

    event = NapCatEvent.from_dict(payload, client=client)
    assert isinstance(event, PrivateMessageEvent)
    assert event.client is client


def test_from_dict_with_client_unknown_event() -> None:
    payload = {
        "time": 1,
        "self_id": 10000,
        "post_type": "nonexistent",
    }
    client = _make_mock_client()

    event = NapCatEvent.from_dict(payload, client=client)
    assert isinstance(event, UnknownEvent)
    assert event.client is client
