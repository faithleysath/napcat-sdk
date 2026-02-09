---
icon: lucide/rocket
---

<div align="center" style="display:flex; flex-direction: column; align-items: center;">

  <img src="img/logo.png" width="250" height="200" alt="NapCat Logo" />

  <h1 align="center" style="margin-bottom: 0.5em;">
    NapCat-SDK for Python
  </h1>

  <div align="center">
    <b>Type-Safe</b> • <b>Async-Ready</b> • <b>Framework-Free</b>
  </div>

  <p>
    <a href="https://pypi.org/project/napcat-sdk/">
        <img src="https://img.shields.io/pypi/v/napcat-sdk?style=flat-square&color=006DAD&label=PyPI" alt="PyPI">
    </a>
    <a href="https://github.com/faithleysath/napcat-sdk/blob/main/LICENSE">
        <img src="https://img.shields.io/github/license/faithleysath/napcat-sdk?style=flat-square&color=blueviolet" alt="License">
    </a>
    <img src="https://img.shields.io/badge/Python-3.12+-FFE873?style=flat-square&logo=python&logoColor=black" alt="Python Version">
    <img src="https://img.shields.io/badge/Typing-Strict-22c55e?style=flat-square" alt="Typing">
  </p>

  <div>
    <a href="https://zread.ai/faithleysath/napcat-sdk" target="_blank"><img src="https://img.shields.io/badge/Ask_Zread-_.svg?style=flat&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff" alt="zread"/></a>
    <a href="https://deepwiki.com/faithleysath/napcat-sdk">
        <img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki">
    </a>
    <img src="https://img.shields.io/badge/QQ%E7%BE%A4-819085771-54a3ff?style=flat-square&logo=tencent-qq&logoColor=white" alt="QQ Group">
  </div>

  <h3 style="margin-top: 0.5em;">Stop guessing parameter types. Let the IDE do the work.</h3>
  <div>告别查文档，享受 <b>100% 类型覆盖</b> 带来的极致补全体验。</div>
</div>

---

NapCat-SDK 是面向 NapCat / OneBot 协议的 Python SDK，主打 **完整类型覆盖**、**原生异步** 与 **零框架约束**。你可以用它快速编写机器人逻辑，同时享受 IDE 级别的参数提示与自动补全。

## 为什么选择 NapCat-SDK

- **完整类型覆盖**：所有事件、消息段、API 都有类型定义，补全体验一流。
- **纯异步**：基于 `websockets` + `asyncio`，轻量且性能优秀。
- **双模式**：既能主动连接 NapCat（Client 模式），也能作为反向 WebSocket 服务端。
- **上游同步**：基于代码生成链路，零时差跟进上游 Schema 与 API 变更。

## 你将学到什么

- 如何在 5 分钟内启动你的第一个 NapCat 机器人
- 如何监听消息事件并发送富媒体消息
- 如何调用 OneBot API，并优雅处理扩展接口
- 如何在 Server 模式下提供反向 WebSocket 服务

## 下一步

- 阅读 **[快速开始](./getting-started/first-bot.md)**，完成第一个可运行的 Bot。
- 了解 **[Client 模式](./key-concept/client.md)** 与 **[Server 模式](./key-concept/server.md)** 的差异。
- 学习 **[事件与消息](./key-concept/events-messages.md)**，高效构建消息处理逻辑。
- 查看 **[API 调用](./api-usage.md)**，了解强类型 API 的使用方式。

---

> 提示：如果你在使用过程中遇到任何问题，欢迎加入 QQ 群或在 GitHub 上提交 issue！
