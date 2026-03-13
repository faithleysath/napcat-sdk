# 示例

这些示例是为真实 Bot 场景准备的最小可改模板，适合直接复制后按需调整。

## 运行方式

在仓库根目录执行：

```bash
uv sync
uv run python examples/01_forward_client.py
```

## 文件说明

- `01_forward_client.py`：连接 NapCat 正向 WebSocket，并处理私聊/群聊消息。
- `02_reverse_server.py`：启动反向 WebSocket 服务端，接收 NapCat 主动连接。
- `03_send_rich_media.py`：发送由 `At`、`Text`、`Image` 组成的强类型消息链。
- `04_wait_for_keyword.py`：使用 `event_match(...)` 等待匹配事件，并自动回复。
- `05_pattern_matching.py`：集中演示类型匹配、属性过滤、消息段序列匹配和 guard 写法。

## 推荐阅读顺序

1. `01_forward_client.py`：先熟悉最基础的事件循环和对象匹配。
2. `05_pattern_matching.py`：重点看模式匹配如何直接表达业务意图。
3. `03_send_rich_media.py`：看强类型消息段如何参与发送。
4. `02_reverse_server.py`：了解反向 WebSocket 的服务端写法。
5. `04_wait_for_keyword.py`：最后看 `event_match(...)` 和等待单次事件的组合。

## 延伸阅读

- `../docs/pattern-matching.md`：更系统地讲解 NapCat-SDK 里该如何使用结构化模式匹配。

## 环境变量

- `NAPCAT_WS_URL`：正向 WebSocket 地址，例如 `ws://127.0.0.1:3001`。
- `NAPCAT_TOKEN`：可选的 Bearer Token，正向客户端和反向服务端示例都会读取它。
- `NAPCAT_GROUP_ID`：发送消息或等待事件时使用的目标群号。当前请求模型里这类 ID 多为字符串。
- `NAPCAT_SERVER_HOST`：反向服务端监听地址，默认 `0.0.0.0`。
- `NAPCAT_SERVER_PORT`：反向服务端监听端口，默认 `8080`。

## 说明

- 请求参数中的 `group_id`、`user_id` 等字段在生成的 API 模型里通常是 `str`。
- 事件对象中的 `event.group_id` 这类字段会按运行时事件类型解析，很多情况下是 `int`。
