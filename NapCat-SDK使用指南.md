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
# 发送私聊消息，返回消息 ID
msg_id = await client.send_private_msg(
    user_id=123456789,
    message="Hello from NapCat!"
)

# 发送群消息，返回消息 ID
group_msg_id = await client.send_group_msg(
    group_id=987654321,
    message="Hello, group!"
)
```

### API 调用

NapCat-SDK 采用了 codegen 的方式根据上游 API 定义自动生成了 160+ API 调用方法，这些方法都定义在 NapCatClient.api 属性中，你可以通过 NapCatClient 实例来访问这些方法：

```python
user_info = await client.api.get_login_info()
self_id = user_info["user_id"]
```

api 方法的返回值通常是一个字典，包含了 API 调用的结果数据。得益于完善的 `TypedDict` 类型定义，你可以享受到完整的类型提示和自动补全功能，极大地提升了开发效率和代码质量。

部分 api 方法会在 client 中进行包装，提供更友好的接口，例如 `send_private_msg` 和 `send_group_msg` 方法就是对底层 API 的包装，提供了更简洁的参数和返回值。你可以根据需要选择使用底层 API 方法或者包装后的方法。

同时，NapCatClient 还实现了动态拦截方法调用的黑魔法，你可以直接通过 `client.api.method_name(a=..., b=...) ` 的方式来调用任何一个存在或不存在的 API 方法，只是后者会缺失类型提示。当sdk版本更新后，你无需变更任何代码就能享受到新增方法的类型检查。

```python
# --- 黑魔法区域 ---

def __getattr__(self, item: str):
    if item.startswith("_"):
        raise AttributeError(item)

    async def dynamic_api_call(**kwargs: Any) -> Mapping[str, Any] | None:
        return await self.call_action(item, kwargs)

    return dynamic_api_call
```

