---
icon: lucide/message-circle
---

# 事件与消息

NapCat-SDK 将 OneBot 事件封装为强类型对象，并提供消息段组件，避免手动拼接 CQ 码。

## 事件类型

SDK 内置常见事件类型，例如：

- `PrivateMessageEvent`
- `GroupMessageEvent`
- `FriendRequestEvent`
- `GroupRequestEvent`

你可以使用 `match` 或 `isinstance` 进行分发：

```python
from napcat import GroupMessageEvent, PrivateMessageEvent

async for event in client:
    match event:
        case PrivateMessageEvent():
            ...
        case GroupMessageEvent():
            ...
```

## 消息段（MessageSegment）

常用消息段类型：

- `Text`
- `Image`
- `At`
- `Reply`
- `Voice` / `Record`

示例：发送一条带 @ 与图片的消息。

```python
from napcat import Text, Image, At

message = [
    At(qq="123456"),
    Text(text=" 来看这张图"),
    Image(file="https://example.com/image.png"),
]

await client.send_group_msg(group_id=123456, message=message)
```

## 回复与引用

大多数消息事件提供快捷方法：

- `event.reply(...)`：回复并自动引用原消息
- `event.send_msg(...)`：发送消息（私聊 / 群聊）

```python
async for event in client:
    await event.reply("收到")
```

## 自定义消息链

你可以传入以下三种形式：

1. `str`
2. `MessageSegment` 或 `Message`
3. `list[MessageSegment]`

SDK 会自动做消息链序列化，无需手动处理。
