---
icon: lucide/bot
---

# MCP 服务器

**MCP (Model Context Protocol)** 是一个开放协议，允许 LLM（大语言模型）通过标准化接口访问外部数据源和工具。NapCat-SDK 内置了 MCP 服务器实现，让 **Claude**、**ChatGPT** 等 AI 助手能够实时查询 SDK 的 API 文档与源代码。

## 1. 什么是 MCP？

MCP 由 Anthropic 提出，旨在解决 AI 应用中的"上下文孤岛"问题。通过 MCP，LLM 可以：

- 🔍 **检索文档**：查询 API 定义、参数类型、返回值结构。
- 📂 **访问代码**：读取源代码文件，理解实现细节。
- 🛠️ **调用工具**：执行预定义的函数（如搜索、计算、数据转换）。

NapCat-SDK 的 MCP 服务器专注于**文档查询场景**，为 AI 提供关于 SDK 本身的"自知识"。

## 2. 快速开始

### 启动 MCP 服务器

NapCat-SDK 提供了命令行工具，一键启动 MCP 服务器：

```bash
napcat-sdk mcp doc
```

服务器会以 **stdio 模式** 运行，通过标准输入输出与 MCP 客户端通信。

> 📌 **stdio 模式**：MCP 服务器不监听网络端口，而是通过标准 I/O 流交换 JSON-RPC 2.0 消息。这是 Claude Desktop 等客户端的默认通信方式。

### 在 Claude Desktop 中配置

编辑 Claude Desktop 的配置文件（位置因平台而异）：

=== "macOS / Linux"
    ```bash
    # ~/.config/claude/config.json
    ```

=== "Windows"
    ```bash
    # %APPDATA%\Claude\config.json
    ```

添加 MCP 服务器配置：

```json
{
  "mcpServers": {
    "napcat-sdk": {
      "command": "napcat-sdk",
      "args": ["mcp", "doc"]
    }
  }
}
```

重启 Claude Desktop 后，它会自动启动 MCP 服务器并与之建立连接。

## 3. 可用工具

MCP 服务器向 LLM 暴露了以下工具，AI 可以自主决定何时调用它们：

### 🔍 `list_apis`

**描述**：列出所有可用的 OneBot API 方法及其简介。

**输入**：无需参数。

**输出**：API 列表，包含方法名和描述。

**示例**：
```json
{
  "send_private_msg": "发送私聊消息",
  "send_group_msg": "发送群消息",
  "get_login_info": "获取登录号信息",
  ...
}
```

**使用场景**：当 AI 不确定有哪些 API 可用时，会首先调用此工具进行探索。

---

### 📖 `get_api_details`

**描述**：获取指定 API 的详细信息，包括函数签名、参数类型、返回值结构。

**输入**：
- `api_name` (string)：API 方法名，如 `"send_group_msg"`

**输出**：包含函数签名、参数定义、返回类型的详细信息。

**示例**：
```python
# 请求
{"api_name": "send_group_msg"}

# 响应
{
  "signature": "async def send_group_msg(group_id: int, message: str | list[MessageSegment], ...) -> dict",
  "parameters": {
    "group_id": "int - 群号",
    "message": "str | list[MessageSegment] - 消息内容"
  },
  "return_type": "dict - 包含 message_id 的字典"
}
```

**使用场景**：当 AI 需要了解某个 API 的具体用法和参数要求时。

---

### 📂 `list_code_files`

**描述**：列出 SDK 源代码的所有文件路径。

**输入**：无需参数。

**输出**：文件路径列表。

**示例**：
```json
[
  "src/napcat/client.py",
  "src/napcat/server.py",
  "src/napcat/connection.py",
  "src/napcat/types/events.py",
  ...
]
```

**使用场景**：当 AI 想要了解 SDK 的代码结构时。

---

### 📄 `get_code_file`

**描述**：读取指定源代码文件的内容。

**输入**：
- `file_path` (string)：文件路径，如 `"src/napcat/client.py"`

**输出**：文件的完整源代码。

**使用场景**：当 AI 需要查看实现细节、调试问题或学习内部机制时。

---

### 🔎 `get_class_definition`

**描述**：查找指定类或函数的定义位置。

**输入**：
- `class_name` (string)：类名或函数名，如 `"NapCatClient"`

**输出**：定义所在的文件路径和行号。

**示例**：
```json
{
  "name": "NapCatClient",
  "file": "src/napcat/client.py",
  "line": 42
}
```

**使用场景**：当 AI 想快速定位某个类或函数的源码位置时。

---

### 📚 `get_llms_txt`

**描述**：获取 SDK 的核心概念与最佳实践文档（llms.txt）。

**输入**：无需参数。

**输出**：包含设计哲学、运行模式、事件处理最佳实践和常用代码模式的文档。

**使用场景**：当 AI 需要理解 SDK 的整体设计理念、推荐的事件处理模式或常见代码模式时。

## 4. 工作原理

### MCP 协议栈

```
┌─────────────────────────┐
│   Claude / ChatGPT      │ ← AI 决策层
└───────────┬─────────────┘
            │ JSON-RPC 2.0
┌───────────▼─────────────┐
│   MCP Client (Desktop)  │ ← 协议层
└───────────┬─────────────┘
            │ stdio
┌───────────▼─────────────┐
│  napcat-sdk mcp doc     │ ← 服务器层
└───────────┬─────────────┘
            │ 文件系统
┌───────────▼─────────────┐
│  SDK 源代码 + 类型定义   │ ← 数据层
└─────────────────────────┘
```

