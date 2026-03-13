"""
NapCat CLI 模块

提供命令行工具的命令实现和 Gateway 守护进程管理。

命令:
  config    管理实例配置
  start     启动 Gateway 守护进程
  stop      停止 Gateway 守护进程
  restart   重启 Gateway 守护进程
  list      列出所有实例
  tldr      快速命令速查
  log       查看日志
  call      调用 OneBot API
  webhook   管理 Webhook
  doc       查询 SDK 文档
  mcp       MCP 相关命令
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from napcat import __version__

from .config import InstanceConfig
from .doc.registry import list_cli_operations
from .mcp.doc_server import main as run_doc_mcp_server

__all__ = ["InstanceConfig", "main", "build_parser"]

CLIHelpFormatter = argparse.RawDescriptionHelpFormatter


def _format_examples(*examples: str) -> str:
    """Format example commands for argparse epilog output."""
    if not examples:
        return ""
    return "Examples:\n" + "\n".join(f"  {example}" for example in examples)


def _build_config_rm_help_parser() -> argparse.ArgumentParser:
    """Build the dedicated help parser for `config rm`."""
    parser = argparse.ArgumentParser(
        prog="napcat-sdk config rm",
        description="Remove an instance configuration.",
        formatter_class=CLIHelpFormatter,
        epilog=_format_examples(
            "napcat-sdk config rm mybot",
        ),
    )
    parser.add_argument(
        "name",
        metavar="NAME",
        help="Instance name to remove (must be stopped first)",
    )
    return parser


def _build_mcp_help_parser() -> argparse.ArgumentParser:
    """Build the dedicated help parser for `mcp`."""
    parser = argparse.ArgumentParser(
        prog="napcat-sdk mcp",
        description=(
            "Run MCP-related commands for NapCat SDK.\n\n"
            "Use `doc` to start a stdio MCP server that exposes SDK docs, API definitions, and source lookups."
        ),
        formatter_class=CLIHelpFormatter,
        epilog=_format_examples(
            "napcat-sdk mcp doc",
        ),
    )
    _add_mcp_subcommands(parser)
    return parser


def _normalize_argv(argv: Sequence[str] | None) -> list[str]:
    """Normalize argv for parser preprocessing."""
    if argv is None:
        return list(sys.argv[1:])
    return list(argv)


def _should_print_config_rm_help(argv: Sequence[str]) -> bool:
    """Detect `napcat-sdk config rm --help` before the main parser runs."""
    return (
        len(argv) >= 3
        and argv[0] == "config"
        and argv[1] == "rm"
        and any(token in {"-h", "--help"} for token in argv[2:])
    )


def _add_doc_subcommands(doc_parser: argparse.ArgumentParser) -> None:
    doc_subparsers = doc_parser.add_subparsers(
        dest="doc_command",
        help="Documentation commands",
    )

    for spec in list_cli_operations():
        if spec.cli_name is None or spec.cli_help is None:
            continue

        subparser = doc_subparsers.add_parser(
            spec.cli_name,
            help=spec.cli_help,
            description=spec.cli_description or spec.cli_help,
            formatter_class=CLIHelpFormatter,
            epilog=_format_examples(*spec.cli_examples),
        )
        if spec.argument_spec is not None:
            subparser.add_argument(
                spec.argument_spec.name,
                nargs="+",
                metavar=spec.argument_spec.metavar,
                help=spec.argument_spec.description,
            )
        subparser.add_argument(
            "--json",
            action="store_true",
            help="Output in JSON format",
        )
        for flag in spec.cli_flags:
            subparser.add_argument(
                f"--{flag.name}",
                action="store_true",
                help=flag.help,
            )


def _add_mcp_subcommands(mcp_parser: argparse.ArgumentParser) -> None:
    """Add MCP subcommands to the provided parser."""
    mcp_subparsers = mcp_parser.add_subparsers(
        dest="mcp_command",
        metavar="{doc}",
        help="MCP commands",
    )
    mcp_subparsers.add_parser(
        "doc",
        help="Start NapCat docs MCP server (stdio)",
        description=(
            "Start the NapCat docs MCP server over stdio.\n\n"
            "The server exposes SDK documentation, API definitions, source indexes, and code lookups to MCP clients."
        ),
        formatter_class=CLIHelpFormatter,
        epilog=_format_examples(
            "napcat-sdk mcp doc",
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="napcat-sdk",
        description="NapCat SDK - CLI for managing QQ bot instances",
        formatter_class=CLIHelpFormatter,
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
        description="View, update, or remove instance configuration",
        usage="napcat-sdk config <NAME> [options]\n       napcat-sdk config rm <NAME>",
        formatter_class=CLIHelpFormatter,
        epilog=_format_examples(
            "napcat-sdk config mybot --ws ws://127.0.0.1:3001 --token <TOKEN>",
            "napcat-sdk config mybot",
            "napcat-sdk config rm mybot",
        ),
    )
    config_parser.add_argument(
        "name",
        nargs="?",
        metavar="NAME",
        help="Instance name to inspect or update",
    )
    config_parser.add_argument(
        "rm_name",
        nargs="?",
        metavar="NAME",
        help=argparse.SUPPRESS,
    )
    config_parser.add_argument("--ws", metavar="URL", help="NapCat WebSocket URL")
    config_parser.add_argument("--token", metavar="STR", help="Access token")
    config_parser.add_argument(
        "--rpc-mode",
        choices=["on", "off"],
        help="Enable or disable transparent RPC proxy",
    )
    config_parser.add_argument("--rpc-host", metavar="HOST", help="RPC listen host")
    config_parser.add_argument("--rpc-port", type=int, metavar="PORT", help="RPC listen port")
    config_parser.add_argument("--rpc-token", metavar="STR", help="RPC auth token")
    config_parser.add_argument(
        "--rpc-public-host",
        metavar="HOST",
        help="Public host advertised in serialized events",
    )

    # start 命令
    start_parser = subparsers.add_parser(
        "start",
        help="Start Gateway daemon",
        description="Start the Gateway daemon for an instance",
        formatter_class=CLIHelpFormatter,
        epilog=_format_examples(
            "napcat-sdk start mybot",
            "napcat-sdk start mybot --foreground",
            "napcat-sdk start mybot --ws ws://127.0.0.1:3001 --rpc-mode on --rpc-port 8080",
        ),
    )
    start_parser.add_argument("name", metavar="NAME", help="Instance name")
    start_parser.add_argument("--ws", metavar="URL", help="Update WebSocket URL before starting")
    start_parser.add_argument("--token", metavar="STR", help="Update token before starting")
    start_parser.add_argument(
        "--rpc-mode",
        choices=["on", "off"],
        help="Enable or disable transparent RPC proxy before starting",
    )
    start_parser.add_argument("--rpc-host", metavar="HOST", help="Update RPC listen host")
    start_parser.add_argument("--rpc-port", type=int, metavar="PORT", help="Update RPC listen port")
    start_parser.add_argument("--rpc-token", metavar="STR", help="Update RPC auth token")
    start_parser.add_argument(
        "--rpc-public-host",
        metavar="HOST",
        help="Update RPC public host advertised to remote consumers",
    )
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
        formatter_class=CLIHelpFormatter,
        epilog=_format_examples(
            "napcat-sdk stop mybot",
            "napcat-sdk stop mybot --force",
        ),
    )
    stop_parser.add_argument("name", metavar="NAME", help="Instance name")
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
        formatter_class=CLIHelpFormatter,
        epilog=_format_examples(
            "napcat-sdk restart mybot",
            "napcat-sdk restart mybot --foreground",
        ),
    )
    restart_parser.add_argument("name", metavar="NAME", help="Instance name")
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

    # tldr 命令
    subparsers.add_parser(
        "tldr",
        help="Show quick command cheatsheet",
        description="Show concise CLI usage examples",
    )

    # log 命令
    log_parser = subparsers.add_parser(
        "log",
        help="View Gateway logs",
        description="View or follow Gateway logs",
        formatter_class=CLIHelpFormatter,
        epilog=_format_examples(
            "napcat-sdk log mybot",
            "napcat-sdk log mybot --follow",
            "napcat-sdk log mybot --lines 200",
        ),
    )
    log_parser.add_argument("name", metavar="NAME", help="Instance name")
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
        description=(
            "Call a OneBot API through the running Gateway.\n\n"
            "Discover action names with `napcat-sdk doc apis` and inspect request/response"
            " schemas with `napcat-sdk doc api <ACTION>` before calling."
        ),
        formatter_class=CLIHelpFormatter,
        epilog=_format_examples(
            "napcat-sdk doc apis",
            "napcat-sdk doc api send_private_msg",
            "napcat-sdk call mybot get_login_info",
            "napcat-sdk call mybot send_private_msg '{\"user_id\":\"123\",\"message\":\"hi\"}'",
        ),
    )
    call_parser.add_argument("name", metavar="NAME", help="Instance name")
    call_parser.add_argument(
        "action",
        metavar="ACTION",
        help="API action name (e.g., get_login_info)",
    )
    call_parser.add_argument(
        "params",
        nargs="?",
        metavar="PARAMS",
        help="JSON parameters (optional; inspect expected fields with `napcat-sdk doc api <ACTION>`)",
    )

    # webhook 命令组
    webhook_parser = subparsers.add_parser(
        "webhook",
        help="Manage webhooks",
        description=(
            "Manage event webhooks for an instance.\n\n"
            "If the instance is running, commands operate on the live Gateway state.\n"
            "Otherwise they read or update the local config, and changes apply on the next start.\n\n"
            "Supported event filters: message, notice, request, meta, or * for all events."
        ),
        formatter_class=CLIHelpFormatter,
        epilog=_format_examples(
            "napcat-sdk webhook mybot add https://example.com/hook --event message",
            "napcat-sdk webhook mybot add https://example.com/hook --event meta",
            "napcat-sdk webhook mybot list --event message",
            "napcat-sdk webhook mybot rm https://example.com/hook",
        ),
    )
    webhook_parser.add_argument("name", metavar="NAME", help="Instance name")
    webhook_subparsers = webhook_parser.add_subparsers(
        dest="webhook_command",
        metavar="{add,list,rm}",
        help="Webhook operations",
        required=True,
    )

    webhook_add_parser = webhook_subparsers.add_parser(
        "add",
        help="Add a webhook",
        description=(
            "Add an event webhook.\n\n"
            "If the instance is running, the live Gateway is updated immediately.\n"
            "Otherwise the webhook is saved to the local config and applied on the next start.\n\n"
            "Supported event filters: message, notice, request, meta, or * for all events."
        ),
        formatter_class=CLIHelpFormatter,
        epilog=_format_examples(
            "napcat-sdk webhook mybot add https://example.com/hook",
            "napcat-sdk webhook mybot add https://example.com/hook --event message --event notice",
            "napcat-sdk webhook mybot add https://example.com/hook --event meta",
            "napcat-sdk webhook mybot add https://example.com/hook --secret supersecret",
        ),
    )
    webhook_add_parser.add_argument(
        "url",
        metavar="URL",
        help="Webhook URL",
    )
    webhook_add_parser.add_argument(
        "--event",
        action="append",
        dest="events",
        metavar="TYPE",
        help="Subscribe to event type (message/notice/request/meta/*; repeatable)",
    )
    webhook_add_parser.add_argument(
        "--secret",
        metavar="STR",
        help="HMAC secret for webhook signature",
    )

    webhook_list_parser = webhook_subparsers.add_parser(
        "list",
        help="List webhooks",
        description=(
            "List current webhooks.\n\n"
            "If the instance is running, the list comes from the live Gateway.\n"
            "Otherwise the list comes from the local config.\n\n"
            "Supported event filters: message, notice, request, meta, or * for all events."
        ),
        formatter_class=CLIHelpFormatter,
        epilog=_format_examples(
            "napcat-sdk webhook mybot list",
            "napcat-sdk webhook mybot list https://example.com/hook",
            "napcat-sdk webhook mybot list --event meta",
            "napcat-sdk webhook mybot list --event message",
        ),
    )
    webhook_list_parser.add_argument(
        "url",
        nargs="?",
        metavar="URL",
        help="Optional webhook URL filter",
    )
    webhook_list_parser.add_argument(
        "--event",
        action="append",
        dest="events",
        metavar="TYPE",
        help="Filter by event type (message/notice/request/meta/*; repeatable)",
    )

    webhook_rm_parser = webhook_subparsers.add_parser(
        "rm",
        aliases=["remove"],
        help="Remove matching webhooks",
        description=(
            "Remove matching webhooks.\n\n"
            "If the instance is running, matching rules are removed from the live Gateway.\n"
            "Otherwise matching rules are removed from the local config and the change applies on the next start.\n\n"
            "Supported event filters: message, notice, request, meta, or * for all events."
        ),
        formatter_class=CLIHelpFormatter,
        epilog=_format_examples(
            "napcat-sdk webhook mybot rm",
            "napcat-sdk webhook mybot rm https://example.com/hook",
            "napcat-sdk webhook mybot rm --event meta",
            "napcat-sdk webhook mybot rm https://example.com/hook --event notice",
        ),
    )
    webhook_rm_parser.add_argument(
        "url",
        nargs="?",
        metavar="URL",
        help="Optional webhook URL filter",
    )
    webhook_rm_parser.add_argument(
        "--event",
        action="append",
        dest="events",
        metavar="TYPE",
        help="Filter by event type before removing (message/notice/request/meta/*; repeatable)",
    )

    # mcp 命令组
    mcp_parser = subparsers.add_parser(
        "mcp",
        help="MCP related commands",
        description=(
            "Run MCP-related commands for NapCat SDK.\n\n"
            "Use `doc` to start a stdio MCP server that exposes SDK docs, API definitions, and source lookups."
        ),
        formatter_class=CLIHelpFormatter,
        epilog=_format_examples(
            "napcat-sdk mcp doc",
        ),
    )
    _add_mcp_subcommands(mcp_parser)

    # doc 命令组
    doc_parser = subparsers.add_parser(
        "doc",
        help="Query SDK documentation",
        description="Query API definitions, source code, and documentation",
        formatter_class=CLIHelpFormatter,
        epilog=_format_examples(
            "napcat-sdk doc apis",
            "napcat-sdk doc api send_private_msg",
            "napcat-sdk doc code client.py --json",
            "napcat-sdk doc class NapCatClient",
            "napcat-sdk doc agent --full",
        ),
    )
    _add_doc_subcommands(doc_parser)

    return parser


def _parse_rpc_mode_arg(value: str | None) -> bool | None:
    """解析命令行的 rpc-mode 参数。"""
    if value is None:
        return None
    return value == "on"


def main(argv: Sequence[str] | None = None) -> int:
    raw_argv = _normalize_argv(argv)
    parser = build_parser()
    if _should_print_config_rm_help(raw_argv):
        _build_config_rm_help_parser().print_help()
        return 0

    args = parser.parse_args(raw_argv)

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
        cmd_tldr,
        cmd_webhook,
    )

    match args.command:
        case "config":
            if args.name is None:
                parser.error("the following arguments are required: name")
                return 2

            if args.name == "rm":
                if args.rm_name is None:
                    parser.error("usage: napcat-sdk config rm <NAME>")
                    return 2

                has_update_options = any(
                    value is not None
                    for value in (
                        args.ws,
                        args.token,
                        args.rpc_mode,
                        args.rpc_host,
                        args.rpc_port,
                        args.rpc_token,
                        args.rpc_public_host,
                    )
                )
                if has_update_options:
                    parser.error("'config rm' does not accept update options")
                    return 2

                return cmd_config(
                    instance_name=args.rm_name,
                    remove=True,
                )

            if args.rm_name is not None:
                parser.error(f"unrecognized arguments: {args.rm_name}")
                return 2

            return cmd_config(
                instance_name=args.name,
                ws_url=args.ws,
                token=args.token,
                rpc_mode=_parse_rpc_mode_arg(args.rpc_mode),
                rpc_host=args.rpc_host,
                rpc_port=args.rpc_port,
                rpc_token=args.rpc_token,
                rpc_public_host=args.rpc_public_host,
            )

        case "start":
            return cmd_start(
                instance_name=args.name,
                ws_url=args.ws,
                token=args.token,
                rpc_mode=_parse_rpc_mode_arg(args.rpc_mode),
                rpc_host=args.rpc_host,
                rpc_port=args.rpc_port,
                rpc_token=args.rpc_token,
                rpc_public_host=args.rpc_public_host,
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

        case "tldr":
            return cmd_tldr()

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
                subcommand=args.webhook_command,
                url=getattr(args, "url", None),
                events=getattr(args, "events", None),
                secret=getattr(args, "secret", None),
            )

        case "doc":
            return cmd_doc(
                doc_command=args.doc_command,
                json_output=getattr(args, 'json', False),
                names=getattr(args, 'names', None),
                paths=getattr(args, 'paths', None),
                full=getattr(args, 'full', False),
                with_code=getattr(args, 'with_code', False),
            )

        case "mcp":
            if args.mcp_command == "doc":
                run_doc_mcp_server()
                return 0
            _build_mcp_help_parser().print_help()
            return 0

        case _:
            parser.error(f"Unknown command: {args.command}")
            return 2


if __name__ == "__main__":
    raise SystemExit(main())
