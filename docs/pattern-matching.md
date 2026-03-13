---
icon: lucide/workflow
---

# 最佳实践：模式匹配的艺术

欢迎来到 **NapCat-SDK** 的核心秘籍。

在过去，编写机器人逻辑往往意味着陷入无穷无尽的 `if-else` 嵌套地狱：判断事件类型、转换类型、检查权限、分割字符串、提取参数。这些琐碎代码经常会把真正的业务逻辑淹没掉。

但现在，时代变了。

得益于 SDK 全面采用 **Dataclass** 和 **强类型** 设计，再结合 Python 3.10+ 的 **结构化模式匹配**，你可以像“画图”一样写机器人逻辑。

**所见即所得。**

## 第一层：告别 `isinstance`（基础路由）

在传统框架中，你可能需要先判断 `event.post_type`，再做类型转换。在 NapCat-SDK 中，我们可以直接匹配对象的**形状**。

### 场景：区分私聊与群聊

```python
from napcat import GroupMessageEvent, NapCatEvent, PrivateMessageEvent


async def handle_event(event: NapCatEvent) -> None:
    match event:
        # 匹配群消息，并直接解构出群号和发送者
        case GroupMessageEvent(group_id=gid, sender=sender):
            print(f"收到群 {gid} 成员 {sender.nickname} 的消息")

        # 匹配私聊消息
        case PrivateMessageEvent(user_id=uid):
            print(f"收到好友 {uid} 的私聊")

        # 忽略其他事件
        case _:
            pass
```

在 `case` 语句里，你不仅是在做类型判断，也是在做**解构赋值**。像 `group_id=gid` 这样的写法，会直接把群号提取到变量 `gid`，不需要之后再写 `event.group_id`。

## 第二层：精准打击（属性过滤）

你不需要进入函数体后再写 `if event.raw_message == "ping"`。很多筛选逻辑，可以在匹配阶段直接完成。

### 场景：特定群的特定指令

```python
from napcat import GroupMessageEvent, MessageSender


async def handle_group_msg(event: GroupMessageEvent) -> None:
    match event:
        # 只有群 123456 发送“开启复读”时才命中
        case GroupMessageEvent(group_id=123456, raw_message="开启复读"):
            await event.reply("复读模式已开启！")

        # 匹配来自 admin 或 owner 的消息
        case GroupMessageEvent(sender=MessageSender(role="admin" | "owner")):
            print("管理员发言，请注意！")

        case _:
            pass
```

这类写法最大的好处，是把“什么时候处理”直接写到了模式本身里。读代码的人不用先看一层类型分发，再往下翻一层条件判断。

## 第三层：庖丁解牛（消息段序列匹配）

这是 `match case` 最有魅力的地方之一。

`event.message` 是一串由 `MessageSegment` 组成的消息段序列。你可以直接按**消息结构**进行匹配，而不是先把原始文本切来切去。

### 场景：命令解析

```python
from napcat import At, Image, Text


async def handle_command(event) -> None:
    match event.message:
        # 纯文本指令
        case [Text(text="help")]:
            await event.reply("帮助文档：...")

        # 组合指令：/ban @某人
        case [Text(text=t), At(qq=target_qq)] if t.strip() == "/ban":
            await event.reply(f"已收到对 {target_qq} 的禁言指令")

        # 搜图指令：搜图 + 图片
        case [Text(text="搜图"), Image(url=img_url)] if img_url:
            print(f"正在搜索图片：{img_url}")

        case _:
            pass
```

这里几乎没有手工解析逻辑。消息结构不符合时，`case` 根本不会命中，代码天然更安全。

> 提示：虽然 `event.message` 在运行时通常是元组，但它同样可以被序列模式 `[...]` 正常匹配。

## 第四层：通配符与 Guard

现实世界的消息经常比理想格式复杂。用户可能会多发空格，也可能在图片前后夹一堆话。这时候就该让 `if` guard 出场了。

### 场景：宽松匹配与逻辑补充

需要注意的是，Python 的序列模式**只允许一个带星号的子模式**。所以像 `[*_, Image(), *_]` 这样的写法虽然直观，但实际上是无效语法。

