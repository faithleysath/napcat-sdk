"""
doc 命令

查询 NapCat SDK 文档。
"""

from __future__ import annotations

import json
import sys
from typing import Any

from ..doc import (
    logic_get_class_details,
    logic_get_code_file,
    logic_get_code_index,
    logic_get_details,
    logic_get_index,
    logic_get_llms_txt,
    logic_get_missing_apis,
    logic_get_missing_classes,
)


def _is_logic_error(result: str) -> bool:
    """判断 logic 层返回是否为错误结果"""
    return result.startswith("# Error")


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
        print("  llms               View llms.txt documentation")
        print("\nOptions:")
        print("  --json             Output in JSON format")
        return 0

    match doc_command:
        case "apis":
            return _handle_apis(json_output)
        case "api":
            if not names:
                print_error("API name(s) required.")
                print("Usage: napcat-sdk doc api <NAME> [NAME ...]")
                return 1
            return _handle_api(names, json_output)
        case "files":
            return _handle_files(json_output)
        case "code":
            if not paths:
                print_error("File path(s) required.")
                print("Usage: napcat-sdk doc code <PATH> [PATH ...]")
                return 1
            return _handle_code(paths, json_output)
        case "class":
            if not names:
                print_error("Class name(s) required.")
                print("Usage: napcat-sdk doc class <NAME> [NAME ...]")
                return 1
            return _handle_class(names, json_output)
        case "llms":
            return _handle_llms(json_output)
        case _:
            print_error(f"Unknown doc command: {doc_command}")
            return 1


def _handle_apis(json_output: bool) -> int:
    """处理 doc apis 命令"""
    try:
        result = logic_get_index()
        if json_output:
            data = _parse_api_index(result)
            print_json(data)
        else:
            print(result)
        return 0
    except Exception as e:
        print_error(str(e))
        return 1


def _handle_api(names: list[str], json_output: bool) -> int:
    """处理 doc api 命令"""
    try:
        result = logic_get_details(names)
        missing = logic_get_missing_apis(names)
        if json_output:
            data = {"apis": names, "result": result}
            print_json(data)
        else:
            print(result)
        return 1 if missing else 0
    except Exception as e:
        print_error(str(e))
        return 1


def _handle_files(json_output: bool) -> int:
    """处理 doc files 命令"""
    try:
        result = logic_get_code_index()
        if json_output:
            data = {"result": result}
            print_json(data)
        else:
            print(result)
        return 0
    except Exception as e:
        print_error(str(e))
        return 1


def _handle_code(paths: list[str], json_output: bool) -> int:
    """处理 doc code 命令"""
    try:
        has_error = False
        if json_output:
            data: list[dict[str, str]] = []
            for p in paths:
                content = logic_get_code_file(p)
                if _is_logic_error(content):
                    has_error = True
                data.append({"path": p, "content": content})
            print_json(data)
        else:
            results = [logic_get_code_file(p) for p in paths]
            has_error = any(_is_logic_error(result) for result in results)
            print("\n\n---\n\n".join(results))
        return 1 if has_error else 0
    except Exception as e:
        print_error(str(e))
        return 1


def _handle_class(names: list[str], json_output: bool) -> int:
    """处理 doc class 命令"""
    try:
        result = logic_get_class_details(names)
        missing = logic_get_missing_classes(names)
        if json_output:
            data = {"classes": names, "result": result}
            print_json(data)
        else:
            print(result)
        return 1 if missing else 0
    except Exception as e:
        print_error(str(e))
        return 1


def _handle_llms(json_output: bool) -> int:
    """处理 doc llms 命令"""
    try:
        result = logic_get_llms_txt()
        has_error = _is_logic_error(result)
        if json_output:
            data = {"content": result}
            print_json(data)
        else:
            print(result)
        return 1 if has_error else 0
    except Exception as e:
        print_error(str(e))
        return 1


def _parse_api_index(markdown: str) -> list[dict[str, str]]:
    """解析 API 索引为 JSON 结构"""
    apis: list[dict[str, str]] = []
    for line in markdown.splitlines():
        if line.startswith("- **"):
            # 解析格式: - **name**: description
            name_end = line.find("**:")
            if name_end > 4:
                name = line[4:name_end]
                desc = line[name_end + 3:].strip()
                apis.append({"name": name, "description": desc})
    return apis
