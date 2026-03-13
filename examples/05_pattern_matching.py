"""展示如何用结构化模式匹配编排 NapCat 事件逻辑。"""

from __future__ import annotations

import asyncio
import os
from collections.abc import Sequence

from napcat import (
    At,
    GroupMessageEvent,
    Image,
    MessageSender,
    NapCatClient,
    PrivateMessageEvent,
    Text,
)


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"缺少必填环境变量：{name}")
    return value


def optional_int_env(name: str) -> int | None:
    value = os.getenv(name)
    if value is None or value == "":
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise SystemExit(f"环境变量 {name} 必须是整数") from exc


def first_image_url(segments: Sequence[object]) -> str | None:
    for segment in segments:
        if isinstance(segment, Image) and segment.url:
            return segment.url
    return None


async def handle_event(
    event: GroupMessageEvent | PrivateMessageEvent,
    *,
    target_group_id: int | None,
) -> None:
    match event:
        case PrivateMessageEvent(sender=sender, message=[Text(text="/ping")]):
            print(f"[私聊] {sender.nickname} 触发了 /ping")
            await event.send_msg("pong")

        case GroupMessageEvent(
            group_id=gid,
            sender=MessageSender(role="admin" | "owner", nickname=nickname),
            message=[Text(text=command), At(qq=target_qq)],
        ) if target_group_id is not None and gid == target_group_id and command.strip() == "/ban":
            print(f"[群:{gid}] 管理员 {nickname} 请求处理用户 {target_qq}")
            await event.reply(f"收到指令，目标 QQ：{target_qq}", at=True)

        case GroupMessageEvent(
            group_id=gid,
            sender=MessageSender(role="admin", nickname=nickname),
            message=segments,
        ) if url := first_image_url(segments):
            print(f"[群:{gid}] 管理员 {nickname} 发送了图片：{url}")
            await event.reply("已记录管理员发送的图片", at=True)

        case GroupMessageEvent(
            group_id=gid,
            sender=sender,
            message=[Text(text=text)],
        ) if target_group_id is not None and gid == target_group_id and "笨蛋" in text:
            print(f"[群:{gid}] 关键词触发：{sender.nickname}")
            await event.reply("你才笨蛋！", at=True)

        case GroupMessageEvent(group_id=gid, sender=sender, raw_message=raw_message):
            print(f"[群:{gid}] {sender.nickname}: {raw_message}")

        case PrivateMessageEvent(sender=sender, raw_message=raw_message):
            print(f"[私聊] {sender.nickname}: {raw_message}")


async def main() -> None:
    client = NapCatClient(
        ws_url=require_env("NAPCAT_WS_URL"),
        token=os.getenv("NAPCAT_TOKEN"),
    )
    target_group_id = optional_int_env("NAPCAT_GROUP_ID")

    if target_group_id is None:
        print("未设置 NAPCAT_GROUP_ID，将只演示通用模式匹配，不启用目标群 guard。")
    else:
        print(f"已启用目标群 guard：group_id={target_group_id}")

    async for event in client:
        match event:
            case GroupMessageEvent() | PrivateMessageEvent():
                await handle_event(event, target_group_id=target_group_id)
            case _:
                continue


if __name__ == "__main__":
    asyncio.run(main())
