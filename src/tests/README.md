# Tests 说明

本文档用于记录 `src/tests` 目录下当前测试的职责与运行方式。

## 测试文件清单

### 1) `test_event_deserialize.py`

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

### 2) `test_smoke_imports.py`

**目标**：递归导入 `napcat` 包的全部子模块，确保不存在导入时错误。

说明：
- 这是 pytest 可收集的 smoke test。
- 失败时会汇总导入失败的模块名和异常。

---

### 3) `test_static_checks.py`

**目标**：把静态质量检查纳入测试体系。

包含：
- `ruff check src`
- `pyright`

说明：
- 两个用例都带有 `@pytest.mark.static`。
- 建议本地默认跳过，CI 中按需执行。

---

### 4) `test_message_segments.py`

**目标**：对 `MessageSegment.from_dict(...)` 的消息段反序列化行为做独立、全面测试。

覆盖内容（示例）：
- 已知消息段类型反序列化：`text` / `at` / `reply` / `face` / `image` / `json`
- `music` 段路由验证（当前注册到 `IdMusic`）
- 未知类型兜底：`UnknownMessageSegment`
- 非法 payload 兜底：`data` 非 `dict` 时回落为 `UnknownMessageSegment`
- 缺失必填字段时抛出 `TypeError`
- `__iter__` 输出格式验证（已知段与未知段）

## 常用运行命令

在项目根目录执行：

```bash
# 运行 tests（排除 static 检查）
uv run pytest src/tests -m "not static" -q

# 仅运行事件反序列化测试
uv run pytest src/tests/test_event_deserialize.py -q

# 仅运行 static 检查
uv run pytest src/tests/test_static_checks.py -m static -q

# 仅运行消息段测试
uv run pytest src/tests/test_message_segments.py -q
```
