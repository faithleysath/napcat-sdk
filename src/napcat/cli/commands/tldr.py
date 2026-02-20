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

            1) Configure an instance
              napcat-sdk config <NAME> --ws <URL> [--token <TOKEN>]
              napcat-sdk config <NAME> --rpc-mode on --rpc-host 0.0.0.0 --rpc-port 8080
              napcat-sdk config rm <NAME>

            2) Start / stop
              napcat-sdk start <NAME>
              napcat-sdk stop <NAME>
              napcat-sdk restart <NAME>

            3) Check status / logs
              napcat-sdk list
              napcat-sdk log <NAME> -f

            4) Call OneBot API
              napcat-sdk call <NAME> get_login_info
              napcat-sdk call <NAME> send_private_msg '{"user_id":123,"message":"hi"}'

            5) Manage webhooks (filter mode)
              napcat-sdk webhook <NAME> add <URL> --event message
              napcat-sdk webhook <NAME> list [URL] [--event TYPE]...
              napcat-sdk webhook <NAME> rm [URL] [--event TYPE]...

            6) Docs / MCP
              napcat-sdk doc apis
              napcat-sdk doc api send_private_msg
              napcat-sdk mcp doc
            """
        ).strip()
    )
    return 0
