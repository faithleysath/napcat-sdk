from dataclasses import dataclass

from .utils import IgnoreExtraArgsMixin, TypeValidatorMixin


@dataclass(slots=True, frozen=True, kw_only=True)
class ResponseDataBase(TypeValidatorMixin, IgnoreExtraArgsMixin):
    pass


@dataclass(slots=True, frozen=True, kw_only=True)
class LoginInfoData(ResponseDataBase):
    user_id: int
    nickname: str


@dataclass(slots=True, frozen=True, kw_only=True)
class MessageIdData(ResponseDataBase):
    message_id: int
