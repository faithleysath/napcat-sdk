# src/napcat/types/events/request.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Literal

from .base import NapCatEvent


@dataclass(slots=True, frozen=True, kw_only=True)
class RequestEvent(NapCatEvent):
    # 对应 NapCatQQ/packages/napcat-onebot/event/request/OB11BaseRequestEvent.ts
    post_type: Literal["request"] = "request"
    request_type: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RequestEvent:
        req_type = data.get("request_type")
        if req_type == "friend":
            return FriendRequestEvent._from_dict(data)
        elif req_type == "group":
            return GroupRequestEvent._from_dict(data)
        
        # 未知类型的 Request，抛出异常或返回基类/Unknown
        raise ValueError(f"Unknown request event type: {req_type}")


@dataclass(slots=True, frozen=True, kw_only=True)
class FriendRequestEvent(RequestEvent):
    # 对应 NapCatQQ/packages/napcat-onebot/event/request/OB11FriendRequest.ts
    user_id: int
    comment: str
    flag: str
    request_type: Literal["friend"] = "friend"

    async def approve(self, remark: str = "") -> None:
        """同意好友请求"""
        if self._client is None:
            raise RuntimeError("Event not bound to a client")
        await self._client.api.set_friend_add_request(flag=self.flag, approve=True, remark=remark)

    async def reject(self) -> None:
        """拒绝好友请求"""
        if self._client is None:
            raise RuntimeError("Event not bound to a client")
        await self._client.api.set_friend_add_request(flag=self.flag, approve=False)


@dataclass(slots=True, frozen=True, kw_only=True)
class GroupRequestEvent(RequestEvent):
    # 对应 NapCatQQ/packages/napcat-onebot/event/request/OB11GroupRequest.ts
    group_id: int
    user_id: int
    sub_type: Literal["add", "invite"] | str # 对应 TS 中的 generic string，但在 OneBot 中通常为 add(加群) 或 invite(邀请)
    comment: str
    flag: str
    request_type: Literal["group"] = "group"

    async def approve(self) -> None:
        """同意入群/邀请请求"""
        if self._client is None:
            raise RuntimeError("Event not bound to a client")
        await self._client.api.set_group_add_request(
            flag=self.flag, 
            approve=True
        )

    async def reject(self, reason: str = "") -> None:
        """拒绝入群/邀请请求"""
        if self._client is None:
            raise RuntimeError("Event not bound to a client")
        await self._client.api.set_group_add_request(
            flag=self.flag, 
            approve=False,
            reason=reason
        )
