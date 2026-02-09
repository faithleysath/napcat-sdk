---
icon: lucide/bot
---

# 第一个机器人

现在，我们将创建一个最简单的机器人。它的功能非常纯粹：**连接到 NapCat，并打印收到的所有事件**。

这能帮助你确认网络连接是否正常。

## 配置 NapCat

NapCat-SDK 支持两种连接模式。为了快速开始，我们推荐使用 **Client 模式**（即 SDK 主动连接到 NapCat）。

请确保你的 NapCat 配置文件（`napcat.json`）中开启了正向 WebSocket 服务：

```json
{
  "network": {
    "websocketClients": [],
    "websocketServers": [
      {
        "enable": true,
        "host": "0.0.0.0",
        "port": 3000, 
        "token": "your_token" 
      }
    ]
  }
}
```

## 编写代码

新建一个文件 `bot.py`，写入以下内容：

```python
import asyncio
from napcat import NapCatClient

# 1. 配置连接信息
# 替换为你 NapCat 的实际地址和 Token
client = NapCatClient(
    ws_url="ws://127.0.0.1:3000",
    token="your_token"
)

async def main():
    print("正在连接到 NapCat...")
    
    # 2. 建立连接并监听事件
    # async with 会自动处理连接和断开
    async with client:
        print(f"连接成功！当前登录账号: {client.self_id}")
        
        # 3. 循环接收事件
        async for event in client:
            print(f"收到事件: {event}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 运行

在终端运行：

```bash
python bot.py
```

如果你看到 **“连接成功！当前登录账号: 123456...”**，并且当你向机器人发送消息时终端有日志滚动，那么恭喜你！你已经成功迈出了第一步。


## 下一步

现在的机器人只是个“复读机”，只会把事件打印到屏幕上。接下来，我们教它如何**读懂消息**并**回复**。

👉 **前往：[实现交互](./interaction.md)**

