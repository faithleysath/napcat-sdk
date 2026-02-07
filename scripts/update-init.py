"""
Update aggregate __init__.py files for napcat types exports.

This script updates only auto-generated export marker blocks in:
- src/napcat/types/events/__init__.py
- src/napcat/types/__init__.py
- src/napcat/__init__.py

Data sources:
- src/napcat/types/events/notice/__init__.py  (__all__)
- src/napcat/types/messages/__init__.py       (__all__)
"""

from __future__ import annotations

import ast
from pathlib import Path

NOTICE_INIT = Path("src/napcat/types/events/notice/__init__.py")
MESSAGES_INIT = Path("src/napcat/types/messages/__init__.py")
EVENTS_INIT = Path("src/napcat/types/events/__init__.py")
TYPES_INIT = Path("src/napcat/types/__init__.py")
NAPCAT_INIT = Path("src/napcat/__init__.py")


EVENTS_NOTICE_EXPORTS_START = "# >>> AUTO-GENERATED: NOTICE EXPORTS START"
EVENTS_NOTICE_EXPORTS_END = "# <<< AUTO-GENERATED: NOTICE EXPORTS END"

TYPES_EVENTS_EXPORTS_START = "# >>> AUTO-GENERATED: EVENTS EXPORTS START"
TYPES_EVENTS_EXPORTS_END = "# <<< AUTO-GENERATED: EVENTS EXPORTS END"

TYPES_MESSAGE_EXPORTS_START = "# >>> AUTO-GENERATED: MESSAGE EXPORTS START"
TYPES_MESSAGE_EXPORTS_END = "# <<< AUTO-GENERATED: MESSAGE EXPORTS END"

NAPCAT_TYPES_EXPORTS_START = "# >>> AUTO-GENERATED: TYPES EXPORTS START"
NAPCAT_TYPES_EXPORTS_END = "# <<< AUTO-GENERATED: TYPES EXPORTS END"


def parse_dunder_all(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    module = ast.parse(source)

    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        if len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name) or target.id != "__all__":
            continue
        if not isinstance(node.value, (ast.List, ast.Tuple)):
            raise ValueError(f"{path}: __all__ is not a list/tuple literal")

        items: list[str] = []
        for elt in node.value.elts:
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                items.append(elt.value)
                continue
            raise ValueError(f"{path}: __all__ contains non-string literal")
        return items

    raise ValueError(f"{path}: __all__ not found")


def replace_marker_block(text: str, start_marker: str, end_marker: str, block: str) -> str:
    start_idx = text.find(start_marker)
    if start_idx < 0:
        raise ValueError(f"start marker not found: {start_marker}")

    end_idx = text.find(end_marker, start_idx)
    if end_idx < 0:
        raise ValueError(f"end marker not found: {end_marker}")

    start_line_end = text.find("\n", start_idx)
    if start_line_end < 0:
        raise ValueError(f"invalid marker line: {start_marker}")

    end_line_start = text.rfind("\n", 0, end_idx)
    if end_line_start < 0:
        end_line_start = 0
    else:
        end_line_start += 1

    new_block = block.rstrip("\n") + "\n"
    return text[: start_line_end + 1] + new_block + text[end_line_start:]


def format_export_items(names: list[str], indent: str = "    ") -> str:
    return "\n".join(f'{indent}"{name}",' for name in names)


def update_events_init(notice_exports: list[str]) -> None:
    source = EVENTS_INIT.read_text(encoding="utf-8")
    source = replace_marker_block(
        source,
        EVENTS_NOTICE_EXPORTS_START,
        EVENTS_NOTICE_EXPORTS_END,
        format_export_items(notice_exports),
    )
    EVENTS_INIT.write_text(source, encoding="utf-8")


def update_types_init(event_exports: list[str], message_exports: list[str]) -> None:
    source = TYPES_INIT.read_text(encoding="utf-8")
    source = replace_marker_block(
        source,
        TYPES_EVENTS_EXPORTS_START,
        TYPES_EVENTS_EXPORTS_END,
        format_export_items(event_exports),
    )
    source = replace_marker_block(
        source,
        TYPES_MESSAGE_EXPORTS_START,
        TYPES_MESSAGE_EXPORTS_END,
        format_export_items(message_exports),
    )
    TYPES_INIT.write_text(source, encoding="utf-8")


def update_napcat_init(type_exports: list[str]) -> None:
    source = NAPCAT_INIT.read_text(encoding="utf-8")
    source = replace_marker_block(
        source,
        NAPCAT_TYPES_EXPORTS_START,
        NAPCAT_TYPES_EXPORTS_END,
        format_export_items(type_exports),
    )
    NAPCAT_INIT.write_text(source, encoding="utf-8")


def main() -> int:
    notice_exports = parse_dunder_all(NOTICE_INIT)
    update_events_init(notice_exports)

    event_exports = parse_dunder_all(EVENTS_INIT)
    message_exports = parse_dunder_all(MESSAGES_INIT)
    update_types_init(event_exports, message_exports)
    type_exports = parse_dunder_all(TYPES_INIT)
    update_napcat_init(type_exports)

    print(f"Updated: {EVENTS_INIT}")
    print(f"Updated: {TYPES_INIT}")
    print(f"Updated: {NAPCAT_INIT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
