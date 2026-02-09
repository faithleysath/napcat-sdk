首先用 `uv add napcat-sdk` 或 `pip install napcat-sdk` 安装 napcat-sdk 包。

接下来可以从 napcat 模块中导入所有需要用到的类和函数：

```python
from napcat import ...
```

# 核心概念

## NapCatClient

这是与 NapCat 建立websocket连接的核心类，它提供了发送消息、接收消息、管理连接等功能。

```python
class NapCatClient:
    def __init__(
        self,
        ws_url: str | None = None,
        token: str | None = None,
        _existing_conn: Connection | None = None,
    ):
```

实例化 NapCatClient 主要有两种方式，一种是直接传入 websocket URL 和 token，另一种是传入一个已经存在的 Connection 对象。后者是用于反向ws服务端的场景。

```python
# 创建 NapCatClient 实例
client = NapCatClient(ws_url="ws://example.com/ws", token="your_token")
```

### 连接管理

接下来讲解使用**第一种方式**实例化 NapCatClient 后其生命周期的管理。

实例化后，NapCatClient 并不会立即创建连接，此时client本质上只是一个连接配置对象，内部保存了url和token等信息。可以通过client.is_running属性来检查连接是否已经建立。

NapCatClient 实现了异步上下文管理器协议，因此可以使用 async with 语句来自动管理连接的生命周期：

```python
client = NapCatClient(ws_url="ws://xxx", token="your_token")

async with client:
    assert client.is_running  # True
    ...

assert not client.is_running  # True，连接已经关闭
```

当然，你也可以使用更简洁的写法：

```python
async with NapCatClient(ws_url="ws://xxx", token="your_token") as client:
    assert client.is_running  # True
    ...
```

如果是使用**第一种方式**实例化的 NapCatClient，在 async with 块结束后，你仍旧可以再次使用 async with 来重新建立连接，因为 NapCatClient 本质上就是一个记录了连接配置的智能对象，它会在每次进入 async with 块时根据保存的配置来创建连接。

### 接收事件

NapCatClient 实现了异步迭代器协议，因此可以使用 async for 语句来接收事件：

```python
async with NapCatClient(ws_url="ws://xxx", token="your_token") as client:
    async for event in client:
        ...
```

当连接因为某些原因被关闭时，async for 循环会自动退出，因此不需要额外的错误处理来捕获连接关闭的情况。如果你需要自动重连，可以在 async with 块外层包裹一个 while True 循环。

当然，你也可以使用更简洁的写法：

```python
async for event in NapCatClient(ws_url="ws://xxx", token="your_token"):
    # 处理接收到的事件
    ...
```

这是因为 NapCatClient 实现了开始迭代时自动创建连接(如果连接不可用)的逻辑，因此在 async for 循环开始时会自动建立连接，并在最后一个迭代器被销毁时自动关闭连接。

如果你需要访问client实例，可以采取以下三种方式：

```python
# 1. 在 async for 循环外部创建client实例

client = NapCatClient(ws_url="ws://xxx", token="your_token")

async for event in client:
    ...

# 2. 或者使用海象运算符在 async for 循环中直接创建client实例

async for event in (client := NapCatClient(ws_url="ws://xxx", token="your_token")):
    ...

# 3. 或者通过event.client来访问

async for event in NapCatClient(ws_url="ws://xxx", token="your_token"):
    client = event.client
    ...
```

### 并发接收事件

在同一个 event loop 内，NapCatClient 的 async for 循环支持被多个协程并发迭代，因此你可以在多个协程中同时使用 async for 来接收事件。NapCatClient 本身并未针对跨线程场景做特殊设计，请不要在多个线程之间直接共享同一个 NapCatClient 实例；如确有需要，请在应用层自行加锁或为每个线程创建独立的 NapCatClient。

```python
async def handle_events(client: NapCatClient):
    async for event in client:
        ...

client = NapCatClient(ws_url="ws://xxx", token="your_token")

await asyncio.gather(
    handle_events(client),
    handle_events(client),
    ...
)
```

在这个例子中，多个协程同时使用 async for 来接收事件，NapCatClient 会将事件广播给所有的迭代器，因此每个事件都会被所有的协程接收到（如果某个协程消费过慢，其可能会丢弃最旧事件）。

同时，NapCatClient 内部实现了引用计数，确保在所有迭代器都被销毁后才会真正关闭连接，因此你不需要担心连接被过早关闭的问题。

### 发送消息

NapCatClient 提供了 `send_private_msg` 和 `send_group_msg` 方法来发送私聊消息和群消息：

