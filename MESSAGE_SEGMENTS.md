# NapCat 消息段类型汇总

## 概述
根据 OpenAPI schema 定义，NapCat 支持以下消息段类型。目前 `messages.py` 中已实现 7 种，还需要实现 11 种。

## 已实现的消息段 ✓

### 1. text - 文本消息
**类型**: `TextMessageSegment`
```python
- text: str
```

### 2. reply - 回复消息
**类型**: `ReplyMessageSegment`
```python
- id: int
```

### 3. image - 图片消息
**类型**: `ImageMessageSegment`
```python
- file: str (必需)
- sub_type: ImageSubType = ImageSubType.NORMAL
  - 0: 普通图片
  - 1: 表情包/斗图
- url: str | None = None
- file_size: int | None = None
```

### 4. video - 视频消息
**类型**: `VideoMessageSegment`
```python
- file: str (必需)
- url: str | None = None
- file_size: int | None = None
```

### 5. file - 文件消息
**类型**: `FileMessageSegment`
```python
- file: str (必需)
- file_id: str (必需)
- url: str | None = None (私聊没有，群聊有)
```

### 6. at - @消息
**类型**: `AtMessageSegment`
```python
- qq: int | Literal["all"]
```

### 7. forward - 转发消息
**类型**: `ForwardMessageSegment`
```python
- id: str
```

---

## 待实现的消息段 ✗

### 8. face - 表情
**描述**: QQ 内置表情
```json
- id: string (必需) - 表情ID
- resultId: string (可选)
- chainCount: number (可选)
```

### 9. mface - 商城表情
**描述**: 购买的表情包
```json
- emoji_package_id: number (必需)
- emoji_id: string (必需)
- key: string (必需)
- summary: string (必需)
```

### 10. poke - 戳一下
**描述**: 戳消息
```json
- type: string (必需)
- id: string (必需)
```

### 11. contact - 联系人
**描述**: 分享联系人
```json
- type: string (必需)
- id: string (必需)
```

### 12. record - 语音消息
**描述**: 语音/音频
```json
- file: string (必需)
- path: string (可选)
- thumb: string (可选)
- name: string (可选)
- url: string (可选)
```

### 13. node - 合并转发节点
**描述**: 合并转发中的单个节点
```json
- id: string (可选)
- user_id: number | string (可选)
- uin: number | string (可选, go-cqhttp 兼容)
- nickname: string (必需)
- name: string (可选, go-cqhttp 兼容)
- content: MessageMixType (必需)
- time: string (可选)
- news: Array<{text: string}> (必需)
- source: string (必需) - 顶部标题
- summary: string (必需) - 底部文本
- prompt: string (必需) - 外显文本
```

### 14. music - 音乐分享
**描述**: 音乐卡片
```json
# 模式1: 仅指定平台和ID
- type: "qq" | "163" | "kugou" | "migu" | "kuwo" (必需)
- id: number | string (必需)

# 模式2: 自定义音乐
- type: "qq" | "163" | "kugou" | "migu" | "kuwo" | "custom" (必需)
- id: number | string (必需)
- url: string (必需)
- image: string (必需)
- audio: string (可选)
- title: string (可选)
- content: string (可选)
```

### 15. json - JSON卡片
**描述**: JSON 格式的卡片消息
```json
- data: string | object (必需)
- config.token: string (可选)
```

### 16. dice - 骰子
**描述**: 骰子消息
```json
- result: number | string (必需)
```

### 17. rps - 猜拳
**描述**: 猜拳（石头、剪刀、布）
```json
- result: number | string (必需)
```

### 18. markdown - Markdown 消息
**描述**: Markdown 格式消息
```json
- content: string (必需)
```

---

## 文件格式说明

### file 字段格式
- **接收时**: 通常是 MD5 值 + 扩展名 (如 `abc123.jpg`, `xyz789.mp4`)
- **发送时**: 支持多种格式
  - 本地文件: `file://D:/path/to/file.jpg`
  - 网络链接: `http://example.com/image.png`
  - Base64: `base64://xxxxxxxx`

---

## 消息数据类结构

每个消息段类型都由以下部分组成:

1. **DataClass**: `XXXData` - dataclass，存储消息段的实际数据
2. **TypeClass**: `XXXDataType` - TypedDict，用于类型提示
3. **SegmentClass**: `XXXMessageSegment` - 消息段主类，继承 `MessageSegment`

### 自动注册机制
- 所有 `MessageSegment` 子类会通过 `__init_subclass__` 自动注册到 `MessageSegment._registry` 中
- 通过 `type` 类变量作为 key
- 支持从字典动态解析为对应的消息段类型

---

## 实现优先级建议

1. **高优先级** (常用):
   - face (表情)
   - record (语音)
   - node (合并转发节点)
   - music (音乐)

2. **中优先级** (需要):
   - mface (商城表情)
   - contact (联系人)
   - poke (戳)

3. **低优先级** (功能性):
   - json (JSON卡片)
   - dice (骰子)
   - rps (猜拳)
   - markdown (Markdown)

