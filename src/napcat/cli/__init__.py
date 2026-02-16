"""
NapCat CLI 模块

提供命令行工具的命令实现和 Gateway 守护进程管理。

命令:
  config    管理实例配置
  start     启动 Gateway 守护进程
  stop      停止 Gateway 守护进程
  restart   重启 Gateway 守护进程
  list      列出所有实例
  log       查看日志
  call      调用 OneBot API
  webhook   管理 Webhook
  doc       查询 SDK 文档
  mcp       MCP 相关命令
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from napcat import __version__

from .config import InstanceConfig
from .mcp.doc_server import main as run_doc_mcp_server

__all__ = ["InstanceConfig", "main", "build_parser"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="napcat-sdk",
        description="NapCat SDK - CLI for managing QQ bot instances",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  napcat-sdk config mybot --ws ws://127.0.0.1:3001 --token mytoken
  napcat-sdk start mybot
  napcat-sdk list
  napcat-sdk call mybot get_login_info
  napcat-sdk stop mybot

For more information, visit: https://github.com/faithleysath/napcat-sdk
""",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"napcat-sdk {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # config 命令
    config_parser = subparsers.add_parser(
        "config",
        help="Manage instance configuration",
        description="View or update instance configuration",
    )
    config_parser.add_argument("name", help="Instance name")
    config_parser.add_argument("--ws", metavar="URL", help="NapCat WebSocket URL")
    config_parser.add_argument("--token", metavar="STR", help="Access token")

    # start 命令
    start_parser = subparsers.add_parser(
        "start",
        help="Start Gateway daemon",
        description="Start the Gateway daemon for an instance",
    )
    start_parser.add_argument("name", help="Instance name")
    start_parser.add_argument("--ws", metavar="URL", help="Update WebSocket URL before starting")
    start_parser.add_argument("--token", metavar="STR", help="Update token before starting")
    start_parser.add_argument(
        "-f", "--foreground",
        action="store_true",
        help="Run in foreground (not as daemon)",
    )

    # stop 命令
    stop_parser = subparsers.add_parser(
        "stop",
        help="Stop Gateway daemon",
        description="Stop the Gateway daemon",
    )
    stop_parser.add_argument("name", help="Instance name")
    stop_parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Force kill (SIGKILL)",
    )

    # restart 命令
    restart_parser = subparsers.add_parser(
        "restart",
        help="Restart Gateway daemon",
        description="Restart the Gateway daemon",
    )
    restart_parser.add_argument("name", help="Instance name")
    restart_parser.add_argument(
        "-f", "--foreground",
        action="store_true",
        help="Run in foreground after restart",
    )

    # list 命令
    subparsers.add_parser(
        "list",
        aliases=["ls"],
        help="List all instances",
        description="List all instances and their status",
    )

    # log 命令
    log_parser = subparsers.add_parser(
        "log",
        help="View Gateway logs",
        description="View or follow Gateway logs",
    )
    log_parser.add_argument("name", help="Instance name")
    log_parser.add_argument(
        "-f", "--follow",
        action="store_true",
        help="Follow log output (tail -f)",
    )
    log_parser.add_argument(
        "-n", "--lines",
        type=int,
        default=50,
        metavar="NUM",
        help="Number of lines to show (default: 50)",
    )

    # call 命令
    call_parser = subparsers.add_parser(
        "call",
        help="Call OneBot API",
        description="Call a OneBot API through the running Gateway",
    )
    call_parser.add_argument("name", help="Instance name")
    call_parser.add_argument("action", help="API action name (e.g., get_login_info)")
    call_parser.add_argument(
        "params",
        nargs="?",
        help="JSON parameters (optional)",
    )

    # webhook 命令组
    webhook_parser = subparsers.add_parser(
        "webhook",
        help="Manage webhooks",
        description="Manage event webhooks for an instance",
    )
    webhook_parser.add_argument("name", help="Instance name")
    webhook_parser.add_argument(
        "subcommand",
        choices=["add", "list", "rm"],
        help="Subcommand: add, list, rm",
    )
    webhook_parser.add_argument(
        "url",
        nargs="?",
        help="Webhook URL (for add/rm)",
    )
    webhook_parser.add_argument(
        "--event",
        action="append",
        dest="events",
        metavar="TYPE",
        help="Event type filter (can specify multiple)",
    )
    webhook_parser.add_argument(
        "--secret",
        metavar="STR",
        help="HMAC secret for webhook signature",
    )
    webhook_parser.add_argument(
        "--index",
        type=int,
        metavar="NUM",
        help="Webhook index to remove (alternative to URL)",
    )

    # mcp 命令组
    mcp_parser = subparsers.add_parser("mcp", help="MCP related commands")
    mcp_subparsers = mcp_parser.add_subparsers(dest="mcp_command")
    mcp_subparsers.add_parser("doc", help="Start NapCat docs MCP server (stdio)")

    # doc 命令组
    doc_parser = subparsers.add_parser(
        "doc",
        help="Query SDK documentation",
        description="Query API definitions, source code, and documentation",
    )
    doc_subparsers = doc_parser.add_subparsers(dest="doc_command", help="Documentation commands")

    # doc apis
    doc_subparsers.add_parser(
        "apis",
        help="List all available APIs",
        description="List all NapCat SDK API methods",
    ).add_argument("--json", action="store_true", help="Output in JSON format")

    # doc api
    api_parser = doc_subparsers.add_parser(
        "api",
        help="Get API details",
        description="Get detailed information about one or more APIs",
    )
    api_parser.add_argument("names", nargs="+", help="API name(s) to query")
    api_parser.add_argument("--json", action="store_true", help="Output in JSON format")

    # doc files
    doc_subparsers.add_parser(
        "files",
        help="List source code files",
        description="List the source code directory structure",
    ).add_argument("--json", action="store_true", help="Output in JSON format")

    # doc code
    code_parser = doc_subparsers.add_parser(
        "code",
        help="View source code",
        description="View the content of source code files",
    )
    code_parser.add_argument("paths", nargs="+", help="File path(s) to view")
    code_parser.add_argument("--json", action="store_true", help="Output in JSON format")

    # doc class
    class_parser = doc_subparsers.add_parser(
        "class",
        help="View class definition",
        description="View class definitions by name",
    )
    class_parser.add_argument("names", nargs="+", help="Class name(s) to query")
    class_parser.add_argument("--json", action="store_true", help="Output in JSON format")

    # doc llms
    doc_subparsers.add_parser(
        "llms",
        help="View llms.txt documentation",
        description="View the llms.txt file with SDK design philosophy and best practices",
    ).add_argument("--json", action="store_true", help="Output in JSON format")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # 无命令或 help
    if args.command is None:
        parser.print_help()
        return 0

    # 导入命令模块 (延迟导入避免循环依赖)
    from .commands import (
        cmd_call,
        cmd_config,
        cmd_doc,
        cmd_list,
        cmd_log,
        cmd_restart,
        cmd_start,
        cmd_stop,
        cmd_webhook,
    )

    match args.command:
        case "config":
            return cmd_config(
                instance_name=args.name,
                ws_url=args.ws,
                token=args.token,
            )

        case "start":
            return cmd_start(
                instance_name=args.name,
                ws_url=args.ws,
                token=args.token,
                foreground=args.foreground,
            )

        case "stop":
            return cmd_stop(
                instance_name=args.name,
                force=args.force,
            )

        case "restart":
            return cmd_restart(
                instance_name=args.name,
                foreground=args.foreground,
            )

        case "list" | "ls":
            return cmd_list()

        case "log":
            return cmd_log(
                instance_name=args.name,
                follow=args.follow,
                lines=args.lines,
            )

        case "call":
            return cmd_call(
                instance_name=args.name,
                action=args.action,
                params_json=args.params,
            )

        case "webhook":
            return cmd_webhook(
                instance_name=args.name,
                subcommand=args.subcommand,
                url=args.url,
                events=args.events,
                secret=args.secret,
                index=args.index,
            )

        case "doc":
            return cmd_doc(
                doc_command=args.doc_command,
                json_output=getattr(args, 'json', False),
                names=getattr(args, 'names', None),
                paths=getattr(args, 'paths', None),
            )

        case "mcp":
            if args.mcp_command == "doc":
                run_doc_mcp_server()
                return 0
            parser.parse_args(["mcp", "--help"])
            return 0

        case _:
            parser.error(f"Unknown command: {args.command}")
            return 2


if __name__ == "__main__":
    raise SystemExit(main())
