# NapCat OneBot Action/Schema 运行时一致性核查报告

- 核查日期：2026-03-10
- 工作区：`/Users/laysath/proj/napcat-sdk`
- 代码范围：
  - `NapCatQQ/packages/napcat-onebot/action`
  - `NapCatQQ/packages/napcat-onebot/api`
  - `NapCatQQ/packages/napcat-onebot/types`
  - `NapCatQQ/packages/napcat-schema`
  - 必要时向下追踪到 `NapCatQQ/packages/napcat-core`
- 目标：判断 `schema` 定义是否与 action/api 的运行时行为一致，并给出任何人/AI 都能直接照着修完的修复方案。

---

## 1. 最终结论

本次扫描覆盖了 `napcat-onebot` 下 **161 个 concrete action**。结论如下：

1. **绝大多数 action 的顶层 payload 字段与运行时读取是一致的。**
2. **真正严重的问题集中在消息发送链路**，尤其是：
   - `send_msg`
   - `send_private_msg`
   - `send_group_msg`
   - `send_forward_msg`
   - `send_private_forward_msg`
   - `send_group_forward_msg`
3. **`returnSchema` 目前不是运行时约束，只是文档/导出元数据。**
4. 另外存在一批 **死参数、占位 action、example 漂移**，这些问题不会都导致运行时报错，但会直接误导调用方、OpenAPI、调试面板和其他 AI。

如果只修一件事，**先修 `SendMsgBase.check()` 不调用 `super.check()` 的问题**。这是本报告里影响面最大、连锁效应最多的问题。

---

## 2. 运行时基线：schema 实际是怎么生效的

### 2.1 `payloadSchema` 的唯一生效入口

`payloadSchema` 只会通过 `OneBotAction.check()` 生效。

关键文件：

