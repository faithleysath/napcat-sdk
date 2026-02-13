# src/napcat/types/events/base.py

from __future__ import annotations

import logging
from abc import ABC
from dataclasses import dataclass, field, is_dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Self, cast

from ..utils import FromDictMixin, get_dataclass_field_default

if TYPE_CHECKING:
    from ...client import NapCatClient
else:
    NapCatClient = Any


logger = logging.getLogger("napcat.events")


@dataclass(slots=True, frozen=True, kw_only=True)
class NapCatEvent(FromDictMixin, ABC):
    """
    对应 NapCatQQ/packages/napcat-onebot/event/OneBotEvent.ts
    """

    time: int
    self_id: int
    post_type: str | tuple[str, ...]
    _client: NapCatClient | None = field(
        init=False, repr=False, hash=False, compare=False, default=None
    )
    _raw: dict[str, Any] = field(
        init=False,
        repr=False,
        hash=False,
        compare=False,
        default_factory=lambda: dict[str, Any](),
    )

    @property
    def client(self) -> NapCatClient | None:
        return self._client

    def bind(self, client: NapCatClient) -> Self:
        """绑定 client 到此 event，使其能调用 API（如 reply/approve 等）。"""
        object.__setattr__(self, "_client", client)
        return self

    def to_dict(self) -> dict[str, Any]:
        """序列化为 dict。若绑定的 client 开启了 rpc_mode，自动注入 _rpc 连接信息。"""
        data = dict(self._raw)
        if self._client is not None and getattr(self._client, "rpc_mode", False):
            data["_rpc"] = {
                "host": self._client.rpc_url_host,
                "port": self._client.rpc_port,
                "token": self._client.rpc_token,
            }
        return data

    # --- 自动注册机制 ---
    _registry: ClassVar[dict[str, type[NapCatEvent]]] = {}
    __event_register__: ClassVar[bool]

    def __init_subclass__(cls: type[NapCatEvent], register: bool = True, **kwargs: Any):
        # super().__init_subclass__(**kwargs)

        # Persist the explicit `register=` decision across potential class
        # recreation by @dataclass(slots=True, ...).
        saved_register = cls.__dict__.get("__event_register__")
        if saved_register is None:
            cls.__event_register__ = register
            effective_register = register
        else:
            effective_register = bool(saved_register)

        # NOTE:
        # dataclass(slots=True, ...) may recreate the class object, causing
        # __init_subclass__ to be called once before @dataclass is applied.
        # Skip that early phase and let the dataclass-processed class handle
        # registration.
        if not is_dataclass(cls):
            return

        # If post_type exists, it means it's an early class not the final class
        if cls.__dict__.get("post_type") is not None:
            return

        if not effective_register:
            return

        if ABC in cls.__bases__:
            return

        # 1. 仅从 post_type 读取注册键
        pt = get_dataclass_field_default(cls, "post_type", declared_only=True)

        if not pt or not isinstance(pt, (str, tuple, list)):
            return

        # 统一转为列表处理
        pt_list: list[str]
        if isinstance(pt, str):
            pt_list = [pt]
        else:
            # 显式告知 Pylance 这里是字符串列表/元组
            pt_list = list(cast(list[str] | tuple[str, ...], pt))

        # 3. 注册逻辑 (带 dataclass slots 兼容)
        for t in pt_list:
            if t in NapCatEvent._registry:
                raise ValueError(
                    f"Duplicate segment type registered: '{t}' by {cls.__name__}"
                )

            # 写入/更新注册表
            NapCatEvent._registry[t] = cls

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        client: NapCatClient | None = None,
    ) -> NapCatEvent:
        # 提取并移除 _rpc 元数据（不属于原始 event）
        clean_data = {k: v for k, v in data.items() if k != "_rpc"}

        post_type = clean_data.get("post_type")

        if not isinstance(post_type, str):
            logger.error(
                "Fallback to UnknownEvent: invalid post_type, payload_keys=%s",
                sorted(clean_data.keys()),
            )
            event = UnknownEvent(
                time=int(clean_data.get("time", 0)),
                self_id=int(clean_data.get("self_id", 0)),
                post_type=str(clean_data.get("post_type", "unknown")),
                raw_data=clean_data,
            )
            object.__setattr__(event, "_raw", clean_data)
            if client is not None:
                object.__setattr__(event, "_client", client)
            return event

        target_cls = NapCatEvent._registry.get(post_type)
        if target_cls is None:
            logger.error(
                "Fallback to UnknownEvent: unregistered post_type=%r, payload_keys=%s",
                post_type,
                sorted(clean_data.keys()),
            )
            event = UnknownEvent(
                time=int(clean_data.get("time", 0)),
                self_id=int(clean_data.get("self_id", 0)),
                post_type=str(clean_data.get("post_type", "unknown")),
                raw_data=clean_data,
            )
            object.__setattr__(event, "_raw", clean_data)
            if client is not None:
                object.__setattr__(event, "_client", client)
            return event

        try:
            event = target_cls.from_dict(clean_data)
            object.__setattr__(event, "_raw", clean_data)
            if client is not None:
                object.__setattr__(event, "_client", client)
            return event
        except Exception:
            logger.error(
                "Fallback to UnknownEvent: %s.from_dict failed for post_type=%r",
                target_cls.__name__,
                post_type,
                exc_info=True,
            )

        # --- 兜底逻辑 ---
        event = UnknownEvent(
            time=int(clean_data.get("time", 0)),
            self_id=int(clean_data.get("self_id", 0)),
            post_type=str(clean_data.get("post_type", "unknown")),
            raw_data=clean_data,
        )
        object.__setattr__(event, "_raw", clean_data)
        if client is not None:
            object.__setattr__(event, "_client", client)
        return event


@dataclass(slots=True, frozen=True, kw_only=True)
class UnknownEvent(NapCatEvent, register=False):
    """万能兜底事件"""

    raw_data: dict[str, Any]
    post_type: str = "unknown"
