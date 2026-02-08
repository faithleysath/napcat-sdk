---
icon: lucide/server
---

# Server 模式（反向连接）

Server 模式适用于 **NapCat 主动连接你的应用** 的场景。

## 典型场景

- 你的程序部署在公网或内网，NapCat 需要反向连接
- 你希望同时接入多个 Bot 实例

## 示例：启动反向 WebSocket 服务

```python
import asyncio
from napcat import ReverseWebSocketServer, NapCatClient, GroupMessageEvent

async def handler(client: NapCatClient):
    async for event in client:
        if isinstance(event, GroupMessageEvent):
            await event.reply("Server 模式已收到消息")

async def main():
    server = ReverseWebSocketServer(
        handler,
        host="0.0.0.0",
        port=8080,
        token="your-token",
    )
    await server.run_forever()

if __name__ == "__main__":
    asyncio.run(main())
```

## 鉴权说明

- SDK 会读取请求头中的 `Authorization: Bearer <token>`
- 若 Token 不匹配，连接将被拒绝

## 多连接处理

每当有新的 WebSocket 连接，`handler` 就会获得一个独立的 `NapCatClient`，你可以：

- 启动独立协程处理事件
- 在 handler 中区分 `client.self_id`
- 按需维护连接池或状态
