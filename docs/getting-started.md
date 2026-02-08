---
icon: lucide/play
---

# 快速开始

本节带你从零搭建一个可运行的 NapCat 机器人。

## 安装

推荐使用 `uv`，也可以直接 `pip`：

```bash
uv add napcat-sdk
# or
pip install napcat-sdk
```

## 前置条件

- Python 3.12+（项目使用严格类型检查）
- 已启动的 NapCat 服务端
- 获取到 WebSocket 地址与 Token（如需要鉴权）

## 你的第一个 Bot（Client 模式）

```python
import asyncio
from napcat import NapCatClient, PrivateMessageEvent

async def main():
    async for event in NapCatClient(ws_url="ws://localhost:3001", token="token"):
        match event:
            case PrivateMessageEvent():
                await event.send_msg("收到你的私聊消息")
            case _:
                pass

if __name__ == "__main__":
    asyncio.run(main())
```

### 运行效果

- 连接成功后，SDK 会自动拉取登录信息并填充 `client.self_id`。
- 事件流以异步迭代器的方式提供，适合直接在循环中处理。

## 下一步推荐

- 了解 **[事件与消息](events-messages.md)**，掌握消息段与回复技巧。
- 如果你的 NapCat 需要反向连接，请查看 **[Server 模式](server-mode.md)**。
