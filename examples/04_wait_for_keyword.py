from __future__ import annotations

import asyncio
import os

from napcat import GroupMessageEvent, NapCatClient
from napcat.matcher import event_match


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
    group_id = int(require_env("NAPCAT_GROUP_ID"))

    print("正在等待目标群里的 /hello，最长 60 秒...")

    try:
        async with client:
            event = await client.wait_event(
                event_match(
                    GroupMessageEvent,
                    group_id=group_id,
                    raw_message=lambda value: value.strip() == "/hello",
                ),
                timeout=60.0,
            )
            match event:
                case GroupMessageEvent(message_id=message_id, user_id=user_id):
                    print(f"已匹配到消息：message_id={message_id} user_id={user_id}")
                    await event.reply("world", at=True)
                case _:
                    raise RuntimeError("wait_event 返回了意料之外的事件类型")
    except TimeoutError:
        print("等待超时，未收到匹配的群消息")



if __name__ == "__main__":
    asyncio.run(main())
