"""
doc 命令

查询 NapCat SDK 文档。
"""

from __future__ import annotations

import json
import sys
from typing import Any

from ..doc.registry import get_cli_operation, list_cli_operations
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
    full: bool = False,
    with_code: bool = False,
) -> int:
    """
    文档查询命令

    Args:
        doc_command: 子命令名称
        json_output: 是否以 JSON 格式输出
        names: API 或类名列表
        paths: 文件路径列表
        full: 是否输出扩展的大上下文文档包
        with_code: 是否内嵌关键源码文件

    Returns:
        退出码
    """
    if doc_command is None:
        _print_doc_help()
        return 0

    return _run_doc_operation(
        doc_command,
        json_output=json_output,
        names=names,
        paths=paths,
        full=full,
        with_code=with_code,
    )


def _print_doc_help() -> None:
    print("Usage: napcat-sdk doc <command> [options]")
    print("\nCommands:")
    for spec in list_cli_operations():
        if spec.cli_usage is None or spec.cli_help is None:
            continue
        print(f"  {spec.cli_usage:<18} {spec.cli_help}")
    print("\nOptions:")
    print("  --json             Output in JSON format")


def _run_doc_operation(
    doc_command: str,
    *,
    json_output: bool,
    names: list[str] | None = None,
    paths: list[str] | None = None,
    full: bool = False,
    with_code: bool = False,
) -> int:
    spec = get_cli_operation(doc_command)
    if spec is None:
        print_error(f"Unknown doc command: {doc_command}")
        return 1

    try:
        service = DocService()
        args = _collect_doc_arguments(
            names=names,
            paths=paths,
            full=full,
            with_code=with_code,
        )

        normalized_args = spec.normalize_arguments(args)
        result = spec.invoke(service, normalized_args)
        if json_output:
            data = spec.render_json(result)
            print_json(data)
        else:
            print(spec.render_text(result))
        return 0 if result.ok else 1
    except BrokenPipeError:
        return 0
    except ValueError as e:
        print_error(str(e))
        if spec.cli_usage is not None:
            print(f"Usage: napcat-sdk doc {spec.cli_usage}")
        return 1
    except Exception as e:
        print_error(str(e))
        return 1


def _collect_doc_arguments(
    *,
    names: list[str] | None,
    paths: list[str] | None,
    full: bool,
    with_code: bool,
) -> dict[str, Any]:
    args: dict[str, Any] = {}
    if names is not None:
        args["names"] = names
    if paths is not None:
        args["paths"] = paths
    args["full"] = full
    args["with_code"] = with_code
    return args
