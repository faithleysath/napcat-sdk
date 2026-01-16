<div align="center">
  <img src="https://raw.githubusercontent.com/faithleysath/napcat-sdk/refs/heads/main/img/logo.png" width="250" height="200" alt="NapCat Logo">

  # NapCat-SDK for Python

  <p align="center">
    <b>Type-Safe</b> • <b>Async-Ready</b> • <b>Framework-Free</b>
  </p>

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

  <h3>Stop guessing parameter types. Let the IDE do the work.</h3>
  <p>告别查文档，享受 <b>100% 类型覆盖</b> 带来的极致补全体验。</p>
</div>

---

## ⚡ The "IDE Magic"

这就是为什么你应该选择 NapCat-SDK：

| **智能 API 补全 + 精准参数提示** | **原生开发体验 + 零心智负担** |
| :---: | :---: |
| ![API Completion](https://raw.githubusercontent.com/faithleysath/napcat-sdk/refs/heads/main/img/api-completion.gif) | ![Native Dev](https://raw.githubusercontent.com/faithleysath/napcat-sdk/refs/heads/main/img/native-dev.gif) |

> 👆 真正的 **140+ API** 全量类型覆盖，每一次按键都有 IDE 的守护。

---

## ✨ Features

- 🔄 **协议自动同步**: 基于 OpenAPI 自动构建，与 NapCat 上游定义零时差同步。
- 🧘 **原生无框架**: 拒绝框架“黑魔法”，纯粹 Python 语法，零心智负担。
- 💎 **极致类型**: 100% 类型覆盖，每一个参数都有定义，享受极致 IDE 补全。
- ⚡ **完全异步**: 基于 `websockets` + `asyncio` 原生开发，无惧高并发。
- 🔌 **双模支持**: 完美支持正向 (Client) 与反向 (Server) WebSocket 连接。
- 📦 **极轻量级**: 仅依赖 `websockets` 与 `orjson`，极速安装，拒绝臃肿。

---

## 📸 Quick Look

<div align="center">
  <img src="https://raw.githubusercontent.com/faithleysath/napcat-sdk/refs/heads/main/img/code-snapshot.png" alt="Code Example" width="800">
</div>

<details>
<summary><b>🖱️ 点击复制代码文本</b></summary>

```python
import asyncio
from napcat import NapCatClient, GroupMessageEvent, PrivateMessageEvent

# --- 消费者 A: 监听私聊 ---
async def listen_private(client: NapCatClient):
    print(">> 私聊监听启动")
    # 独立的 async for，享受完整的事件流副本
    async for event in client.events():
        match event:
            case PrivateMessageEvent():
                print(f"[私信] {event.sender.nickname}: {event.raw_message}")
                await event.send_msg("已阅")
            case _:
                pass

# --- 消费者 B: 监听群聊 ---
async def listen_group(client: NapCatClient):
    print(">> 群聊监听启动")
    # 另一个独立的 async for，互不抢占
    async for event in client.events():
        match event:
            case GroupMessageEvent():
                print(f"[群消息] {event.group_id}: {event.raw_message}")
                await event.reply("复读")
            case _:
                pass

async def main():
    # 正向 WebSocket 连接
    async with NapCatClient(ws_url="ws://localhost:80", token="123") as client:
        # 关键点：使用 gather 同时运行多个消费者
        await asyncio.gather(
            listen_private(client),
            listen_group(client)
        )

if __name__ == "__main__":
    asyncio.run(main())
```
</details>

---

## 📦 Installation

```bash
uv add napcat-sdk
# or
pip install napcat-sdk
```