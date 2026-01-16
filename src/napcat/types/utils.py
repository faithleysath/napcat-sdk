from dataclasses import MISSING, Field, fields
from enum import Enum
from functools import lru_cache
from types import UnionType
from typing import (
    Annotated,
    Any,
    ClassVar,
    Final,
    Literal,
    LiteralString,
    Protocol,
    get_args,
    get_origin,
    get_type_hints,
    runtime_checkable,
)


@runtime_checkable
class DataclassProtocol(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Any]]


@lru_cache(maxsize=None)
def _cache_cls_fields(cls: type[DataclassProtocol]) -> tuple[Field[Any], ...]:
    return fields(cls)


class IgnoreExtraArgsMixin:
    __slots__ = ()

    @classmethod
    def from_dict[T: DataclassProtocol](cls: type[T], data: dict[str, Any]) -> T:
        cls_fields = {f.name: f for f in _cache_cls_fields(cls) if f.init}
        valid_args = {k: v for k, v in data.items() if k in cls_fields}

        missing_fields: list[str] = []
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

    @classmethod
    def _from_dict[T: DataclassProtocol](cls: type[T], data: dict[str, Any]) -> T:
        return IgnoreExtraArgsMixin.from_dict.__func__(cls, data)


@lru_cache(maxsize=None)
def _cached_type_hints(cls: type) -> dict[str, Any]:
    return get_type_hints(cls, include_extras=True)


def _type_repr(t: Any) -> str:
    try:
        return t.__name__  # type: ignore[attr-defined]
    except Exception:
        return repr(t)


def _strip_wrappers(t: Any) -> Any:
    while True:
        origin = get_origin(t)
        if origin is Annotated:
            t = get_args(t)[0]
            continue
        if origin is Final:
            t = get_args(t)[0]
            continue
        if origin is ClassVar:
            t = get_args(t)[0]
            continue
        return t


def _literal_matches(value: Any, literal_vals: tuple[Any, ...]) -> bool:
    # 比较严格：不仅 value == lit，还要求 type(value) is type(lit)，避免 True == 1 这种情况
    for lit in literal_vals:
        if value == lit and type(value) is type(lit):
            return True
    return False


def _shallow_isinstance(value: Any, expected: Any) -> bool:
    expected = _strip_wrappers(expected)

    if expected is Any or expected is object:
        return True

    # LiteralString -> str
    if expected is LiteralString:
        return isinstance(value, str)

    origin = get_origin(expected)

    # Literal[...]
    if origin is Literal:
        return _literal_matches(value, get_args(expected))

    # Union / Optional / PEP604 |
    if origin is UnionType:
        return any(_shallow_isinstance(value, opt) for opt in get_args(expected))

    # type[T]
    if origin is type:
        if not isinstance(value, type):
            return False
        args = get_args(expected)
        if not args or args == (Any,):
            return True
        base = _strip_wrappers(args[0])
        return isinstance(base, type) and issubclass(value, base)

    # 枚举：必须是枚举实例（严格要求）
    if isinstance(expected, type) and issubclass(expected, Enum):
        return isinstance(value, expected)

    # 容器/泛型：只检查最表层容器类型，不检查内部
    if origin is not None:
        if isinstance(origin, type):
            return isinstance(value, origin)
        # 其他 origin（比如特殊 typing 构造）无法可靠 isinstance，保守放行
        return True

    # 普通类
    if isinstance(expected, type):
        return isinstance(value, expected)

    # 其他 typing 构造（TypeVar/Protocol 等）：这里无法可靠判断，保守放行
    return True


class TypeValidatorMixin:
    """
    dataclass mixin: 在 __post_init__ 做字段类型校验（只检查最表层）。
    - 容器只校验容器本身类型，不校验内部元素类型
    - Enum 必须是 Enum 实例，不能用原始值代替
    """

    __slots__ = ()

    def __post_init__(self) -> None:
        # 兼容 cooperative multiple inheritance
        super_post = getattr(super(), "__post_init__", None)
        if callable(super_post):
            super_post()

        self.validate_types()

    def validate_types(self) -> None:
        cls = self.__class__
        hints = _cached_type_hints(cls)

        errors: list[str] = []
        for f in _cache_cls_fields(cls):
            name = f.name
            if name not in hints:
                continue

            expected = hints[name]
            value = getattr(self, name)

            if not _shallow_isinstance(value, expected):
                errors.append(
                    f"{name}: expected {_type_repr(_strip_wrappers(expected))}, "
                    f"got {type(value).__name__} ({value!r})"
                )

        if errors:
            raise TypeError(
                f"{cls.__name__} type validation failed:\n- " + "\n- ".join(errors)
            )
