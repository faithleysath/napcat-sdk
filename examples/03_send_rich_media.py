from __future__ import annotations

import asyncio
import os

from napcat import At, Image, Message, NapCatClient, Text


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"缺少必填环境变量：{name}")
    return value


async def main() -> None:
    client = NapCatClient(
        ws_url=require_env("NAPCAT_WS_URL"),
        token=os.getenv("NAPCAT_TOKEN"),
    )
    group_id = require_env("NAPCAT_GROUP_ID")

    message: list[Message] = [
        At(qq="12345678"),
        Text(text=" 来看这张图"),
        Image(file="https://example.com/image.jpg"),
    ]

    async with client:
        result = await client.send_group_msg(group_id=group_id, message=message)

    print(f"群消息发送成功：message_id={result['message_id']}")


if __name__ == "__main__":
    asyncio.run(main())