### 通信流程

1. **初始化**：MCP 客户端（如 Claude Desktop）通过 `initialize` 消息握手。
2. **能力协商**：服务器返回支持的协议版本与工具列表。
3. **工具调用**：AI 根据用户问题，决定调用哪个工具。
4. **执行与返回**：服务器执行对应函数（如读取文件），返回结果。
5. **迭代深入**：AI 可能基于首次结果，发起后续调用。

### 示例对话

**用户**：`send_group_msg` 这个 API 怎么用？

**AI 内部流程**：
1. 调用 `get_api_details("send_group_msg")` 获取签名和参数说明。
2. 调用 `get_code_file("src/napcat/client_api.py")` 查看实现。
3. 综合信息生成回答。

**AI 回复**：
> `send_group_msg` 用于发送群消息。主要参数：
> - `group_id` (int)：目标群号
> - `message` (str | list[MessageSegment])：消息内容
> 
> 返回值包含 `message_id`。示例：
> ```python
> await client.send_group_msg(group_id=123456, message="Hello!")
> ```

## 5. 使用场景

### 场景一：AI 辅助开发

在 Claude Desktop 中直接询问 SDK 相关问题，无需手动查文档：

```
你：如何发送带图片的群消息？
AI：（调用 list_apis, get_api_details, get_code_file）
    你可以使用 send_group_msg，消息参数支持 MessageSegment 列表...
```

### 场景二：代码调试

让 AI 分析源码，排查问题：

```
你：为什么我的客户端连接后立即断开？
AI：（调用 get_code_file 查看 connection.py）
    可能是鉴权失败。检查你的 token 是否正确，以及...
```

### 场景三：学习内部机制

通过 AI 理解复杂的设计模式：

```
你：NapCat-SDK 的双流架构是怎么实现的？
AI：（调用 get_class_definition("Connection"), get_code_file）
    在 connection.py 中，event_stream 和 proxy_stream 分别...
```

## 6. 高级配置

### 自定义工具路径

如果你从源码运行，可以使用 uv 运行 CLI 命令：

```json
{
  "mcpServers": {
    "napcat-sdk": {
      "command": "uv",
      "args": ["run", "napcat-sdk", "mcp", "doc"]
    }
  }
}
```

或者使用系统安装的版本：

```json
{
  "mcpServers": {
    "napcat-sdk": {
      "command": "napcat-sdk",
      "args": ["mcp", "doc"]
    }
  }
}
```

> **注意**：旧版模块入口 `python -m napcat.mcp.doc_server` 已迁移到 CLI 命令 `napcat-sdk mcp doc`。

### 日志调试

MCP 服务器的日志会输出到 **stderr**（不影响 stdio 通信），你可以重定向到文件：

```bash
napcat-sdk mcp doc 2> mcp.log
```

### 兼容性

MCP 服务器遵循 **Model Context Protocol 规范 v0.1.0**，理论上兼容所有支持该协议的客户端：

- ✅ Claude Desktop (官方客户端)
- ✅ MCP Inspector (调试工具)
- ⚠️ ChatGPT Desktop (取决于 OpenAI 是否支持 MCP)

## 7. 与其他模式的对比

| 模式 | 用户 | 协议 | 用途 |
|------|------|------|------|
| **Client 模式** | Python 程序 | WebSocket (OneBot) | 与 NapCat 通信，接收事件 |
| **Server 模式** | NapCat | WebSocket (Reverse) | 作为反向 WS 服务端 |
| **RPC 模式** | 外部应用 | WebSocket (自定义) | 跨语言调用 NapCat API |
| **MCP 模式** | AI (Claude/GPT) | JSON-RPC 2.0 (stdio) | 让 AI 查询 SDK 文档 |

## 8. 局限性与未来计划

### 当前局限

- **只读访问**：MCP 服务器仅提供查询功能，不支持修改代码或执行 API。
- **无状态设计**：每次工具调用都是独立的，无法维持上下文（如"记住上次查询的类"）。
- **有限的搜索能力**：暂不支持模糊搜索或语义搜索，AI 需要提供精确的类名/方法名。

### 未来增强

- 🔍 **全文搜索**：支持在源码中搜索关键字或正则表达式。
- 📊 **依赖图谱**：可视化类与类之间的调用关系。
- 🛠️ **代码生成**：基于 API 定义自动生成使用示例。
- 🌐 **HTTP 模式**：支持通过 HTTP 端点暴露工具（适配更多客户端）。

---

## 总结

MCP 服务器让 NapCat-SDK 成为"AI 友好"的项目。通过标准化的协议，AI 助手可以像人类开发者一样查阅文档、理解代码，甚至提供技术支持。

**核心优势：**

1. **无缝集成**：一条命令即可在 Claude Desktop 中启用。
2. **自助查询**：AI 可以自主决定查什么、怎么查，无需人工介入。
3. **实时同步**：源码更新后，AI 立即能看到最新内容。
4. **开发者友好**：不侵入原有代码，纯粹作为文档查询层存在。

**快速上手：**

```bash
# 1. 启动服务器
napcat-sdk mcp doc

# 2. 在 Claude Desktop 配置文件中添加
{
  "mcpServers": {
    "napcat-sdk": {
      "command": "napcat-sdk",
      "args": ["mcp", "doc"]
    }
  }
}

# 3. 重启 Claude Desktop，开始提问！
```

