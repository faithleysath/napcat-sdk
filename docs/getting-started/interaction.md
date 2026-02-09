---
icon: lucide/message-square
---

# 实现交互

在这一章，我们将实现一个经典的 **Echo Bot**： 当用户发送群消息 **“你好”** 时，机器人回复 **“你好呀！[握手表情]”**。

这涉及到两个核心操作：**判断事件类型** 和 **调用 API**。

## 完善代码

修改你的 `bot.py`，引入必要的事件类型和消息段：

```python
import asyncio
from napcat import NapCatClient, GroupMessageEvent, Text, Face

client = NapCatClient(
    ws_url="ws://127.0.0.1:3000",
    token="your_token"
)

async def main():
    async with client:
        print(f"Bot {client.self_id} 已启动")
        
        async for event in client:
            # 1. 判断是否为群消息
            # 使用 isinstance 获得类型安全，IDE 会自动提示 event 下的属性
            if isinstance(event, GroupMessageEvent):
                
                # 2. 判断消息内容
                # event.raw_message 是消息的纯文本形式
                if event.raw_message == "你好":
                    print(f"收到群 {event.group_id} 的问候")
                    
                    # 3. 发送回复
                    # 我们可以像搭积木一样混合使用 文本(Text) 和 表情(Face)
                    await event.reply([
                        Text(text="你好呀！"),
                        Face(id="54")  # QQ 默认表情 ID
                    ])

if __name__ == "__main__":
    asyncio.run(main())
```

## 关键点解析

1. **`isinstance(event, GroupMessageEvent)`**: 这是 SDK 的核心哲学。通过类型检查，IDE 能准确地告诉你 `event` 里包含 `group_id` 而不是 `user_id`，避免了 `KeyError` 的发生。
2. **`event.raw_message`**: 这是一个方便的属性，它提取了消息中的所有文本部分。如果你只想做简单的关键词匹配，用它就够了。
3. **`event.reply(...)`**: 这是一个快捷方法。你不需要手动调用 `client.send_group_msg` 并填入群号，SDK 已经帮你自动绑定了上下文。

---

## 🎉 旅程继续

恭喜！你已经掌握了 NapCat-SDK 的基础用法。

现在的你，可能想深入了解：

- **Server 模式**：如果你需要反向 WebSocket 连接。
- **复杂消息**：如何处理图片、语音、回复引用？
- **事件细节**：还有哪些事件可以监听？

请前往核心概念章节，探索更多高级特性。

👉 **前往：[核心概念 - Client 模式](../key-concept/client.md)**