---
icon: lucide/workflow
---

# 最佳实践：模式匹配的艺术

欢迎来到 **NapCat-SDK** 的核心秘籍。

在过去，编写机器人逻辑往往意味着陷入无穷无尽的 `if-else` 嵌套地狱：判断事件类型、转换类型、检查权限、分割字符串、提取参数……这些琐碎的代码掩盖了真正的业务逻辑。

但现在，时代变了。

得益于 SDK 全面采用 **Dataclass** 和 **强类型** 设计，结合 Python 3.10+ 的 **结构化模式匹配**，你可以像“画图”一样编写代码。

**所见即所得。**

## 🚀 第一层：告别 `isinstance` (基础路由)

在传统框架中，你可能需要先判断 `event.post_type`，再强转类型。在 NapCat-SDK 中，我们直接匹配对象的**形状**。

### 场景：区分私聊与群聊

```python
from napcat.client import NapCatClient
from napcat.types.events import GroupMessageEvent, PrivateMessageEvent, NapCatEvent

async def handle_event(event: NapCatEvent):
    match event:
        # ✅ 匹配群消息，并自动获得 GroupMessageEvent 的类型提示
        case GroupMessageEvent(group_id=gid, sender=sender):
            print(f"收到群 {gid} 成员 {sender.nickname} 的消息")

        # ✅ 匹配私聊消息
        case PrivateMessageEvent(user_id=uid):
            print(f"收到好友 {uid} 的私聊")

        # ❌ 忽略其他所有事件（如心跳、请求等）
        case _:
            pass
```

> **💡 Pro Tip:** 在 `case` 语句中，你不仅是在做类型判断，还在做**解构赋值**。注意 `group_id=gid`，我们直接把群号提取到了变量 `gid` 中，无需稍后访问 `event.group_id`。

## ⚡ 第二层：精准打击 (属性过滤)

你不需要进入函数体后再写 `if event.raw_message == 'ping'`。可以在匹配阶段直接拦截特定属性。

### 场景：特定群的特定指令

```python
async def handle_group_msg(event: GroupMessageEvent):
    match event:
        # 🎯 只有群 123456 发送 "开启复读" 时才会命中
        case GroupMessageEvent(group_id=123456, raw_message="开启复读"):
            await event.reply("复读模式已开启！")

        # 🎯 匹配来自 "admin" 或 "owner" 的消息
        # 使用 `|` 符号表示逻辑或
        case GroupMessageEvent(sender=MessageSender(role="admin" | "owner")):
            print("管理员发言，请注意！")
```

## 🔥 第三层：庖丁解牛 (消息段序列匹配)

这是 `match case` 最具魔力的时刻。 `event.message` 是一个由 `MessageSegment` 组成的列表（元组）。我们可以直接匹配这个**列表的结构**，从而免去复杂的字符串解析。

### 场景：命令解析 `python /ban @某人`

假设指令格式为：`文本("/ban")` + `At(目标)`。

```python
from napcat.types.messages import Text, At, Image

match event.message:
    # 模式 A: 纯文本指令
    # 匹配：[Text(text="help")]
    case [Text(text="help")]:
        await event.reply("帮助文档：...")

    # 模式 B: 复杂的组合指令
    # 匹配：[Text("/ban "), At(target_qq)]
    # 注意：这里直接提取出了 target_qq！
    case [Text(text=t), At(qq=target_qq)] if t.strip() == "/ban":
        await client.set_group_ban(event.group_id, target_qq, duration=600)
        await event.reply(f"已禁言用户 {target_qq}")

    # 模式 C: 搜图指令
    # 匹配：[Text("搜图"), Image(url)]
    case [Text(text="搜图"), Image(url=img_url)]:
        print(f"正在搜索图片: {img_url}")
```

> **✨ Magic:** 不需要 `split()`，不需要遍历 list，不需要 `isinstance`。如果消息结构不符合（例如用户发了 `/ban` 但没 `@` 人），`case` 根本不会命中，代码极其安全。