```python
# 发送私聊消息，返回数据字典，包含消息 ID 等信息
resp = await client.send_private_msg(
    user_id="123456789",
    message="Hello from NapCat!"
)

# 发送群消息，返回数据字典，包含消息 ID 等信息
resp = await client.send_group_msg(
    group_id="987654321",
    message="Hello, group!"
)

print(f"消息发送成功，消息 ID: {resp['message_id']}")
```

### API 调用

NapCat-SDK 采用了 codegen 的方式根据上游 API 定义自动生成了 160+ API 调用方法，你可以通过 NapCatClient 实例来访问这些方法：

```python
user_info = await client.get_login_info()
self_id = user_info["user_id"]
```

api 方法的返回值通常是一个字典，包含了 API 调用的结果数据。得益于完善的 `TypedDict` 类型定义，你可以享受到完整的类型提示和自动补全功能，极大地提升了开发效率和代码质量。

同时，NapCatClient 还实现了动态拦截方法调用的黑魔法，你可以直接通过 `client.method_name(...) ` 的方式来调用任何一个存在或不存在的 API 方法，只是会缺失类型提示。当sdk版本更新后，你无需变更任何代码就能享受到新增方法的类型检查。

```python
# --- 黑魔法区域 ---

def __getattr__(self, item: str):
    if item.startswith("_"):
        raise AttributeError(item)

    async def dynamic_api_call(**kwargs: Any) -> Mapping[str, Any] | None:
        return await self.call_action(item, kwargs)

    return dynamic_api_call
```

### 异常处理

由于网络波动、权限不足或参数错误，API 调用可能会失败。SDK 使用原生异常来表示错误：

1. **逻辑错误 (`RuntimeError`)**: 当 API 返回非 `ok` 状态或 `retcode != 0` 时抛出。
2. **网络超时 (`TimeoutError`)**: 默认 10 秒超时。
3. **连接断开 (`ConnectionError`)**: 连接意外断开时调用 API 抛出。

```python
import asyncio

try:
    await client.send_private_msg(
        user_id="123456", 
        message="Hello"
    )
except RuntimeError as e:
    # 比如对方拒收消息、被禁言等
    print(f"API 调用失败: {e}")
except asyncio.TimeoutError:
    print("API 调用超时")
except ConnectionError:
    print("连接已断开")
```

## ReverseWebSocketServer

`ReverseWebSocketServer` 用于 **Server 模式（反向连接）**，也就是 NapCat 主动连到你的程序。

```python
class ReverseWebSocketServer:
    def __init__(
        self,
        handler: Callable[[NapCatClient], Awaitable[None]],
        host: str = "0.0.0.0",
        port: int = 8080,
        token: str | None = None,
        shutdown_timeout: float = 5.0,
    ):
```

- `handler`: 每个新连接会触发一次，参数是一个独立的 `NapCatClient`
- `host` / `port`: 监听地址和端口
- `token`: 鉴权 token，要求请求头为 `Authorization: Bearer <token>`
- `shutdown_timeout`: 关闭服务时等待连接结束的超时时间

### 基本使用

```python
import asyncio
from napcat import ReverseWebSocketServer, NapCatClient, GroupMessageEvent

async def handler(client: NapCatClient):
    # 每个连接都会获得一个独立 client
    print(f"Bot Connected: self_id={client.self_id}")

    async for event in client:
        if isinstance(event, GroupMessageEvent):
            await event.reply("Server 模式已收到消息")

async def main():
    server = ReverseWebSocketServer(
        handler=handler,
        host="0.0.0.0",
        port=8080,
        token="your_token",
    )
    await server.run_forever()

if __name__ == "__main__":
    asyncio.run(main())
```

### 生命周期管理

`ReverseWebSocketServer` 同样支持异步上下文管理器：

```python
async with ReverseWebSocketServer(handler, host="0.0.0.0", port=8080, token="your_token"):
    await asyncio.Event().wait()
```

或者用 `run_forever()` 配合 `stop()`：

```python
server = ReverseWebSocketServer(handler, token="your_token")

# 在其他协程或信号处理器中调用 server.stop() 后，run_forever() 会退出
await server.run_forever()
```

### Server 模式下的 NapCatClient 连接语义

在 Server 模式中，`handler` 收到的 `client` 是这样构造出来的：

- `client = NapCatClient(_existing_conn=conn)`
- 这个 `client` 不携带 `ws_url` / `token`
- 它的连接对象由外部注入（`Connection(ws)`）

因此在这个模式下：

- `async for event in client` **不会**自动建立连接
- `async for` 结束时也**不会**自动关闭连接
- 连接的开启和关闭由 `ReverseWebSocketServer` 在 `handler` 外层统一管理

也就是当 `handler` 退出后，外层的 `async with client` 会触发退出逻辑并关闭连接。核心代码如下：

