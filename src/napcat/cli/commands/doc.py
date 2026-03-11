"""
doc 命令

查询 NapCat SDK 文档。
"""

from __future__ import annotations

import json
import sys
from typing import Any

from ..doc.registry import get_cli_operation
from ..doc.service import DocService


def print_error(msg: str) -> None:
    """打印错误信息到 stderr"""
    print(f"\033[91mError:\033[0m {msg}", file=sys.stderr)


def print_json(data: Any) -> None:
    """打印 JSON 格式输出"""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_doc(
    doc_command: str | None,
    json_output: bool = False,
    names: list[str] | None = None,
    paths: list[str] | None = None,
) -> int:
    """
    文档查询命令

    Args:
        doc_command: 子命令名称
        json_output: 是否以 JSON 格式输出
        names: API 或类名列表
        paths: 文件路径列表

    Returns:
        退出码
    """
    if doc_command is None:
        print("Usage: napcat-sdk doc <command> [options]")
        print("\nCommands:")
        print("  apis               List all available APIs")
        print("  api <NAME>...      Get API details")
        print("  files              List source code files")
        print("  code <PATH>...     View source code file")
        print("  class <NAME>...    View class definition")
        print("\nOptions:")
        print("  --json             Output in JSON format")
        return 0

    match doc_command:
        case "apis":
            return _run_doc_operation(doc_command, json_output=json_output)
        case "api":
            if not names:
                print_error("API name(s) required.")
                print("Usage: napcat-sdk doc api <NAME> [NAME ...]")
                return 1
            return _run_doc_operation(doc_command, json_output=json_output, names=names)
        case "files":
            return _run_doc_operation(doc_command, json_output=json_output)
        case "code":
            if not paths:
                print_error("File path(s) required.")
                print("Usage: napcat-sdk doc code <PATH> [PATH ...]")
                return 1
            return _run_doc_operation(doc_command, json_output=json_output, paths=paths)
        case "class":
            if not names:
                print_error("Class name(s) required.")
                print("Usage: napcat-sdk doc class <NAME> [NAME ...]")
                return 1
            return _run_doc_operation(doc_command, json_output=json_output, names=names)
        case _:
            print_error(f"Unknown doc command: {doc_command}")
            return 1


def _run_doc_operation(
    doc_command: str,
    *,
    json_output: bool,
    names: list[str] | None = None,
    paths: list[str] | None = None,
) -> int:
    try:
        spec = get_cli_operation(doc_command)
        if spec is None:
            print_error(f"Unknown doc command: {doc_command}")
            return 1

        service = DocService()
        args: dict[str, Any] = {}
        if names is not None:
            args["names"] = names
        if paths is not None:
            args["paths"] = paths

        normalized_args = spec.normalize_arguments(args)
        result = spec.invoke(service, normalized_args)
        if json_output:
            data = spec.render_json(result)
            print_json(data)
        else:
            print(spec.render_text(result))
        return 0 if result.ok else 1
    except Exception as e:
        print_error(str(e))
        return 1