## 🌪️ 第四层：万象天引 (通配符与守卫)

现实世界的消息往往很复杂。用户可能会在指令里加空格，或者在图片前后废话。这时我们需要 `*` (Wildcard) 和 `if` (Guard)。

### 场景：宽松匹配与逻辑守卫

```python
match event:
    # 🌟 场景：只要消息里包含“一张图片”，且发送者是管理员
    # [*_, Image(), *_] 表示：前面有些东西，后面有些东西，中间必须有个 Image
    case GroupMessageEvent(
        sender=MessageSender(role="admin"),
        message=[*_, Image(url=url), *_]
    ):
        await event.reply(f"管理员发图了，地址：{url}")

    # 🌟 场景：关键词触发，忽略多余空格
    # 使用 Guard (if 子句) 处理复杂的字符串逻辑
    case GroupMessageEvent(message=[Text(text=t)]) if "笨蛋" in t:
        await event.reply("你才笨蛋！")
```

## 👑 第五层：最终奥义 (嵌套解构与别名)

当你掌握了以上所有技巧，你可以写出看起来像魔法一样的代码。我们将类型、属性、列表结构、逻辑判断融为一体。

### 场景：复杂的“新人入群欢迎”逻辑

**需求**：

1. 必须是群消息。
2. 发送者必须是男性 (`sex='male'`)。
3. 消息格式必须是：`Text("我是") + Text(名字) + Image(自拍)`。
4. 我们要提取他的名字和照片 URL。

```python
# 一气呵成，没有任何多余的赋值语句
match event:
    case GroupMessageEvent(
        group_id=gid,
        sender=MessageSender(sex="male", user_id=uid), # 提取 uid
        message=[
            Text(text="我是"),       # 开头必须是 "我是"
            Text(text=name),        # 第二段是名字，提取为 name
            Image(url=photo_url),   # 第三段是照片，提取为 photo_url
            *_                      # 忽略后面可能跟的表情包
        ]
    ) if len(name) < 10:            # 额外的逻辑检查：名字不能太长
        
        # 🚀 业务逻辑直接开始
        print(f"群 {gid} 来了个帅哥 {name} (ID: {uid})")
        print(f"爆照地址: {photo_url}")
        await client.send_group_msg(gid, message=f"欢迎帅哥 {name}！")

    case _:
        pass # 不符合格式的直接忽略
```

## ⚠️ 陷阱警告：变量匹配与捕获

这是很多新手（甚至老手）容易翻车的地方。

如果你想匹配的不是一个**字面量**（如 `123456`），而是一个**外部变量**，**不能**直接写在参数里。

### ❌ 错误示范

```python
target_group = 987654321

match event:
    # 错误！Python 会认为你在定义一个新变量 target_group 并赋值！
    # 这会导致它匹配所有群，并且把群号赋值给 target_group。
    case GroupMessageEvent(group_id=target_group):
        print("这行代码永远会被执行，而且 target_group 变成了当前群号")
```

### ✅ 正确示范

对于变量匹配，必须使用 **Guard (卫语句)**：

```python
target_group = 987654321

match event:
    # 正确：先捕获为 gid，再用 if 判断是否等于 target_group
    case GroupMessageEvent(group_id=gid) if gid == target_group:
        print("确实是目标群发来的消息")
```

> **原理：** 在 Python 模式匹配中，只有**字面量**（数字、字符串）和**带点的名称**（如 `Consts.GROUP_ID`）才会被当作值来匹配。普通的变量名会被当作**捕获模式 (Capture Pattern)**，也就是赋值操作。

## 📝 总结

在 NapCat-SDK 中使用 `match case` 的三个心法：

1. **形状优先**：先思考你期望的数据“长什么样”（类结构、列表结构），直接把形状写在 `case` 后。
2. **就地提取**：不要先匹配再赋值，直接在匹配时使用 `param=var_name` 提取变量。
3. **守卫逻辑**：简单的值匹配写在对象里，复杂的变量对比写在 `if` 后。

现在，去写出像散文一样优雅的代码吧。
