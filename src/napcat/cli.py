"""
命令行接口模块

提供 napcat-sdk 的命令行工具入口。
目前支持查看版本、启动 MCP 文档服务器等功能。
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from . import __version__
from .mcp.doc_server import main as run_doc_mcp_server


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="napcat-sdk",
        description="NapCat SDK command line interface",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"napcat-sdk {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("help", help="Show help message")
    subparsers.add_parser("version", help="Show napcat-sdk version")

    mcp_parser = subparsers.add_parser("mcp", help="MCP related commands")
    mcp_subparsers = mcp_parser.add_subparsers(dest="mcp_command")
    mcp_subparsers.add_parser("doc", help="Start NapCat docs MCP server (stdio)")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command in (None, "help"):
        parser.print_help()
        return 0

    if args.command == "version":
        print(f"napcat-sdk {__version__}")
        return 0

    if args.command == "mcp":
        if args.mcp_command == "doc":
            run_doc_mcp_server()
            return 0

        parser.parse_args(["mcp", "--help"])
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