```python
# 2. 创建连接对象并追踪任务
conn = Connection(ws)
client = NapCatClient(_existing_conn=conn)
try:
    async with client:
        await self.handler(client)
```

### 多连接与关闭行为

- 每条连接都会创建独立的 `NapCatClient`，互不影响
- handler 中对 `client` 的用法与 Client 模式基本一致（`async for event in client`、`client.send_*` 等）
- 调用 `server.close()`（或退出 `async with`）时，服务端会取消活跃连接任务并等待其结束（等待时长受 `shutdown_timeout` 控制）

### 连接意外关闭时会发生什么

当连接因为网络波动、NapCat 重启等原因意外关闭时，`async for event in client` 会正常结束并退出循环，随后 `handler` 自然返回。

在 Server 模式中，**不要**在 `handler` 里把 `async for` 套在 `while True` 外层，例如：

```python
# 不推荐（Server 模式）
async def handler(client: NapCatClient):
    while True:
        async for event in client:
            ...
```

正确做法是让 `handler` 在断开后结束，把“重连”交给 NapCat 端。NapCat 重新连上来时，`ReverseWebSocketServer` 会创建新的连接并再次调用你的 `handler`。

如果你在 Server 模式里坚持使用 `while True`，通常会出现下面两种情况：

1. 不捕获异常：首次断连后，`async for` 退出；下一轮循环会在已关闭连接上抛出 `RuntimeError`，然后 `handler` 被异常结束。
2. 捕获并吞掉异常继续循环：会在无效连接上反复重试，可能导致空转（CPU 占用升高）和日志刷屏。


## 事件与消息模型

前面我们已经讲了如何建立连接以及接收事件：

```python
async for event in client:
    ...
```

接下来需要理解的是：`event` 到底是什么、消息内容如何表示、以及怎么优雅地回复。

### 事件类型分发

NapCat-SDK 会把上游事件反序列化为强类型对象。最常见的是消息事件：

- `PrivateMessageEvent`：私聊消息
- `GroupMessageEvent`：群消息

同时还包含请求类、通知类、元事件等类型，例如：

- `FriendRequestEvent` / `GroupRequestEvent`
- `NoticeEvent`（及其子类）
- `MetaEvent`（如心跳）

建议使用 `isinstance` 或 `match` 做分发：

```python
async for event in client:
    match event:
        case GroupMessageEvent():
            await event.reply("收到群消息了")
        case PrivateMessageEvent():
            await event.reply("收到私聊消息了")
        case _:
            print(f"其他事件：{event}")

    if isinstance(event, GroupMessageEvent):
        await event.reply("收到群消息了")
    elif isinstance(event, PrivateMessageEvent):
        await event.reply("收到私聊消息了")
    else:
        print(f"其他事件：{event}")
```

> 所有事件都可以从 `napcat` 模块中导入，例如 `from napcat import GroupMessageEvent`

### 事件对象与上下文

每个事件对象都会带有本次事件的上下文信息，并且可通过 `event.client` 拿到当前连接对应的 `NapCatClient` 实例。

这意味着你既可以：

- 在循环外直接使用 `client.send_*` 主动发消息
- 也可以在事件处理里通过 `event.client` 调用 API

```python
async for event in client:
    # event.client 与当前 client 指向同一个连接上下文
    me = await event.client.get_login_info()
    ...
```

### 消息段（MessageSegment）

NapCat-SDK 使用“消息段”来表达富文本消息，而不是让你手动拼 CQ 码。

常见消息段包括：

- `Text`
- `At`
- `Image`
- `Reply`
- `Record` / `Video` 等

例如发送一条“@ + 文本 + 图片”的群消息：

```python
from napcat import Text, At, Image

message = [
    At(qq="123456"),
    Text(text=" 来看这张图"),
    Image(file="https://example.com/image.png"),
]

await client.send_group_msg(group_id="987654321", message=message)
```

你也可以直接传字符串：

```python
await client.send_private_msg(user_id="123456789", message="Hello")
```

### `event.reply(...)` 与 `client.send_*` 的区别

对于消息事件，推荐优先使用 `event.reply(...)` 做“就地回复”。

```python
from napcat import GroupMessageEvent

async for event in client:
    if isinstance(event, GroupMessageEvent):
        await event.reply("收到你的消息了")
```

二者区别可以简单理解为：

- `event.reply(...)`：基于当前事件上下文做回复，SDK 会自动帮你填充目标 ID（如 user_id / group_id）和 Reply 消息段。
- `client.send_private_msg(...)` / `client.send_group_msg(...)`：主动向任意目标发送（更通用）

如果你的逻辑是“收到什么就回什么”，`event.reply(...)` 往往更简洁。

