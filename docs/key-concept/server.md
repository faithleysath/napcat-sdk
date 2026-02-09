---
icon: lucide/server
---

# 反向WebSocket服务器

`ReverseWebSocketServer` 实现了 **Server 模式（反向连接）**。

在这种模式下，你的程序不再主动出击，而是作为一个服务端监听端口，等待 NapCat 主动发起连接。这在 Docker 部署或公网回调场景中非常常见。

## 1. 快速开始

使用 `ReverseWebSocketServer` 非常简单，你只需要定义一个 **Handler（回调函数）**，告诉服务器“当有 Bot 连上来时该做什么”。

```python
import asyncio
from napcat import ReverseWebSocketServer, NapCatClient, GroupMessageEvent

# 核心逻辑：定义每个连接的处理方式
async def on_bot_connect(client: NapCatClient):
    print(f"Bot 已连接, QQ号: {client.self_id}")

    # 像平时一样迭代事件
    async for event in client:
        if isinstance(event, GroupMessageEvent):
            print(f"收到群 {event.group_id} 消息: {event.message}")
            await event.reply("收到！")

    print("Bot 连接已断开")

# 启动服务器
if __name__ == "__main__":
    server = ReverseWebSocketServer(
        handler=on_bot_connect,
        host="0.0.0.0",
        port=8080,
        token="your_token", # 可选：鉴权 Token
    )
    asyncio.run(server.run_forever())
```

## 2. 核心概念：控制反转

与 `NapCatClient` 主动连接不同，Server 模式遵循**“好莱坞原则”**（Don't call us, we'll call you）。

### 预热的 Client 对象

在你的 `handler` 被调用时，传入的 `client` 参数是一个**已经建立好连接**、**完成鉴权**且**处于活跃状态**的对象。

这意味着：

1. **无需手动连接**：你不需要（也不能）在 handler 里再写 `async with client:`。
2. **开箱即用**：你可以直接调用 `await client.send_private_msg(...)`。
3. **生命周期绑定**：当 `handler` 函数执行结束（或抛出异常）时，Server 会认为该次会话结束，并自动关闭底层的 WebSocket 连接。

### 断线与重连

在 Server 模式下，**重连的控制权在 NapCat 端**。

- **断线时**：`async for event in client` 循环会结束，你的 `handler` 也会随之退出。
- **重连时**：NapCat 发起新的连接，`ReverseWebSocketServer` 会**重新调用**你的 `handler`，并传入一个新的 `client` 实例。

> **⚠️ 常见误区** 请**不要**在 handler 内部包裹 `while True` 来试图保活。 如果连接断开，你应该让 handler 自然退出，等待下一次连接。强行死循环会导致你在一个已断开的连接上空转，引发错误刷屏。

```python
# ❌ 错误写法：试图在断开后手动重连（无效且危险）
async def handler(client):
    while True: # 不要写这个！
        try:
            async for event in client: ...
        except:
            pass 

# ✅ 正确写法：顺其自然
async def handler(client):
    async for event in client:
        ...
    # 循环结束意味着连接断开，直接退出函数即可
```

## 3. 生命周期管理

`ReverseWebSocketServer` 提供了灵活的启动方式，既可以长期运行，也可以嵌入到现有的异步流程中。

### 方式一：run_forever (推荐)

适用于作为独立进程运行的场景。

```python
server = ReverseWebSocketServer(handler, port=8080)
try:
    await server.run_forever()
except KeyboardInterrupt:
    server.stop() # 优雅停止
```

### 方式二：异步上下文管理器

适用于需要与其他服务（如 Web Server）共存，或进行测试的场景。

```python
async with ReverseWebSocketServer(handler, port=8080) as server:
    # 服务器已在后台启动
    print("Server started")
    
    # 你的其他业务逻辑...
    await asyncio.sleep(3600)

# 离开上下文时，服务器会自动停止并断开所有连接
```

### 优雅关闭

当你调用 `server.stop()` 或退出 `async with` 时，服务器会：

1. 停止接收新的连接。
2. 取消所有正在运行的 `handler` 任务。
3. 等待 `shutdown_timeout` (默认 5秒)，让 handler 有机会完成最后的清理工作。

## 4. API 参考

```python
class ReverseWebSocketServer:
    def __init__(
        self,
        handler: Callable[[NapCatClient], Awaitable[None]],
        host: str = "0.0.0.0",
        port: int = 8080,
        token: str | None = None,
        shutdown_timeout: float = 5.0,
    ): ...
```

- **handler**: 必填。处理连接的核心回调函数。
- **host / port**: 监听地址。`0.0.0.0` 表示允许所有 IP 连接。
- **token**: 可选。如果设置，Server 会检查请求头 `Authorization: Bearer <token>`，不匹配则直接拒绝连接（HTTP 4001）。
- **shutdown_timeout**: 停止服务时，等待活跃连接关闭的最长时间。
