from __future__ import annotations

import asyncio
import os

from napcat import GroupMessageEvent, NapCatClient, ReverseWebSocketServer, Text


def parse_port(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise SystemExit(f"环境变量 {name} 必须是整数") from exc


async def handler(client: NapCatClient) -> None:
    print(f"Bot 已连接：self_id={client.self_id}")

    async for event in client:
        match event:
            case GroupMessageEvent(
                group_id=gid,
                sender=sender,
                message=[Text(text="/ping")],
            ):
                print(f"[群:{gid}] {sender.nickname}: /ping")
                await event.reply("来自反向服务端的 pong", at=True)
            case GroupMessageEvent(group_id=gid, sender=sender, raw_message=raw_message):
                print(f"[群:{gid}] {sender.nickname}: {raw_message}")
            case _:
                continue


async def main() -> None:
    server = ReverseWebSocketServer(
        handler,
        host=os.getenv("NAPCAT_SERVER_HOST", "0.0.0.0"),
        port=parse_port("NAPCAT_SERVER_PORT", 8080),
        token=os.getenv("NAPCAT_TOKEN"),
    )
    await server.run_forever()


if __name__ == "__main__":
    asyncio.run(main())
