---
icon: lucide/bot
---

# AI 辅助开发

NapCat-SDK 原生支持 AI 辅助开发。通过 `llms.txt` 和 MCP 服务器，你可以让 AI 助手（如 Claude、Cursor、Copilot 等）深度理解 SDK 并提供精准的代码建议。

## 方式一：使用 llms.txt

[llms.txt](https://llmstxt.org/) 是一个专为 LLM 设计的文档标准。NapCat-SDK 提供了精简的 `llms.txt` 文件，包含核心概念、最佳实践和常用代码模式。

### 获取地址

```
https://faithleysath.github.io/napcat-sdk/llms.txt
```

### 使用方法

**Claude / ChatGPT 对话**

直接在对话中提供链接，AI 会自动获取：

```
请阅读 https://faithleysath.github.io/napcat-sdk/llms.txt 并帮我写一个群消息复读机
```

**Cursor / Windsurf**

在项目根目录创建 `.cursorrules` 或 `.windsurfrules`：

```
@https://faithleysath.github.io/napcat-sdk/llms.txt
```

**Copilot**

在 `.github/copilot-instructions.md` 中添加：

```markdown
参考文档：https://faithleysath.github.io/napcat-sdk/llms.txt
```

---

## 方式二：MCP 服务器（推荐）

MCP（Model Context Protocol）让 AI 能够**实时查询** SDK 的 API 定义和源代码，获得最准确的上下文。

### Claude Code 配置

在 `~/.claude/settings.json` 或项目的 `.claude/settings.local.json` 中添加：

```json
{
  "mcpServers": {
    "napcat-sdk": {
      "command": "uvx",
      "args": ["--from", "napcat-sdk", "napcat-sdk", "mcp", "doc"]
    }
  }
}
```

### Claude Desktop 配置

编辑 Claude Desktop 配置文件：

=== "macOS / Linux"
    ```bash
    ~/.config/claude/config.json
    ```

=== "Windows"
    ```bash
    %APPDATA%\Claude\config.json
    ```

添加 MCP 服务器：

```json
{
  "mcpServers": {
    "napcat-sdk": {
      "command": "uvx",
      "args": ["--from", "napcat-sdk", "napcat-sdk", "mcp", "doc"]
    }
  }
}
```

### Cursor / Windsurf 配置

在 `.cursor/mcp.json` 或 `.windsurf/mcp.json` 中：

```json
{
  "mcpServers": {
    "napcat-sdk": {
      "command": "uvx",
      "args": ["--from", "napcat-sdk", "napcat-sdk", "mcp", "doc"]
    }
  }
}
```

### 可用的 MCP 工具

配置完成后，AI 可以调用以下工具：

| 工具 | 功能 |
|------|------|
| `list_apis` | 列出所有可用 API 及简介 |
| `get_api_details` | 获取指定 API 列表（`names`）的参数和返回值 |
| `list_code_files` | 列出 SDK 源代码文件 |
| `get_code_file` | 读取指定源代码文件（`paths`） |
| `get_class_definition` | 查询指定类列表（`names`）的定义源码 |
| `get_llms_txt` | 获取核心概念与最佳实践文档 |

---

## 推荐工作流

**最佳实践**：同时使用 `llms.txt` + MCP 服务器

```
┌─────────────────┐     ┌─────────────────┐
│   llms.txt      │     │   MCP Server    │
│  (核心概念)      │     │  (API 详情)     │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │
                     ▼
              ┌─────────────┐
              │  AI 助手    │
              │  (Claude)   │
              └─────────────┘
```

1. **llms.txt** 提供 SDK 的设计哲学、核心概念、最佳实践
2. **MCP 服务器** 提供实时 API 查询和源代码访问

这样 AI 既能理解"怎么写"（模式匹配、事件处理），也能查询"写什么"（具体 API 参数）。

---

## 示例对话

配置完成后，你可以这样与 AI 对话：

**问**：帮我写一个群消息关键词回复机器人

**AI**：（读取 llms.txt 理解模式匹配最佳实践，调用 MCP 查询 `send_group_msg` API）

```python
from napcat import NapCatClient, GroupMessageEvent, Text

async with NapCatClient(ws_url="ws://127.0.0.1:3000", token="xxx") as client:
    async for event in client:
        if isinstance(event, GroupMessageEvent):
            match event.raw_message:
                case "hello":
                    await event.reply("Hello!")
                case "ping":
                    await event.reply("pong")
```

---

## 故障排除

### uvx 命令找不到

确保已安装 [uv](https://docs.astral.sh/uv/)：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### MCP 服务器无法启动

检查 napcat-sdk 是否正确安装：

```bash
uvx --from napcat-sdk napcat-sdk mcp doc
```

### Claude Code 不识别 MCP 配置

确保 JSON 格式正确，且文件路径正确：
- 全局配置：`~/.claude/settings.json`
- 项目配置：`.claude/settings.local.json`
