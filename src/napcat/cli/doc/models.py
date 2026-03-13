"""
Structured models for doc queries.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ProblemKind = Literal["invalid_input", "not_found", "internal"]
CodeEntryCategory = Literal["module", "api-definitions", "typed-dicts"]


@dataclass(slots=True, frozen=True)
class DocProblem:
    kind: ProblemKind
    message: str
    target: str | None = None


@dataclass(slots=True, frozen=True)
class ApiIndexItem:
    name: str
    description: str


@dataclass(slots=True, frozen=True)
class ApiDetailItem:
    name: str
    found: bool
    signature: str | None
    description: str | None
    response_type: str | None
    typed_dict_codes: tuple[str, ...] = ()
    problems: tuple[DocProblem, ...] = ()


@dataclass(slots=True, frozen=True)
class CodeIndexEntry:
    path: str
    summary: str | None
    category: CodeEntryCategory


@dataclass(slots=True, frozen=True)
class CodeFileItem:
    path: str
    found: bool
    content: str | None
    problems: tuple[DocProblem, ...] = ()


@dataclass(slots=True, frozen=True)
class ClassDefinitionSource:
    path: str
    code: str


@dataclass(slots=True, frozen=True)
class ClassDefinitionItem:
    name: str
    found: bool
    sources: tuple[ClassDefinitionSource, ...]
    problems: tuple[DocProblem, ...] = ()


@dataclass(slots=True, frozen=True)
class AgentBundleSection:
    title: str
    content: str


@dataclass(slots=True, frozen=True)
class OperationResult[T]:
    ok: bool
    items: tuple[T, ...]
    problems: tuple[DocProblem, ...] = ()
