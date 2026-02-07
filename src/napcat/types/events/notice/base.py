# src/napcat/types/events/notice/base.py
from __future__ import annotations

from dataclasses import dataclass, is_dataclass
import logging
from typing import Any, ClassVar, Literal, cast

from ..base import NapCatEvent


logger = logging.getLogger("napcat.events")


@dataclass(slots=True, frozen=True, kw_only=True)
class NoticeEvent(NapCatEvent):
    """
    所有通知事件的绝对基类。
    对应 TS: OB11BaseNoticeEvent
    """

    post_type: Literal["notice"] = "notice"
    notice_type: str

    # Python 3.12+: 使用原生 dict 和 type
    _post_type: ClassVar[str] = "notice"
    _notice_registry: ClassVar[dict[str, type[NoticeEvent]]] = {}
    _notify_registry: ClassVar[dict[str, type[NoticeEvent]]] = {}
    __notice_register__: ClassVar[bool]

    def __init_subclass__(cls, register: bool = True, **kwargs: Any):
        super().__init_subclass__(**kwargs)

        # Persist explicit register decision across dataclass(slots=True) class recreation.
        saved_register = cls.__dict__.get("__notice_register__")
        if saved_register is None:
            cls.__notice_register__ = register
            effective_register = register
        else:
            effective_register = bool(saved_register)

        # dataclass(slots=True, ...) may trigger an early __init_subclass__ call
        # before dataclass processing; skip early phase to avoid duplicate registration.
        if not is_dataclass(cls):
            return

        if not effective_register:
            return

        # 1. 获取 notice_type (仅限当前类定义，不查找父类)
        n_type = cls.__dict__.get("notice_type")

        # 如果当前类没有显式定义 notice_type，直接跳过注册
        # 这完美解决了 PokeEvent 子类重复注册的问题
        if not n_type or not isinstance(n_type, str):
            return

        # 定义一个内部 helper 来处理注册和冲突检查 (兼容 slots)
        def register_safely(
            registry: dict[str, type[NoticeEvent]],
            key: str,
            value_cls: type[NoticeEvent],
        ):
            if key in registry:
                raise ValueError(
                    f"Duplicate notice type registered: '{key}' by {value_cls.__name__}"
                )

            registry[key] = value_cls

        # 2. 注册逻辑
        if n_type == "notify":
            # 同样仅限当前类定义的 sub_type
            s_type = cls.__dict__.get("sub_type")
            if s_type and isinstance(s_type, str):
                register_safely(
                    NoticeEvent._notify_registry,
                    s_type,
                    cast(type[NoticeEvent], cls),
                )
        else:
            register_safely(
                NoticeEvent._notice_registry,
                n_type,
                cast(type[NoticeEvent], cls),
            )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NoticeEvent:
        n_type = data.get("notice_type")

        if n_type == "notify":
            sub_type = data.get("sub_type")
            if isinstance(sub_type, str):
                target = cls._notify_registry.get(sub_type)
                if target:
                    return target._from_dict(data)
                logger.error(
                    "Fallback to UnknownNoticeEvent: unregistered notify sub_type=%r, payload_keys=%s",
                    sub_type,
                    sorted(data.keys()),
                )
            else:
                logger.error(
                    "Fallback to UnknownNoticeEvent: invalid notify sub_type=%r, payload_keys=%s",
                    sub_type,
                    sorted(data.keys()),
                )
        elif isinstance(n_type, str):
            target = cls._notice_registry.get(n_type)
            if target:
                return target._from_dict(data)
            logger.error(
                "Fallback to UnknownNoticeEvent: unregistered notice_type=%r, payload_keys=%s",
                n_type,
                sorted(data.keys()),
            )
        else:
            logger.error(
                "Fallback to UnknownNoticeEvent: invalid notice_type=%r, payload_keys=%s",
                n_type,
                sorted(data.keys()),
            )

        # 3. 兜底
        return UnknownNoticeEvent(
            time=int(data.get("time", 0)),
            self_id=int(data.get("self_id", 0)),
            notice_type=str(n_type) if n_type else "unknown",
            raw_data=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class UnknownNoticeEvent(NoticeEvent, register=False):
    """兜底未知事件"""

    raw_data: dict[str, Any]
    notice_type: str = "unknown"
