import logging
from collections.abc import (
    Iterable as ABCIterable,
)
from collections.abc import (
    Mapping as ABCMapping,
)
from collections.abc import (
    MutableMapping as ABCMutableMapping,
)
from collections.abc import (
    Sequence as ABCSequence,
)
from dataclasses import MISSING, fields, is_dataclass
from enum import Enum
from types import UnionType
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Iterable,
    Literal,
    Mapping,
    MutableMapping,
    Protocol,
    Self,
    Sequence,
    Union,
    cast,
    get_args,
    get_origin,
    get_type_hints,
    runtime_checkable,
)

logger = logging.getLogger("napcat.types.utils")


@runtime_checkable
class DataclassProtocol(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Any]]


class IgnoreExtraArgsMixin(DataclassProtocol):
    __slots__ = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
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


class IgnoreExtraArgsInternalMixin(DataclassProtocol):
    __slots__ = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
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


class TypeValidatorMixin(DataclassProtocol):
    __slots__ = ()
    _type_hints_cache: ClassVar[dict[type, dict[str, Any] | None]] = {}

    def __post_init__(self):
        cls = self.__class__
        cache = self._type_hints_cache
        if cls not in cache or cache[cls] is None:
            try:
                cache[cls] = get_type_hints(cls, include_extras=True)
            except Exception as e:
                logger.warning(f"Failed to resolve type hints for {cls.__name__}: {e}")
                cache[cls] = None

        hints = cache[cls] or {}

        for f in fields(self):
            name = f.name
            if name not in hints:
                continue

            # 缩小 try 范围，只针对属性获取
            try:
                val = getattr(self, name)
            except AttributeError:
                continue

            tp = hints[name]

            try:
                # 传递 name 用于日志调试
                new_val = self._validate(tp, val, name)
                # 使用 object.__setattr__ 以支持 frozen dataclasses
                if new_val is not val:
                    object.__setattr__(self, name, new_val)
            except Exception as e:
                raise ValueError(f"Validation failed for field '{name}': {e}") from e

    def _validate(self, tp: Any, val: Any, name: str = "") -> Any:
        # [Fix] 优先处理 Any，避免后续 isinstance(val, Any) 报错
        if tp is Any:
            return val

        origin = get_origin(tp)
        args = get_args(tp)

        # 0. Unwrap Annotated
        if origin is Annotated:
            return self._validate(args[0], val, name)

        # 1. None Check
        if val is None:
            is_optional = tp is type(None) or (
                origin in (Union, UnionType) and type(None) in args
            )
            if is_optional:
                return None
            raise ValueError(f"Field '{name}' cannot be None")

        # 2. Fast Path: Exact Match
        # [Fix] 增加对 type(None) 的保护，虽然 get_origin 处理了大部分
        if origin is None and not is_dataclass(tp) and not isinstance(val, Enum):
            try:
                if isinstance(val, tp):
                    return val
            except TypeError:
                # 某些特殊类型（如 NewType 或一些 Callable）可能不支持 isinstance
                pass

        # 3. Enum Handling
        if isinstance(tp, type) and issubclass(tp, Enum):
            if isinstance(val, tp):
                return val
            if isinstance(val, Enum):
                val = val.value

            try:
                ret = tp(val)
                logger.debug(f"🔄 Coerced {name}: {val!r} -> {ret}")
                return ret
            except ValueError:
                pass

            # 支持字符串名查找
            if isinstance(val, str) and val in tp.__members__:
                ret = tp[val]
                logger.debug(f"🔄 Coerced {name}: {val!r} -> {ret}")
                return ret

            raise ValueError(f"{val!r} is not a valid {tp.__name__}")

        # 4. Union Handling
        if origin in (Union, UnionType):
            # Pass 1: Strict Check
            for arg in args:
                if arg is type(None):
                    continue
                origin_arg = get_origin(arg)
                # 只有非容器、非泛型才做 strict check，避免泛型 List[int] 在这里报错
                if origin_arg is None and not is_dataclass(arg) and arg is not Any:
                    try:
                        if isinstance(val, arg):
                            return val
                    except TypeError:
                        pass

            # Pass 2: Coercion
            errs = []
            for arg in args:
                if arg is type(None):
                    continue
                try:
                    return self._validate(arg, val, name)
                except (ValueError, TypeError) as e:
                    errs.append(str(e))
                    continue
            raise TypeError(f"Expected {tp}, got {val!r}. Errors: {'; '.join(errs)}")

        # 5. Tuple Handling
        if origin is tuple:
            if not isinstance(val, (list, tuple)):
                raise TypeError(f"Expected tuple/list for {name}, got {type(val)}")

            if len(args) == 2 and args[1] is Ellipsis:
                item_tp = args[0]
                return tuple(
                    self._validate(item_tp, v, f"{name}[{i}]")
                    for i, v in enumerate(val)
                )

            if args:
                if len(val) != len(args):
                    raise ValueError(
                        f"Expected tuple of length {len(args)}, got {len(val)}"
                    )
                return tuple(
                    self._validate(arg_tp, v, f"{name}[{i}]")
                    for i, (arg_tp, v) in enumerate(zip(args, val))
                )

            return tuple(val)

        # 6. List/Set/Sequence/Iterable Handling
        if origin in (list, set, frozenset):
            if not isinstance(val, (list, tuple, set, frozenset)):
                raise TypeError(f"Expected iterable for {name}, got {type(val)}")
            item_tp = args[0] if args else Any
            new_items = [
                self._validate(item_tp, v, f"{name}[{i}]") for i, v in enumerate(val)
            ]
            return origin(new_items)

        # tuple 单独你原来已经处理过（#5），这里不用管

        # typing.Sequence / typing.Iterable / collections.abc.Sequence / collections.abc.Iterable
        if origin in (ABCSequence, ABCIterable) or tp in (Sequence, Iterable):
            # 防止把 str/bytes 当成 iterable 拆字符
            if isinstance(val, (str, bytes, bytearray)):
                raise TypeError(f"Expected iterable for {name}, got scalar {type(val)}")
            # 防止 dict 被当 iterable（遍历 key）
            if isinstance(val, ABCMapping):
                raise TypeError(
                    f"Expected iterable for {name}, got mapping {type(val)}"
                )
            if not isinstance(val, ABCIterable):
                raise TypeError(f"Expected iterable for {name}, got {type(val)}")

            item_tp = args[0] if args else Any
            new_items = [
                self._validate(item_tp, v, f"{name}[{i}]") for i, v in enumerate(val)
            ]
            return list(new_items)

        # 7. Dict/Mapping Handling
        if origin in (dict, ABCMapping, ABCMutableMapping, Mapping, MutableMapping):
            if not isinstance(val, ABCMapping):
                raise TypeError(f"Expected mapping for {name}, got {type(val)}")

            kt, vt = args if len(args) == 2 else (Any, Any)
            return {
                self._validate(kt, k, f"{name}.k"): self._validate(vt, v, f"{name}.v")
                for k, v in val.items()
            }

        # 8. Literal
        if origin is Literal:
            if val in args:
                return val
            val_str = str(val)
            for opt in args:
                # 限制只尝试基础类型的 coercion，避免对象转 str 后误判
                if type(opt) in (int, bool, float, str) and str(opt) == val_str:
                    logger.debug(f"🔄 Coerced {name}: {val!r} -> Literal[{opt}]")
                    return opt
            raise ValueError(f"Expected {args}, got {val!r}")

        # 9. Nested Dataclass
        if isinstance(val, dict) and isinstance(tp, type) and is_dataclass(tp):
            valid_field_names = {f.name for f in fields(tp) if f.init}
            filtered_val = {k: v for k, v in val.items() if k in valid_field_names}

            from_dict = getattr(tp, "from_dict", None)
            if from_dict is not None:
                from_dict_fn = cast(Callable[[dict[str, Any]], Any], from_dict)
                return from_dict_fn(filtered_val)
            return tp(**filtered_val)

        # 10. Primitives Coercion (numbers <-> strings only)
        # 只支持：str <-> int/float，int <-> float（可选），以及数值 -> str
        if tp is int:
            if isinstance(val, int) and not isinstance(val, bool):
                return val

            # str -> int
            if isinstance(val, str):
                s = val.strip()
                try:
                    ret = int(s)
                    logger.warning(f"🔄 Coerced {name}: {val!r} -> {ret!r}")
                    return ret
                except ValueError:
                    pass

            # float -> int（只接受整数形态，比如 3.0）
            if isinstance(val, float) and val.is_integer():
                ret = int(val)
                logger.warning(f"🔄 Coerced {name}: {val!r} -> {ret!r}")
                return ret

            # 其他一律不在这里处理，交给后续 fallback 报错
            # （你外层会最终 raise TypeError）
            pass

        if tp is float:
            if isinstance(val, float):
                return val

            # int -> float
            if isinstance(val, int) and not isinstance(val, bool):
                ret = float(val)
                logger.warning(f"🔄 Coerced {name}: {val!r} -> {ret!r}")
                return ret

            # str -> float
            if isinstance(val, str):
                s = val.strip()
                try:
                    ret = float(s)
                    logger.warning(f"🔄 Coerced {name}: {val!r} -> {ret!r}")
                    return ret
                except ValueError:
                    pass

            pass

        if tp is str:
            if isinstance(val, str):
                return val

            # int/float -> str
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                ret = str(val)
                logger.warning(f"🔄 Coerced {name}: {val!r} -> {ret!r}")
                return ret

            pass

        # [Final Fallback]
        # 如果什么都没匹配到，且 origin 为 None（普通类），尝试最后一次类型检查
        if origin is None and isinstance(tp, type):
            if isinstance(val, tp):
                return val

        raise TypeError(f"Cannot validate {val!r} as {tp}")
