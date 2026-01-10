from typing import Any, ClassVar, Protocol


class DataclassProtocol(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Any]]


class IgnoreExtraArgsMixin:
    __slots__ = ()

    @classmethod
    def from_dict[T: DataclassProtocol](cls: type[T], data: dict) -> T:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class IgnoreExtraArgsInternalMixin:
    __slots__ = ()

    @classmethod
    def _from_dict[T: DataclassProtocol](cls: type[T], data: dict) -> T:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
