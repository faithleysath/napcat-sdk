---
icon: lucide/plug
---


# NapCatClient 核心指南

`NapCatClient` 是与 NapCat 交互的智能中枢。

为了让你更自然地理解它，我们采用了**“配置与执行分离”**的设计哲学。你不需要手动管理复杂的 Socket 连接状态，只需告诉 Client “去哪里连接”，剩下的生命周期管理交由 SDK 自动完成。

## 1. 核心哲学：配置即蓝图

当你实例化 `NapCatClient` 时，**网络连接并不会立即建立**。 此时的 `client` 只是一个保存了连接配置（URL 和 Token）的“蓝图”对象。这意味着你可以安全地在程序的任何地方创建它，而不用担心资源消耗。

```python
# 仅仅是配置，没有任何网络活动
client = NapCatClient(ws_url="ws://127.0.0.1:3000", token="123456")
```

真正的连接行为，只会在你明确进入**上下文（Context）**或**迭代（Iterate）**时通过“懒加载”触发。

## 2. 生命周期：自动化的连接管理

NapCatClient 实现了智能的上下文管理器。你无需手动调用 `connect()` 或 `close()`，使用 `async with` 即可掌控一切。

- **进入时**：自动建立 WebSocket 连接。
- **退出时**：自动关闭连接并清理资源。

```python
# 进入代码块 -> 自动连接
async with client:
    # 此时连接已建立，is_running 为 True
    await client.send_group_msg(group_id="123", message="上线啦！")

# 离开代码块 -> 自动断开
```

## 3. 事件流：一切皆是迭代

在 NapCat 的设计中，事件接收被抽象为**异步数据流**。 你不需要编写复杂的回调函数，只需要像遍历列表一样，使用 `async for` 遍历源源不断的事件。

更棒的是，`NapCatClient` 极其智能：**如果你在迭代时还未建立连接，它会自动为你连接。**

```python
# 写法极简：自动连接 -> 接收事件 -> 迭代结束自动断开
async for event in NapCatClient(ws_url="...", token="..."):
    if event.post_type == "message":
        print(f"收到消息: {event.message}")
```

> **并发友好**：你可以在同一个 Client 实例上启动多个 `async for` 循环（例如在不同的协程中），SDK 内部会将事件广播给所有监听者，而不会造成冲突。

## 4. API 调用：静态类型与动态扩展的融合

**NapCat-SDK** 在 API 设计上追求**“极致的开发体验”**与**“未来的兼容性”**并存。

### 🛡️ 静态优先：像调用本地函数一样调用 API

得益于 **OpenAPI Codegen** 技术，SDK 内置了上游 **160+ API** 的完整定义。 当你输入 `client.` 时，IDE 会立即列出所有可用方法。每个方法都拥有完整的 `TypedDict` 类型定义、详细的 Docstring 文档甚至使用示例。

这意味着：

- **零记忆负担**：无需查阅文档，IDE 即是文档。
- **类型安全**：返回值里的字段都有类型提示，再也不用靠 `print` 来猜字典里有什么 key。

```python
# 享受完整的代码补全和类型检查
user_info = await client.get_login_info() 

# user_info 是 TypedDict，IDE 会提示 user_id 是 int 类型
print(user_info["user_id"])
```

### ⚡️ 动态兜底：面向未来的黑魔法

如果服务端更新了新功能，而 SDK 尚未重新生成代码，怎么办？ Client 内部保留了**动态代理机制**。它能够智能拦截所有未定义的方法调用，并将其自动转换为标准的 API 请求。

这意味着你拥有了**版本免疫力**：即使不更新 SDK，你也可以直接调用服务端的新特性，虽然失去了类型提示，但保证了功能的即时可用性。

```python
# 假设服务端新增了 "new_feature"，SDK 还没更新
# 你依然可以直接调用，client 会自动将其转换为 action="new_feature" 的请求
await client.new_feature(param="value")
```

---

## 总结：你的开发直觉

1. **实例化**只是在写配置，不耗资源。
2. **async with** 帮你管理连接开关。
3. **async for** 帮你源源不断地拉取事件。
4. **client.xxx()** 帮你自动发送 API 请求。
