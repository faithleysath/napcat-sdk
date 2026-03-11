"""Generate `src/napcat/matcher.pyi` from final event dataclasses."""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import fields, is_dataclass
from pathlib import Path
from types import UnionType
from typing import Any, Literal, TypeAliasType, get_args, get_origin, get_type_hints

DEFAULT_OUTPUT = Path("src/napcat/matcher.pyi")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _ensure_src_path() -> None:
    src = _repo_root() / "src"
    src_str = str(src)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)


def _load_event_classes() -> list[type[Any]]:
    _ensure_src_path()

    import napcat.types.events as events
    from napcat.types.events.base import NapCatEvent

    result: list[type[Any]] = []
    for name in events.__all__:
        obj = getattr(events, name, None)
        if not isinstance(obj, type):
            continue
        if not is_dataclass(obj):
            continue
        if not issubclass(obj, NapCatEvent):
            continue
        result.append(obj)
    return sorted(result, key=lambda cls: cls.__name__)


def _iter_dataclass_field_types(cls: type[Any]) -> Iterable[Any]:
    hints = get_type_hints(cls, include_extras=True)
    for field in fields(cls):
        if field.name.startswith("_") or not field.init:
            continue
        yield hints.get(field.name)


def _walk_nested_dataclasses(root_events: list[type[Any]]) -> list[type[Any]]:
    queue = list(root_events)
    seen: set[type[Any]] = set()

    def enqueue_type(tp: Any) -> None:
        origin = get_origin(tp)
        if origin is not None or isinstance(tp, UnionType):
            for arg in get_args(tp):
                enqueue_type(arg)
            return
        if isinstance(tp, TypeAliasType):
            return
        if isinstance(tp, type) and tp is not type(None) and is_dataclass(tp):
            queue.append(tp)

    while queue:
        cls = queue.pop()
        if cls in seen:
            continue
        seen.add(cls)
        for tp in _iter_dataclass_field_types(cls):
            if tp is not None:
                enqueue_type(tp)

    return sorted(seen, key=lambda cls: cls.__name__)


def _validate_unique_class_names(classes: list[type[Any]]) -> None:
    grouped: dict[str, list[str]] = defaultdict(list)
    for cls in classes:
        grouped[cls.__name__].append(cls.__module__)

    duplicated = {
        name: modules for name, modules in grouped.items() if len(modules) > 1
    }
    if duplicated:
        lines = [
            f"{name}: {', '.join(sorted(modules))}"
            for name, modules in sorted(duplicated.items())
        ]
        raise ValueError(
            "Matcher stub generation requires globally unique dataclass names:\n"
            + "\n".join(lines)
        )


class ImportRegistry:
    def __init__(self) -> None:
        self._names_by_module: dict[str, set[str]] = defaultdict(set)

    def add(self, module: str, name: str) -> None:
        if module == "builtins":
            return
        self._names_by_module[module].add(name)

    def render(self) -> list[str]:
        lines: list[str] = []
        for module in sorted(self._names_by_module, key=str.lower):
            relative = "." + module.removeprefix("napcat.")
            names = sorted(self._names_by_module[module], key=str.lower)
            single_line = f"from {relative} import {', '.join(names)}"
            if len(single_line) <= 88 and len(names) <= 3:
                lines.append(single_line)
                continue

            lines.append(f"from {relative} import (")
            lines.extend(f"    {name}," for name in names)
            lines.append(")")
        return lines


def _pattern_name(cls: type[Any]) -> str:
    return f"{cls.__name__}Pattern"


def _format_type(tp: Any, imports: ImportRegistry) -> str:
    origin = get_origin(tp)

    if tp is Any:
        return "Any"

    if tp is Ellipsis:
        return "..."

    if tp is type(None):
        return "None"

    if isinstance(tp, TypeAliasType):
        imports.add(tp.__module__, tp.__name__)
        return tp.__name__

    if origin is Literal:
        args = ", ".join(repr(arg) for arg in get_args(tp))
        return f"Literal[{args}]"

    if origin is dict:
        key_type, value_type = get_args(tp)
        return f"dict[{_format_type(key_type, imports)}, {_format_type(value_type, imports)}]"

    if origin is list:
        (item_type,) = get_args(tp)
        return f"list[{_format_type(item_type, imports)}]"

    if origin is set:
        (item_type,) = get_args(tp)
        return f"set[{_format_type(item_type, imports)}]"

    if origin is frozenset:
        (item_type,) = get_args(tp)
        return f"frozenset[{_format_type(item_type, imports)}]"

    if origin is tuple:
        tuple_args = get_args(tp)
        if len(tuple_args) == 2 and tuple_args[1] is Ellipsis:
            return f"tuple[{_format_type(tuple_args[0], imports)}, ...]"
        return (
            "tuple[" + ", ".join(_format_type(arg, imports) for arg in tuple_args) + "]"
        )

    if origin is not None or isinstance(tp, UnionType):
        return " | ".join(_format_type(arg, imports) for arg in get_args(tp))

    if isinstance(tp, type):
        imports.add(tp.__module__, tp.__name__)
        return tp.__name__

    return "Any"


