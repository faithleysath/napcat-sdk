"""
tldr 命令

输出 CLI 常用命令速查。
"""

from __future__ import annotations

from textwrap import dedent


def cmd_tldr() -> int:
    """打印 CLI 快速使用说明。"""
    print(
        dedent(
            """
            NapCat CLI TL;DR

            1) Create / inspect config
              napcat-sdk config <NAME> --ws <URL>
              napcat-sdk config mybot --ws ws://127.0.0.1:3001 --token <TOKEN>
              napcat-sdk config mybot --ws ws://127.0.0.1:3001 --rpc-mode on --rpc-host 0.0.0.0 --rpc-port 8080
              napcat-sdk config mybot
              napcat-sdk config rm mybot

            2) Start / stop
              napcat-sdk start mybot
              napcat-sdk stop mybot
              napcat-sdk restart mybot

            3) Check status / logs
              napcat-sdk list
              napcat-sdk log mybot -f

            4) Call OneBot API (instance must be running)
              napcat-sdk call mybot get_login_info
              napcat-sdk call mybot send_private_msg '{"user_id":"123","message":"hi"}'

            5) Manage webhooks
              --event TYPE supports: message, notice, request, meta, *
              napcat-sdk webhook <NAME> rm [URL] [--event TYPE]...
              napcat-sdk webhook mybot add https://example.com/hook --event message
              napcat-sdk webhook mybot add https://example.com/hook --event meta
              napcat-sdk webhook mybot list
              napcat-sdk webhook mybot rm https://example.com/hook

            6) Browse SDK docs / MCP
              napcat-sdk doc apis
              napcat-sdk doc api send_private_msg
              napcat-sdk doc files
              napcat-sdk doc code client.py
              napcat-sdk doc class NapCatClient
              napcat-sdk doc agent --full
              napcat-sdk doc agent --full --with-code
              napcat-sdk mcp doc
            """
        ).strip()
    )
    return 0