更稳妥的方式是：先把整个消息序列绑定到变量，再在 guard 里补充更复杂的判断。

```python
from collections.abc import Sequence

from napcat import GroupMessageEvent, Image, MessageSender, Text


def first_image_url(segments: Sequence[object]) -> str | None:
    for segment in segments:
        if isinstance(segment, Image) and segment.url:
            return segment.url
    return None


async def handle_group_event(event: GroupMessageEvent) -> None:
    match event:
        # 只要消息里包含一张图片，且发送者是管理员
        case GroupMessageEvent(
            sender=MessageSender(role="admin"),
            message=segments,
        ) if (url := first_image_url(segments)):
            await event.reply(f"管理员发图了，地址：{url}")

        # 关键词触发，忽略复杂的文本判断细节
        case GroupMessageEvent(message=[Text(text=t)]) if "笨蛋" in t:
            await event.reply("你才笨蛋！")

        case _:
            pass
```

模式负责“看形状”，guard 负责“补逻辑”。这两者配合起来，表达力会非常强。

## 第五层：最终奥义（嵌套解构）

当你把类型、属性、序列结构和 guard 混在一起使用时，代码会开始接近一种“声明式”的风格。

### 场景：复杂的新人入群自我介绍

需求：

1. 必须是群消息。
2. 发送者必须是男性（`sex="male"`）。
3. 消息结构必须是：`Text("我是") + Text(名字) + Image(自拍)`。
4. 我们要提取群号、用户 ID、名字和图片地址。

```python
from napcat import GroupMessageEvent, Image, MessageSender, Text


async def handle_intro(event) -> None:
    match event:
        case GroupMessageEvent(
            group_id=gid,
            sender=MessageSender(sex="male", user_id=uid),
            message=[Text(text="我是"), Text(text=name), Image(url=photo_url), *_],
        ) if name.strip() and photo_url:
            print(f"群 {gid} 成员 {uid} 自称：{name}")
            print(f"照片地址：{photo_url}")
            await event.reply(f"你好，{name}！")

        case _:
            pass
```

这段逻辑里几乎没有“准备变量”的代码。匹配成功时，业务所需的数据已经全部在手上了。

## 陷阱警告：变量匹配与捕获

这是很多人初学模式匹配时最容易翻车的地方。

如果你想匹配的不是一个**字面量**，而是一个**外部变量**，不能直接把那个变量名写进模式里。

### 错误示范

```python
target_group = 987654321

match event:
    # 错误：这里不是“比较”，而是“捕获”
    case GroupMessageEvent(group_id=target_group):
        print("这行代码会匹配所有群消息")
```

上面这段代码不会拿 `event.group_id` 和外部的 `target_group` 做比较。它会把当前事件里的群号**重新绑定**给 `target_group`。

### 正确示范

```python
target_group = 987654321

match event:
    case GroupMessageEvent(group_id=gid) if gid == target_group:
        print("确实是目标群发来的消息")
```

对于变量比较，请优先用 guard。

## 什么时候用 `match case`，什么时候用 `event_match(...)`

这两者不是竞争关系，而是互补关系。

- `match case`：适合写**持续运行中的事件处理逻辑**，让分支结构一眼可见。
- `event_match(...)`：适合配合 `client.wait_event(...)` 这类场景，用来表达“一次性的等待条件”。

如果你的代码是“来一个事件就处理一个事件”，优先考虑 `match case`。如果你的代码是“我要等一个满足条件的事件出现”，那 `event_match(...)` 通常会更自然。

## 总结

在 NapCat-SDK 中使用 `match case`，可以记住三个心法：

1. **形状优先**：先思考你要的事件和消息“长什么样”，然后把它直接写进 `case`。
2. **就地提取**：匹配成功时，顺手把你要用的数据也解构出来。
3. **逻辑后置**：简单条件写在模式里，复杂条件交给 `if` guard。

当你的事件处理代码越来越像“描述数据形状”，而不是“堆判断语句”时，说明你已经进入状态了。