def _format_pattern_type(
    tp: Any,
    *,
    dataclass_names: set[str],
    imports: ImportRegistry,
) -> str:
    actual = _format_type(tp, imports)

    if isinstance(tp, type) and tp.__name__ in dataclass_names and is_dataclass(tp):
        return f"{_pattern_name(tp)} | PredicateLike[{actual}]"

    return f"{actual} | PredicateLike[{actual}]"


def build_matcher_stub() -> str:
    event_classes = _load_event_classes()
    dataclass_classes = _walk_nested_dataclasses(event_classes)
    _validate_unique_class_names(dataclass_classes)

    imports = ImportRegistry()
    dataclass_names = {cls.__name__ for cls in dataclass_classes}

    pattern_blocks: list[str] = []
    for cls in dataclass_classes:
        hints = get_type_hints(cls, include_extras=True)
        field_lines: list[str] = []
        for field in fields(cls):
            if field.name.startswith("_") or not field.init:
                continue
            annotation = _format_pattern_type(
                hints.get(field.name, Any),
                dataclass_names=dataclass_names,
                imports=imports,
            )
            field_lines.append(f"    {field.name}: {annotation}")

        if field_lines:
            pattern_body = "\n".join(field_lines)
        else:
            pattern_body = "    pass"

        pattern_blocks.append(
            f"class {_pattern_name(cls)}(TypedDict, total=False):\n{pattern_body}"
        )

    overloads: list[str] = []
    for cls in event_classes:
        imports.add(cls.__module__, cls.__name__)
        overloads.append(
            "\n".join(
                [
                    "@overload",
                    "def event_match(",
                    f"    event_type: type[{cls.__name__}],",
                    "    /,",
                    f"    **pattern: Unpack[{_pattern_name(cls)}],",
                    ") -> Predicate[NapCatEvent]: ...",
                ]
            )
        )

    imports.add("napcat.types.events.base", "NapCatEvent")

    sections = [
        "# Auto-generated file. Do not modify directly.",
        "",
        "from __future__ import annotations",
        "",
        "from collections.abc import Callable",
        "from types import UnionType",
        "from typing import Any, Literal, TypedDict, Unpack, overload",
        "",
        *imports.render(),
        "",
        "class Predicate[T]:",
        "    def __call__(self, value: T, /) -> bool: ...",
        "    def __or__(self, other: Callable[[T], bool] | Predicate[T], /) -> Predicate[T]: ...",
        "    def __ror__(self, other: Callable[[T], bool] | Predicate[T], /) -> Predicate[T]: ...",
        "    def __and__(self, other: Callable[[T], bool] | Predicate[T], /) -> Predicate[T]: ...",
        "    def __rand__(self, other: Callable[[T], bool] | Predicate[T], /) -> Predicate[T]: ...",
        "",
        "type PredicateLike[T] = Callable[[T], bool] | Predicate[T]",
        "",
        "TRUE: Predicate[Any]",
        "FALSE: Predicate[Any]",
        "",
        *pattern_blocks,
        "",
        *overloads,
        "",
        "@overload",
        "def event_match(",
        "    event_type: type[NapCatEvent],",
        "    /,",
        "    **pattern: Any,",
        ") -> Predicate[NapCatEvent]: ...",
        "",
        "@overload",
        "def event_match(",
        "    event_type: UnionType,",
        "    /,",
        "    **pattern: Any,",
        ") -> Predicate[NapCatEvent]: ...",
        "",
        "def event_match(",
        "    event_type: type[NapCatEvent] | UnionType,",
        "    /,",
        "    **pattern: Any,",
        ") -> Predicate[NapCatEvent]: ...",
        "",
    ]
    return "\n".join(sections)


def write_stub(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate src/napcat/matcher.pyi")
    parser.add_argument("--out", default=str(DEFAULT_OUTPUT), help="Output .pyi path")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if the generated content differs from the existing file",
    )
    ns = parser.parse_args()

    output_path = Path(ns.out)
    content = build_matcher_stub()

    if ns.check:
        if not output_path.is_file():
            print(f"Missing generated stub: {output_path}")
            return 1
        existing = output_path.read_text(encoding="utf-8")
        if existing != content:
            print(f"Outdated generated stub: {output_path}")
            return 1
        print(f"Matcher stub is up to date: {output_path}")
        return 0

    write_stub(output_path, content)
    print(f"Wrote matcher stub to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
