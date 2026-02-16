"""
CLI 工具函数

提供命令行工具使用的通用工具函数。
"""

from __future__ import annotations

import json
import sys
from typing import Any


def print_error(message: str) -> None:
    """打印错误消息到 stderr"""
    print(f"\033[31mError:\033[0m {message}", file=sys.stderr)


def print_success(message: str) -> None:
    """打印成功消息"""
    print(f"\033[32m✓\033[0m {message}")


def print_warning(message: str) -> None:
    """打印警告消息"""
    print(f"\033[33mWarning:\033[0m {message}")


def print_json(data: Any, indent: int = 2) -> None:
    """格式化打印 JSON"""
    print(json.dumps(data, indent=indent, ensure_ascii=False))


def format_status(running: bool) -> str:
    """格式化运行状态"""
    if running:
        return "\033[32mRunning\033[0m"
    return "\033[90mStopped\033[0m"


def truncate(s: str, max_len: int = 30) -> str:
    """截断字符串"""
    if len(s) <= max_len:
        return s
    return s[: max_len - 3] + "..."
