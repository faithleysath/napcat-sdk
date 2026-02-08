---
icon: lucide/help-circle
---

# 常见问题

## 1. 为什么 `self_id` 是 -1？

SDK 会在连接成功后调用 `get_login_info` 获取登录号。如果 NapCat 未配置该 API 或连接权限不足，会回落为 -1。请检查 NapCat 是否正常运行，以及 Token 是否正确。

## 2. 如何处理事件分发？

你可以直接在 `async for event in client` 中使用 `match` 语法分发，也可以将事件路由到你自己的调度器中。

## 3. 消息为什么发送失败？

请优先确认：

- WebSocket 连接是否可用
- Token 是否正确
- 是否具有对应群或好友的发送权限

## 4. 能否发送富媒体消息？

可以。使用 `Text`、`Image`、`At` 等消息段组合成列表后发送即可。

## 5. SDK 没有某个 API？

请使用动态调用临时绕过：

```python
await client.call_action("some_new_action", {"param": 1})
```

同时建议在上游协议同步后更新 SDK 或提 Issue。
