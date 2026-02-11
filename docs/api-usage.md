---
icon: lucide/code
---

# API 调用

NapCat-SDK 提供两种调用方式：

1. **强类型 API**：通过 `client.<api_method>(...)` 直接调用
2. **动态调用**：通过 `client.call_action` 或直接调用 `client.some_action()`

## 强类型 API

所有 API 定义都被自动生成，并带有类型提示。

```python
login_info = await client.get_login_info()
print(login_info["nickname"])

members = await client.get_group_member_list(
    group_id=123456,
    no_cache=True,
)
```

## 动态调用

当上游接口更新而 SDK 尚未同步时，可使用动态调用：

```python
await client.call_action("some_new_action", {"param": 1})
```

或者直接：

```python
await client.some_new_action(param=1)
```

## 发送消息 API

SDK 在调用 `send_private_msg` 与 `send_group_msg` 时会自动序列化消息链：

```python
from napcat import Text

await client.send_group_msg(
    group_id=123456,
    message=[Text(text="hello")],
)
```

## 错误处理

当返回 `status != ok` 或 `retcode != 0` 时，SDK 会抛出 `NapCatAPIError`。

建议在业务层统一捕获并记录：

```python
try:
    await client.get_login_info()
except NapCatAPIError as exc:
    logger.error("API 调用失败: %s", exc)
    logger.debug("action=%s retcode=%s", exc.action, exc.retcode)
```

常见异常类型：

- `NapCatAPIError`: API 返回失败状态
- `NapCatProtocolError`: 上报事件数据不符合预期结构
- `NapCatStateError`: 客户端未连接或事件未绑定
