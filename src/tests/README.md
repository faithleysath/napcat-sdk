# Tests 说明

本文档用于记录 `src/tests` 目录下当前测试的职责与运行方式。

## 测试文件清单

### 1) `test_client_connection_server.py`

**目标**：验证客户端连接生命周期、请求发送、事件迭代、反向 WebSocket 服务端和常用便捷方法的行为。

覆盖内容（示例）：
- `NapCatClient` 的异步上下文与迭代生命周期
- 请求响应匹配、超时、错误响应转换
- 连接关闭、清理异常、后台任务回收
- `ReverseWebSocketServer` 的连接接入与任务清理
- 事件绑定后调用 `reply` / `send_msg` 等方法
- `event_match` 与消息节点相关的集成场景

---

### 2) `test_event_deserialize.py`

**目标**：验证事件类反序列化入口 `NapCatEvent.from_dict(...)` 的路由与兜底行为。

覆盖内容（示例）：
- `notice` 路由
  - `group_upload`（嵌套 `GroupUploadFile`）
  - `group_msg_emoji_like`（嵌套 `likes` 列表）
  - `notify/poke` 的好友/群路由
  - 未知 `notice_type` -> `UnknownNoticeEvent`
- `message` 路由
  - `private` -> `PrivateMessageEvent`
  - `group` -> `GroupMessageEvent`
  - 未知 `message_type` / 非法 sender -> `UnknownEvent`
- `meta_event` 路由
  - `lifecycle` -> `LifecycleMetaEvent`
  - `heartbeat` -> `HeartbeatEvent`
  - 非法 `status` -> `UnknownEvent`
- `request` 路由
  - `friend` -> `FriendRequestEvent`
  - `group` -> `GroupRequestEvent`
  - 未知 `request_type` -> `UnknownEvent`
- 顶层兜底
  - 非法 `post_type` / 未注册 `post_type` -> `UnknownEvent`

---

### 3) `test_event_serialize.py`

**目标**：验证事件对象序列化、绑定客户端后的上下文注入，以及未知事件的往返行为。

覆盖内容（示例）：
- 私聊、群聊、好友请求事件的 `to_dict()` 往返一致性
- `bind(...)` 返回自身并保存客户端引用
- `NapCatEvent.from_dict(..., client=...)` 的绑定行为
- `_rpc` 元信息的注入、提取与清理
- 序列化结果保持原始 payload 的关键字段

---

### 4) `test_matcher.py`

**目标**：验证事件匹配器 `event_match(...)` 的字段匹配、嵌套匹配和组合能力。

覆盖内容（示例）：
- 顶层标量字段匹配
- 嵌套 dataclass / mapping 字段匹配
- callable 条件匹配
- 多事件类型匹配
- `TRUE` / `FALSE` 与 `&` / `|` 组合
- 非法事件类型参数校验

---

### 5) `test_message_segments.py`

**目标**：对 `MessageSegment.from_dict(...)` 的消息段反序列化行为做独立、全面测试。

覆盖内容（示例）：
- 已知消息段类型反序列化：`text` / `at` / `reply` / `face` / `image` / `json`
- `music` 段路由验证（当前注册到 `IdMusic`）
- 未知类型兜底：`UnknownMessageSegment`
- 非法 payload 兜底：`data` 非 `dict` 时回落为 `UnknownMessageSegment`
- 缺失必填字段时抛出 `TypeError`
- `__iter__` 输出格式验证（已知段与未知段）

---

### 6) `test_smoke_imports.py`

**目标**：递归导入 `napcat` 包的全部子模块，确保不存在导入时错误。

说明：
- 这是 pytest 可收集的 smoke test。
- 失败时会汇总导入失败的模块名和异常。

---

### 7) `test_static_checks.py`

**目标**：把静态质量检查纳入测试体系。

包含：
- `ruff check src`
- `pyright`

说明：
- 两个用例都带有 `@pytest.mark.static`。
- 建议本地默认跳过，CI 中按需执行。

---

## 常用运行命令

在项目根目录执行：

```bash
# 运行 tests（排除 static 检查）
uv run pytest src/tests -m "not static" -q

# 仅运行事件反序列化测试
uv run pytest src/tests/test_event_deserialize.py -q

# 仅运行事件序列化测试
uv run pytest src/tests/test_event_serialize.py -q

# 仅运行事件匹配器测试
uv run pytest src/tests/test_matcher.py -q

# 仅运行 static 检查
uv run pytest src/tests/test_static_checks.py -m static -q

# 仅运行消息段测试
uv run pytest src/tests/test_message_segments.py -q
```
