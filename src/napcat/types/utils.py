import logging
from dataclasses import MISSING, fields
from enum import Enum
from types import UnionType
from typing import (
    Any,
    ClassVar,
    Literal,
    Protocol,
    Self,
    Union,
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
        cls_fields = {f.name: f for f in fields(cls) if f.init}
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
        cls_fields = {f.name: f for f in fields(cls) if f.init}
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


class TypeValidatorMixin:
    __slots__ = ()

    # cls -> list[(field_name, kind, payload, expected)] | None
    _spec_cache: ClassVar[dict[type, list[tuple[str, str, Any, str]] | None]] = {}
    _CACHE_MISS = object()

    def __post_init__(self):
        cls = self.__class__

        # (1) fix: cache None properly (avoid rebuilding spec forever)
        spec = self._spec_cache.get(cls, self._CACHE_MISS)
        if spec is self._CACHE_MISS:
            spec = self._build_spec(cls)  # may be None
            self._spec_cache[cls] = spec

        if not spec:
            return

        getv = getattr
        if isinstance(spec, list):
            for name, kind, payload, expected in spec:
                v = getv(self, name)

                ok = self._check(kind, payload, v)
                if not ok:
                    raise TypeError(
                        f"Field '{name}' expected {expected}, got {type(v).__name__}: {v!r}"
                    )

    @staticmethod
    def _isinstance_no_bool(v: Any, tp_or_tuple: Any) -> bool:
        """
        (4) fix: treat bool as NOT int unless bool is explicitly allowed.
        - isinstance(True, int) == True in Python, we usually don't want that.
        """
        if isinstance(tp_or_tuple, tuple):
            if isinstance(v, bool):
                return bool in tp_or_tuple
            return isinstance(v, tp_or_tuple)

        tp = tp_or_tuple
        if tp is int and isinstance(v, bool):
            return False
        return isinstance(v, tp)

    @classmethod
    def _check(cls, kind: str, payload: Any, v: Any) -> bool:
        # Any always passes
        if kind == "any":
            return True

        # (6) fix: merge duplicated branches (type/origin/enum are all isinstance checks)
        if kind in ("type", "origin", "enum"):
            return cls._isinstance_no_bool(v, payload)

        if kind == "literal":
            return v in payload

        if kind == "union_types":
            types_tuple, allow_none = payload
            if v is None:
                return bool(allow_none)
            return cls._isinstance_no_bool(v, types_tuple)

        # (3) fix: support unions like Optional[list[int]] etc (shallow branch checking)
        if kind == "union":
            branch_specs, allow_none, has_uncheckable = payload
            if v is None:
                return bool(allow_none)

            for b_kind, b_payload, _b_expected in branch_specs:
                if cls._check(b_kind, b_payload, v):
                    return True

            # if union contains uncheckable branches, don't raise false negatives
            return bool(has_uncheckable)

        # unknown kind -> skip (keep previous behavior)
        return True

    @classmethod
    def _build_spec(cls, target_cls: type):
        try:
            hints = get_type_hints(target_cls, include_extras=False)
        except Exception as e:
            logger.warning(
                f"Failed to resolve type hints for {target_cls.__name__}: {e}"
            )
            return None

        out: list[tuple[str, str, Any, str]] = []
        for f in fields(target_cls):
            tp = hints.get(f.name)
            if tp is None:
                continue
            kind, payload, expected = cls._compile(tp)
            if kind != "skip":
                out.append((f.name, kind, payload, expected))
        return out

    @staticmethod
    def _compile(tp: Any) -> tuple[str, Any, str]:
        if tp is Any:
            return "any", None, "Any"

        origin = get_origin(tp)
        args = get_args(tp)

        if origin is Literal:
            return "literal", set(args), f"Literal{args}"

        if isinstance(tp, type) and issubclass(tp, Enum):
            return "enum", tp, tp.__name__

        if origin in (Union, UnionType):
            allow_none = type(None) in args
            branches = [a for a in args if a is not type(None)]

            # fast path: union of plain types -> old behavior kept
            if branches and all(isinstance(a, type) for a in branches):
                return "union_types", (tuple(branches), allow_none), str(tp)

            # (3) new path: compile checkable branches; keep track of uncheckables
            branch_specs: list[tuple[str, Any, str]] = []
            has_uncheckable = False
            for b in branches:
                b_kind, b_payload, b_expected = TypeValidatorMixin._compile(b)
                if b_kind == "skip":
                    has_uncheckable = True
                else:
                    branch_specs.append((b_kind, b_payload, b_expected))

            # If nothing checkable, just skip (can't validate)
            if not branch_specs:
                return "skip", None, str(tp)

            return "union", (branch_specs, allow_none, has_uncheckable), str(tp)

        if origin is not None:
            try:
                return "origin", origin, getattr(origin, "__name__", str(origin))
            except TypeError:
                return "skip", None, str(tp)

        if isinstance(tp, type):
            return "type", tp, tp.__name__

        return "skip", None, str(tp)
