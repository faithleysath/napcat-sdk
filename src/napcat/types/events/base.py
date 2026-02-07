# src/napcat/types/events/base.py

from __future__ import annotations

import logging
from abc import ABC
from dataclasses import dataclass, field, is_dataclass
from typing import TYPE_CHECKING, Any, ClassVar, cast

from ..utils import FromDictMixin

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

        if not effective_register:
            return

        if ABC in cls.__bases__:
            return

        # 1. 仅从 post_type 读取注册键
        pt = cls.__dict__.get("post_type")

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
                raise ValueError(f"Duplicate segment type registered: '{t}' by {cls.__name__}")

            # 写入/更新注册表
            NapCatEvent._registry[t] = cls

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NapCatEvent:
        post_type = data.get("post_type")

        if not isinstance(post_type, str):
            logger.error(
                "Fallback to UnknownEvent: invalid post_type, payload_keys=%s",
                sorted(data.keys()),
            )
            return UnknownEvent(
                time=int(data.get("time", 0)),
                self_id=int(data.get("self_id", 0)),
                post_type=str(data.get("post_type", "unknown")),
                raw_data=data,
            )

        target_cls = NapCatEvent._registry.get(post_type)
        if target_cls is None:
            logger.error(
                "Fallback to UnknownEvent: unregistered post_type=%r, payload_keys=%s",
                post_type,
                sorted(data.keys()),
            )
            return UnknownEvent(
                time=int(data.get("time", 0)),
                self_id=int(data.get("self_id", 0)),
                post_type=str(data.get("post_type", "unknown")),
                raw_data=data,
            )

        try:
            return target_cls.from_dict(data)
        except Exception:
            logger.error(
                "Fallback to UnknownEvent: %s.from_dict failed for post_type=%r",
                target_cls.__name__,
                post_type,
                exc_info=True,
            )

        # --- 兜底逻辑 ---
        return UnknownEvent(
            time=int(data.get("time", 0)),
            self_id=int(data.get("self_id", 0)),
            post_type=str(data.get("post_type", "unknown")),
            raw_data=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class UnknownEvent(NapCatEvent, register=False):
    """万能兜底事件"""
    raw_data: dict[str, Any]
    post_type: str = "unknown"
