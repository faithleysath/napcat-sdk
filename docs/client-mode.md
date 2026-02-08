---
icon: lucide/plug
---

# Client 模式（主动连接）

Client 模式适用于 **你的应用主动连接 NapCat** 的场景。

## 典型场景

- 你在本地或服务器上运行一个 Bot
- NapCat 已暴露 WebSocket 地址与 Token

## 连接流程

1. 使用 `NapCatClient` 创建实例
2. 通过 `async for event in client:` 开启事件循环
3. SDK 会在首次迭代时自动建立连接并在循环结束时自动关闭连接

```python
from napcat import NapCatClient

client = NapCatClient(ws_url="ws://localhost:3001", token="your-token")

async for event in client:
    ...
```

## 生命周期管理

- `NapCatClient` 实现了异步上下文管理器
- 也可以手动管理连接：

```python
async with NapCatClient(ws_url="ws://localhost:3001") as client:
    async for event in client:
        ...
```

## 常用属性

| 属性 | 说明 |
| --- | --- |
| `client.self_id` | 登录账号 ID（连接后自动获取） |
| `client.api` | 强类型 API 入口（`NapCatAPI`） |

## 适合人群

- 想要快速启动 Bot 的开发者
- 希望由应用主动控制连接、重连策略的场景
