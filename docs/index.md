---
icon: lucide/rocket
---

# NapCat-SDK 文档

NapCat-SDK 是面向 NapCat / OneBot 协议的 Python SDK，主打 **完整类型覆盖**、**原生 asyncio** 与 **零框架约束**。你可以用它快速编写机器人逻辑，同时享受 IDE 级别的参数提示与自动补全。

## 为什么选择 NapCat-SDK

- **完整类型覆盖**：所有事件、消息段、API 都有类型定义，补全体验一流。
- **纯异步**：基于 `websockets` + `asyncio`，轻量且性能优秀。
- **双模式**：既能主动连接 NapCat（Client 模式），也能作为反向 WebSocket 服务端（Server 模式）。
- **低依赖**：只依赖 `websockets` 与 `orjson`，安装快、体积小。

## 你将学到什么

- 如何在 5 分钟内启动你的第一个 NapCat 机器人
- 如何监听消息事件并发送富媒体消息
- 如何调用 OneBot API，并优雅处理扩展接口
- 如何在 Server 模式下提供反向 WebSocket 服务

## 下一步

- 阅读 **[快速开始](getting-started.md)**，完成第一个可运行的 Bot。
- 了解 **[Client 模式](client-mode.md)** 与 **[Server 模式](server-mode.md)** 的差异。
- 学习 **[事件与消息](events-messages.md)**，高效构建消息处理逻辑。
- 查看 **[API 调用](api-usage.md)**，了解强类型 API 的使用方式。

---

> 提示：如果你想直接浏览完整示例与截图，可参考项目 README。该文档更偏向结构化学习与上手。
