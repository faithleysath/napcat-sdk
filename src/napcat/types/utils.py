from dataclasses import MISSING, fields
from typing import Any, ClassVar, Protocol


class DataclassProtocol(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Any]]


class IgnoreExtraArgsMixin:
    __slots__ = ()

    @classmethod
    def from_dict[T: DataclassProtocol](cls: type[T], data: dict) -> T:
        cls_fields = {f.name: f for f in fields(cls)}
        valid_args = {k: v for k, v in data.items() if k in cls_fields}

        missing_fields = []
        for name, field in cls_fields.items():
            if name not in valid_args:
                if field.default is MISSING and field.default_factory is MISSING:
                    missing_fields.append(name)

        if missing_fields:
            raise ValueError(
                f"Failed to parse {cls.__name__}: Missing required fields {missing_fields}. "
                f"Input data: {data}"
            )

        return cls(**valid_args)


class IgnoreExtraArgsInternalMixin:
    __slots__ = ()

    @classmethod
    def from_dict[T: DataclassProtocol](cls: type[T], data: dict) -> T:
        cls_fields = {f.name: f for f in fields(cls)}
        valid_args = {k: v for k, v in data.items() if k in cls_fields}

        missing_fields = []
        for name, field in cls_fields.items():
            if name not in valid_args:
                if field.default is MISSING and field.default_factory is MISSING:
                    missing_fields.append(name)

        if missing_fields:
            raise ValueError(
                f"Failed to parse {cls.__name__}: Missing required fields {missing_fields}. "
                f"Input data: {data}"
            )

        return cls(**valid_args)