- [OneBotAction.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/OneBotAction.ts#L67)

当前机制：

1. `handle()` / `websocketHandle()` 调用 `this.check(payload)`。
2. 默认 `check()` 会：
   - `TypeCompiler.Compile(this.payloadSchema)`
   - `Value.Parse(this.payloadSchema, payload)`
   - `validate.Check(payload)`
3. 只有 `check()` 返回 `valid: true`，才会进入 `_handle()`。

也就是说：

- **谁覆盖了 `check()`，谁就接管了 payload 校验。**
- 如果覆盖后的 `check()` 不调用 `super.check()`，那这个 action 的 `payloadSchema` 就是“写了，但运行时没用”。

### 2.2 `returnSchema` 不是运行时校验

关键文件：

- [OneBotAction.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/OneBotAction.ts#L90)
- [napcat-schema/index.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-schema/index.ts#L474)

当前事实：

- `OneBotAction.handle()` 和 `websocketHandle()` **不会**对 `_handle()` 的返回值做 `returnSchema` 校验。
- `returnSchema` 只会被 `napcat-schema` 收集后用于：
  - OpenAPI
  - 调试面板
  - schema 导出

因此：

- **payload/schema 不一致 = 运行时和文档都会出问题。**
- **return/schema 不一致 = 运行时不一定炸，但文档和工具一定会错。**

### 2.3 `action-local schema` 和 `shared schema` 是两套系统

关键文件：

- [SendMsg.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/msg/SendMsg.ts#L22)
- [message.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/types/message.ts#L349)

现在发送消息至少有两套 schema：

1. `action/msg/SendMsg.ts` 里的 `SendMsgPayloadSchema`
2. `types/message.ts` 里的 `OB11PostSendMsgSchema`

这两套 schema 已经发生漂移：

- `OB11PostSendMsgSchema` 有 `messages`
- `SendMsgPayloadSchema` 没有 `messages`

但 `napcat-schema` 导出的是 **action 自己挂的 `payloadSchema`**，不是共享 schema。  
所以只要 action-local schema 漂了，OpenAPI/调试页就会跟着一起漂。

---

## 3. 问题总表

| ID | 严重级别 | 问题 | 受影响 action |
| --- | --- | --- | --- |
| A-01 | P1 | `SendMsgBase.check()` 绕过 `payloadSchema` | 6 个发送消息 action |
| A-02 | P1 | `send_forward_msg*` schema 缺少 `messages` | 3 个 forward action |
| A-03 | P2 | `OB11MessageNodeSchema` 比运行时严格 | 所有 forward node 输入 |
| A-04 | P2 | `set_group_leave.is_dismiss` 是死参数 | `set_group_leave` |
| A-05 | P3 | `set_doubt_friends_add_request.approve` 是死参数 | `set_doubt_friends_add_request` |
| A-06 | P3 | `set_group_album_media_like.set` 是死参数 | `set_group_album_media_like` |
| A-07 | P2/P3 | 若干 action 是 stub/占位实现，但 schema/example 仍宣称可用 | `check_url_safely` / `get_online_clients` / `_set_model_show` / `get_guild_list` / `get_guild_service_profile` |
| A-08 | P4 | 部分 `payloadExample` / `returnExample` 与 schema 或运行时不一致 | 多个 action |
| A-09 | P4 | 少数无参 action 缺失显式空 payload schema | `_mark_all_as_read` / `get_version_info` |

---

## 4. 详细问题与修复说明

## A-01. `SendMsgBase.check()` 绕过了 payload schema

### 4.1 现状

关键文件：

- [OneBotAction.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/OneBotAction.ts#L67)
- [SendMsg.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/msg/SendMsg.ts#L130)
- [SendPrivateMsg.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/msg/SendPrivateMsg.ts#L19)
- [SendGroupMsg.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/group/SendGroupMsg.ts#L15)
- [SendForwardMsg.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/go-cqhttp/SendForwardMsg.ts#L8)

`SendMsgBase.check()` 当前实现：

```ts
protected override async check (payload: SendMsgPayload): Promise<BaseCheckResult> {
  const messages = normalize(payload.message);
  const nodeElementLength = getSpecialMsgNum(messages, OB11MessageDataType.node);
  if (nodeElementLength > 0 && nodeElementLength !== messages.length) {
    return { valid: false, message: '...' };
  }
  return { valid: true };
}
```

问题不在这段逻辑本身，而在于它**没有调用 `super.check(payload)`**。

结果：

- `SendMsgPayloadSchema` 不会被执行
- `Value.Parse()` 不会发生
- 类型 coercion 不会发生
- 必填检查不会发生
- 错误码会从“参数错误”退化成“深层运行时失败”

### 4.2 受影响 action

受 `SendMsgBase` 影响的 concrete action 共 6 个：

1. `send_msg`
2. `send_private_msg`
3. `send_group_msg`
4. `send_forward_msg`
5. `send_private_forward_msg`
6. `send_group_forward_msg`

### 4.3 为什么这是 P1

这是本仓库里最重要的 schema/runtime 失配，因为它不是单个字段问题，而是：

- **整条发送消息契约都没被 schema 守住**
- 文档和运行时会同时误导调用方
- 后续 forward node / `messages` / ID coercion 等问题都会被它放大

### 4.4 必须怎么修

#### 方案：在 `SendMsgBase.check()` 的最开始调用 `super.check(payload)`

建议改成：

```ts
protected override async check (payload: SendMsgPayload): Promise<BaseCheckResult> {
  const base = await super.check(payload);
  if (!base.valid) {
    return base;
  }

  const messages = normalize(payload.message);
  const nodeElementLength = getSpecialMsgNum(messages, OB11MessageDataType.node);
  if (nodeElementLength > 0 && nodeElementLength !== messages.length) {
    return {
      valid: false,
      message: '转发消息不能和普通消息混在一起发送,转发需要保证message只有type为node的元素',
    };
  }

  return { valid: true };
}
```

#### 为什么顺序必须是“先 `super.check()`，再做 node 校验”

因为：

1. `super.check()` 负责把 schema parse/coerce 到 payload 上
2. 然后 `normalize(payload.message)` 才能基于 schema 解析后的值工作
3. 如果先做 `normalize()`，那 `payload.message` 缺失时就会直接把脏数据带入后续逻辑

### 4.5 修完后的预期行为

- 缺少 `message` 时：
  - `send_msg` 系列应在 `check()` 阶段失败
  - HTTP 返回 400
  - WebSocket 返回 1400
- `user_id: 123456` / `group_id: 123456` 这种可被 parse 的输入应按 schema 处理，而不是等到 `_handle()` 里再碰运气

### 4.6 必须补的测试

建议新增或修改 `NapCatQQ/packages/napcat-test/schema.test.ts`，并新增一个 action contract test 文件，例如：

- `NapCatQQ/packages/napcat-test/action-contract.test.ts`

至少要补这 3 个测试：

1. `send_private_msg` 缺少 `message` 时，`websocketHandle()` 返回 `retcode=1400`
2. `send_group_msg` 缺少 `group_id` 时，`websocketHandle()` 返回 `retcode=1400`
3. `send_forward_msg` 传混合 node/non-node 时，依旧按当前业务规则失败，但失败来源应该是 `check()`，不是深层 `_handle()`

---

## A-02. `send_forward_msg*` 的 action schema 缺少 `messages`

### 4.7 现状

关键文件：

- [SendForwardMsg.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/go-cqhttp/SendForwardMsg.ts#L1)
- [SendMsg.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/msg/SendMsg.ts#L22)
- [message.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/types/message.ts#L349)
- [napcat-schema/index.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-schema/index.ts#L484)

运行时行为：

```ts
type GoCQHTTPSendForwardMsgPayload = SendMsgPayload & { messages?: OB11MessageMixType; };

if (payload.messages) payload.message = normalize(payload.messages);
return super.check(payload);
```

说明运行时明确支持：

- `messages`
- 然后在 `check()` 阶段把它转成 `message`

但是 action 自身继承的 `SendMsgPayloadSchema` 只有：

- `message_type`
- `user_id`
- `group_id`
- `message`
- `auto_escape`
- `source`
- `news`
- `summary`
- `prompt`

**没有 `messages`。**

同时，共享 schema `OB11PostSendMsgSchema` 又已经有 `messages`。这说明是 duplicated schema 漂移。

### 4.8 为什么这是 P1

这不是 example 小问题，而是：

1. go-cqhttp 兼容接口的**主输入字段**没进 action schema
2. `napcat-schema` 导出用的是 action-local schema
3. 所有依赖导出 schema 的调用方/AI/调试页都会得到错误的请求格式

### 4.9 推荐修法

#### 首选修法：给 `GoCQHTTPSendForwardMsgBase` 单独挂正确的 payload schema

不要继续复用原封不动的 `SendMsgPayloadSchema`。

建议在 `SendForwardMsg.ts` 中新增：

```ts
const GoCQHTTPSendForwardPayloadSchema = Type.Union([
  SendMsgPayloadSchema,
  Type.Intersect([
    Type.Omit(SendMsgPayloadSchema, ['message']),
    Type.Object({
      messages: OB11MessageMixTypeSchema,
      message: Type.Optional(OB11MessageMixTypeSchema),
    }),
  ]),
]);
```

然后在 `GoCQHTTPSendForwardMsgBase` 上显式挂：

```ts
override payloadSchema = GoCQHTTPSendForwardPayloadSchema;
```

这样能完整保留当前运行时兼容性：

- `message` 仍可用
- `messages` 也可用
- 文档/调试页不再错

#### 更长期的修法：统一到共享 schema

如果准备系统性收敛 schema，建议：

1. 让发送消息 action 复用 `types/message.ts` 里的共享 schema
2. action 层只做少量差异化扩展，不要再本地复制一套字段清单

### 4.10 验收标准

修完后，以下输入都必须满足：

1. `send_forward_msg` 的 action 导出 schema 中包含 `messages`
2. 调试页看到的入参文档里能看到 `messages`
3. `messages` 作为唯一字段时可正常通过 `check()`
4. `message` 作为兼容字段时也可正常通过 `check()`

### 4.11 必补测试

1. `actionSchemas['send_forward_msg'].payload` 必须包含 `messages`
2. `payloadExample` 中使用 `messages` 的 action，schema 也必须包含 `messages`

---

## A-03. `OB11MessageNodeSchema` 比运行时严格

### 4.12 现状

关键文件：

- [message.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/types/message.ts#L280)
- [SendMsg.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/msg/SendMsg.ts#L228)
- [SendMsg.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/msg/SendMsg.ts#L362)

当前 `OB11MessageNodeSchema` 要求：

- `nickname` 必填
- `content` 必填

但运行时实际上支持至少两种 node 形态：

### 形态 1：引用已有消息

运行时分支：

```ts
if (node.data.id) {
  // 直接按 id 找原消息
}
```

这类 node 实际只需要：

```json
{
  "type": "node",
  "data": {
    "id": "123456"
  }
}
```

不需要 `content`。

### 形态 2：内联构造 node

运行时分支：

```ts
if (!node.data.id) {
  const OB11Data = normalize(node.data.content);
  ...
  senderName: (node.data.nickname || node.data.name) ?? parentMeta?.nickname ?? 'QQ用户'
}
```

说明：

- `content` 对 inline node 是必需的
- 但发送者名不一定必须来自 `nickname`
- `name` 可以兜底
- 父节点和机器人默认值也可以兜底

另外：

- schema 里的 `time` 现在是 `Type.String`
- 运行时却是 `Number(node.data.time)`
- 所以数值型 `time` 也是运行时支持的

### 4.13 推荐修法

把 `OB11MessageNodeSchema` 改成联合，而不是单一 object：

#### 参考 node

```ts
const OB11MessageNodeReferenceSchema = Type.Object({
  type: Type.Literal(OB11MessageDataType.node),
  data: Type.Object({
    id: Type.String({ description: '转发消息ID' }),
  }),
});
```

#### 内联 node

```ts
const OB11MessageNodeInlineSchema = Type.Object({
  type: Type.Literal(OB11MessageDataType.node),
  data: Type.Object({
    id: Type.Optional(Type.String({ description: '可选：兼容字段' })),
    user_id: Type.Optional(Type.Union([Type.Number(), Type.String()])),
    uin: Type.Optional(Type.Union([Type.Number(), Type.String()])),
    nickname: Type.Optional(Type.String()),
    name: Type.Optional(Type.String()),
    content: Type.Any({ description: '消息内容 (OB11MessageMixType)' }),
    source: Type.Optional(Type.String()),
    news: Type.Optional(Type.Array(Type.Object({ text: Type.String() }))),
    summary: Type.Optional(Type.String()),
    prompt: Type.Optional(Type.String()),
    time: Type.Optional(Type.Union([Type.String(), Type.Number()])),
  }),
});
```

最终导出：

```ts
export const OB11MessageNodeSchema = Type.Union([
  OB11MessageNodeReferenceSchema,
  OB11MessageNodeInlineSchema,
]);
```

### 4.14 验收标准

以下 3 类输入必须被 schema 接受：

1. `id`-only node
2. inline node，只有 `name` 没有 `nickname`
3. inline node，`time` 为 number

### 4.15 必补测试

在 `NapCatQQ/packages/napcat-test/schema.test.ts` 新增：

1. `id`-only node 通过 `OB11MessageDataSchema`
2. inline node with `name` but without `nickname` 通过
3. inline node with numeric `time` 通过

---

## A-04. `set_group_leave.is_dismiss` 是死参数

### 4.16 现状

关键文件：

- [SetGroupLeave.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/group/SetGroupLeave.ts#L7)
- [group.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-core/apis/group.ts#L444)
- [NodeIKernelGroupService.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-core/services/NodeIKernelGroupService.ts#L200)

schema 声称：

- `group_id`
- `is_dismiss`

描述也写了“退出或解散指定群聊”。

但 `_handle()` 实现只有：

```ts
await this.core.apis.GroupApi.quitGroup(payload.group_id.toString());
```

完全不读 `is_dismiss`。

### 4.17 推荐修法

这里**推荐实现功能**，而不是删字段，因为底层服务已经暴露了 `destroyGroup(groupCode)`。

#### 第一步：在 `napcat-core/apis/group.ts` 增加 wrapper

```ts
async destroyGroup (groupCode: string) {
  return this.context.session.getGroupService().destroyGroup(groupCode);
}
```

#### 第二步：在 `SetGroupLeave.ts` 里真正分支

```ts
const isDismiss =
  typeof payload.is_dismiss === 'string'
    ? payload.is_dismiss === 'true'
    : !!payload.is_dismiss;

if (isDismiss) {
  await this.core.apis.GroupApi.destroyGroup(payload.group_id.toString());
} else {
  await this.core.apis.GroupApi.quitGroup(payload.group_id.toString());
}
```

#### 第三步：更新说明

- `actionDescription` 要明确：
  - 普通成员：退出群
  - 群主：`is_dismiss=true` 时解散群

### 4.18 验收标准

1. `is_dismiss=false` 调 `quitGroup`
2. `is_dismiss=true` 调 `destroyGroup`
3. 非群主解散时，错误由底层透出，不要静默吞掉

---

## A-05. `set_doubt_friends_add_request.approve` 是死参数

### 4.19 现状

关键文件：

- [SetDoubtFriendsAddRequest.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/new/SetDoubtFriendsAddRequest.ts#L5)
- [friend.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-core/apis/friend.ts#L105)
- [NodeIKernelBuddyService.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-core/services/NodeIKernelBuddyService.ts#L123)

当前 schema 暴露：

- `flag`
- `approve`

但 action 实现只做：

```ts
return await this.core.apis.FriendApi.handleDoubtFriendRequest(payload.flag);
```

`approve` 完全没用。

### 4.20 推荐修法

这里推荐走“**收缩 public contract**”而不是猜测 reject 语义：

1. 从 schema 移除 `approve`
2. 从 `payloadExample` 移除 `approve`
3. 把 `actionDescription` 从“同意或拒绝”改成“同意/处理可疑好友申请”

原因：

- 当前有明确的 `approvalDoubtBuddyReq`
- 但 reject 语义并没有在 onebot action 层被正确接线
- 盲目把 `approve=false` 接到 `delDoubtBuddyReq` 风险太大，因为当前代码没有证据证明这就是“拒绝”

如果产品要求保留 `approve=false`：

- 先人工验证 `delDoubtBuddyReq(uid)` 的业务语义
- 再决定是否把 `approve=false` 接过去

### 4.21 验收标准

最小一致性修复标准：

1. schema 不再暴露 `approve`
2. example 不再出现 `approve`
3. 文档不再承诺“拒绝”

---

## A-06. `set_group_album_media_like.set` 是死参数

### 4.22 现状

关键文件：

- [SetGroupAlbumMediaLike.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/extends/SetGroupAlbumMediaLike.ts#L5)
- [webapi.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-core/apis/webapi.ts#L503)

schema 暴露了：

- `set: boolean`

但 action 没有读它：

```ts
return await this.core.apis.WebApi.doAlbumMediaLikeByNTQQ(
  payload.group_id,
  payload.album_id,
  payload.lloc,
  payload.id
);
```

底层 `doAlbumMediaLikeByNTQQ()` 还把 `status` 写死成了 `1`。

### 4.23 推荐修法

这里有两个可选修法：

#### 方案 A（推荐，最稳）：删掉 `set`

如果当前版本不支持取消点赞：

1. 从 schema 移除 `set`
2. 删掉代码注释中的“未实现”
3. 文档明确该接口只做“点赞”

#### 方案 B（如果要保留兼容字段）：把 `set` 真正接到底层

1. 给 `doAlbumMediaLikeByNTQQ()` 增加 `set: boolean`
2. 在 `status` 处改为：

```ts
status: set ? 1 : 0
```

3. 补实际联调，确认 `0` 真的是取消点赞

**如果没有联调，不要贸然选方案 B。**

---

## A-07. Stub / 占位 action 必须统一处理

这部分不是单纯“字段少一个”的问题，而是：

- schema
- example
- actionSummary/actionDescription
- `_handle()`

四者之间已经整体失配。

### 4.24 `check_url_safely`

关键文件：

- [GoCQHTTPCheckUrlSafely.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/go-cqhttp/GoCQHTTPCheckUrlSafely.ts#L6)

现状：

- schema 要求 `url`
- `_handle()` 根本不读 `url`
- 永远返回 `{ level: 1 }`

这不是 schema 小问题，而是**功能未实现**。

#### 推荐处理

二选一，只能选一个：

1. **实现真实 URL 安全检查**
2. **明确改成“不支持”**

推荐第二个，因为当前代码库里找不到任何可复用的 URL 安全检查能力。

如果选“不支持”：

- `_handle()` 直接 `throw new Error('当前版本未实现 check_url_safely')`
- 文档/示例同步改成“未实现兼容接口”
- 不要再继续返回假阳性 `{ level: 1 }`

### 4.25 `get_online_clients`

关键文件：

- [GetOnlineClient.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/go-cqhttp/GetOnlineClient.ts#L7)
- [GoCQHTTPActionsExamples.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/example/GoCQHTTPActionsExamples.ts#L58)

现状：

- schema 是空对象
- example 里却有 `no_cache`
- `_handle()` 只是触发 `getOnlineDev()` 然后 `sleep(500)`，最后固定返回 `[]`

#### 推荐处理

如果当前拿不到在线设备列表，建议：

1. 明确标成“兼容占位接口，当前未实现”
2. 删除 example 里的 `no_cache`
3. `_handle()` 改成显式报错，而不是静默返回空数组

### 4.26 `_set_model_show`

关键文件：

- [GoCQHTTPSetModelShow.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/go-cqhttp/GoCQHTTPSetModelShow.ts#L7)
- [GoCQHTTPActionsExamples.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/example/GoCQHTTPActionsExamples.ts#L74)

现状：

- schema 是空对象
- example 仍要求 `model` / `model_show`
- `_handle()` 是空实现

#### 推荐处理

和 `check_url_safely` 一样，不要保留“静默成功”的假实现：

1. 如果没有真实能力，改成显式 `throw new Error('当前版本未实现 _set_model_show')`
2. 如果必须保留 placeholder，则 example 必须改成 `{}`，并在 description 里明确“未实现”

### 4.27 `get_guild_list` / `get_guild_service_profile`

关键文件：

- [GetGuildList.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/guild/GetGuildList.ts#L7)
- [GetGuildProfile.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/guild/GetGuildProfile.ts#L7)
- [GuildActionsExamples.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/example/GuildActionsExamples.ts#L1)

现状：

- 两个 action 都是空 `_handle()`
- schema 都是：
  - payload: `{}`
  - return: `null`
- 但 example 却宣称：
  - `get_guild_list` 返回数组
  - `get_guild_service_profile` 需要 `guild_id`，返回对象

这已经不是 drift，而是**整个 contract 没定义好**。

#### 推荐处理

优先推荐：

1. 先把这两个 action 标成“未实现”
2. `_handle()` 显式抛错
3. schema/example/description 全部与“未实现”状态对齐

只有在确实要做频道能力时，才进入下一阶段：

1. 先定义 payloadSchema / returnSchema
2. 再补 core/api wrapper
3. 最后再写 example

---

## A-08. Example 漂移与文档契约问题

这部分优先级较低，但必须一起清理，否则 AI 和调用方还是会被误导。

### 4.28 `ReceiveOnlineFile`

关键文件：

- [ReceiveOnlineFile.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/file/online/ReceiveOnlineFile.ts#L6)

问题：

- schema 要求：
  - `user_id`
  - `msg_id`
  - `element_id`
- example 却是：
  - `user_id`
  - `msg_id`
  - `save_path`

`save_path` 根本不存在于 schema 和 runtime，`element_id` 反而缺失。

#### 修法

把 example 改成：

```ts
{
  user_id: '123456789',
  msg_id: '123',
  element_id: '456',
}
```

### 4.29 `TestDownloadStream`

关键文件：

- [TestStreamDownload.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/stream/TestStreamDownload.ts#L7)

问题：

- schema 只有 `error`
- example 却是 `url`

#### 修法

把 example 改成：

```ts
{ error: false }
```

### 4.30 `GoCQHTTPGetModelShow`

关键文件：

- [GoCQHTTPGetModelShow.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/go-cqhttp/GoCQHTTPGetModelShow.ts#L12)
- [GoCQHTTPActionsExamples.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/example/GoCQHTTPActionsExamples.ts#L70)

问题：

- `returnSchema` 是 `Type.Array(...)`
- runtime 也返回数组
- 但 example 是单个对象 `{ variants: [] }`

#### 修法

example 改成：

```ts
[
  {
    variants: {
      model_show: 'napcat',
      need_pay: false,
    },
  },
]
```

### 4.31 通用清理规则

建议补一个静态 contract test，规则如下：

1. 若 `payloadSchema = Type.Object({})`，则 `payloadExample` 必须是 `{}` 或 `undefined`
2. 若 `returnSchema = Type.Null()`，则 `returnExample` 必须是 `null`
3. `payloadExample` 的顶层 key 必须是 `payloadSchema` 的子集

---

## A-09. 无参 action 缺失显式空 payload schema

### 4.32 现状

当前至少这两个 action 没有显式 `payloadSchema = Type.Object({})`：

1. [GetVersionInfo.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/system/GetVersionInfo.ts#L13)
2. [MarkMsgAsRead.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-onebot/action/msg/MarkMsgAsRead.ts#L86) 中的 `MarkAllMsgAsRead`

这不会直接影响运行时功能，但会导致：

- action 导出信息不完整
- schema/debug 面板表现不统一

### 4.33 修法

统一加上：

```ts
override payloadSchema = Type.Object({});
```

---

## 5. 修复顺序建议

严格按这个顺序改，返工最少：

1. **先修 A-01**
   - `SendMsgBase.check()` 先恢复 `super.check()`
2. **再修 A-02 / A-03**
   - forward payload schema
   - forward node schema
3. **再修死参数**
   - `is_dismiss`
   - `approve`
   - `set`
4. **再处理 stub/placeholder action**
5. **最后统一清 example/no-arg schema**

原因：

- A-01 是前置基础，不先修，forward 相关测试全会失真
- A-02 / A-03 修完后，发送消息接口的 contract 才稳定
- 其他项 mostly 是 contract cleanup

---

## 6. 必须新增的测试

## 6.1 Schema 层测试

文件建议：

- `NapCatQQ/packages/napcat-test/schema.test.ts`

至少新增：

1. `OB11MessageNodeSchema` 接受 `id`-only node
2. `OB11MessageNodeSchema` 接受只有 `name` 的 inline node
3. `OB11MessageNodeSchema` 接受 numeric `time`
4. `send_forward_msg` action schema 含 `messages`

## 6.2 Action contract 测试

新增文件建议：

- `NapCatQQ/packages/napcat-test/action-contract.test.ts`

至少新增：

1. `send_private_msg` 缺少 `message` 时在 `check()` 失败，不进入 `_handle()`
2. `send_group_msg` 缺少 `group_id` 时在 `check()` 失败
3. `send_forward_msg` 仅提供 `messages` 时可以通过 schema
4. `ReceiveOnlineFile.payloadExample` 包含 `element_id`
5. `GoCQHTTPGetModelShow.returnExample` 是数组

## 6.3 元数据一致性测试

使用 `napcat-schema` 的 `initSchemas()` + `actionSchemas` 做静态检查：

- [napcat-schema/index.ts](/Users/laysath/proj/napcat-sdk/NapCatQQ/packages/napcat-schema/index.ts#L474)

建议新增规则：

1. action 不是 `unknown` 时，`payloadExample` 和 `payloadSchema` 顶层 key 要一致
2. `Type.Null()` 对应 `returnExample === null`
3. 若 action 被注册但 `_handle()` 明显是 placeholder，必须在 description 中出现“未实现”或测试直接失败

---

## 7. 这轮核查中已排除的误报

下面这些经人工复核后，**不算问题**：

1. `GetFriendList.no_cache`
   - 运行时确实使用了，只是参数名叫 `_payload`
2. `GetGroupSystemMsg.count`
   - 运行时确实使用了，只是参数名叫 `params`
3. `UploadFileStream` 的多个字段
   - 运行时通过 destructuring 使用，静态脚本初看像“没读”
4. `GetMiniAppArk` 的联合字段
   - schema 与运行时分支是一一对应的，不是死字段

这意味着本报告里列出的问题，已经做过一次静态筛查 + 源码复核，不是仅靠 grep 猜的。

---

## 8. 修完后的最终验收清单

全部修完后，至少满足下面 12 条：

1. `SendMsgBase.check()` 调用了 `super.check()`
2. `send_msg` / `send_private_msg` / `send_group_msg` 无效入参在校验阶段失败
3. `send_forward_msg*` 的 action schema 导出包含 `messages`
4. `OB11MessageNodeSchema` 接受 `id`-only node
5. `OB11MessageNodeSchema` 不再强制 `nickname`
6. `set_group_leave.is_dismiss` 要么真正实现，要么删掉
7. `set_doubt_friends_add_request.approve` 要么真正实现，要么删掉
8. `set_group_album_media_like.set` 要么真正实现，要么删掉
9. `check_url_safely` 不再假装工作
10. `_set_model_show` / `get_guild_*` 不再 silent no-op
11. `ReceiveOnlineFile` / `TestDownloadStream` / `GoCQHTTPGetModelShow` example 修正
12. `get_version_info` / `_mark_all_as_read` 有显式空 payload schema

---

## 9. 推荐执行命令

在 `NapCatQQ` 根目录执行：

```bash
pnpm --filter napcat-test run test
pnpm typecheck
```

如果把 contract test 独立成新文件，也建议单独跑一遍：

```bash
pnpm --filter napcat-test exec vitest run action-contract.test.ts
```

---

## 10. 一句话修复策略

**先把发送消息链路的 schema 真正接回运行时，再清掉 dead field / stub / example 漂移；不要继续让 action-local schema 和 shared schema 各写各的。**
