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
3. SDK 会在首次迭代时自动建立连接
4. 如果没有使用 `async with` 管理生命周期，循环结束时会自动关闭连接

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

- 当处于 `async with client` 作用域时，`async for event in client` 不会提前关闭连接；连接会在退出 `async with` 时统一关闭
- 当处于 `async with client` 作用域时，若连接已断开，下一轮 `async for event in client` 会自动重建连接

### 并发迭代说明

- 同一个 `client` 可以被多个协程同时 `async for event in client`。
- 多个迭代器共享同一条连接（不会为每个迭代器各建一条连接）。
- 事件分发是“广播”语义：每个活跃迭代器都会收到一份事件，而不是由多个迭代器分摊消费。
- 若未使用 `async with`，连接会在最后一个并发迭代器结束后自动关闭。
- 若使用了 `async with`，即使所有并发迭代器都结束，也不会提前关闭连接；仍由 `async with` 退出时统一关闭。

## 常用属性

| 属性 | 说明 |
| --- | --- |
| `client.self_id` | 登录账号 ID（连接后自动获取） |
| `client.api` | 强类型 API 入口（`NapCatAPI`） |

## 适合人群

- 想要快速启动 Bot 的开发者
- 希望由应用主动控制连接、重连策略的场景
