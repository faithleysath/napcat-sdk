<div align="center">
  <img src="https://raw.githubusercontent.com/faithleysath/napcat-sdk/refs/heads/main/docs/img/logo.png" width="250" height="200" alt="NapCat Logo">

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

  <p>
    <a href="https://zread.ai/faithleysath/napcat-sdk" target="_blank"><img src="https://img.shields.io/badge/Ask_Zread-_.svg?style=flat&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff" alt="zread"/></a>
    <a href="https://deepwiki.com/faithleysath/napcat-sdk">
        <img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki">
    </a>
    <a href="https://faithleysath.github.io/napcat-sdk/">
        <img src="https://img.shields.io/badge/Docs-📖-blue?style=flat-square&color=2986cc" alt="Documentation">
    </a>
    <img src="https://img.shields.io/badge/QQ%E7%BE%A4-819085771-54a3ff?style=flat-square&logo=tencent-qq&logoColor=white" alt="QQ Group">
  </p>

  <h3>Stop guessing parameter types. Let the IDE do the work.</h3>
  <p>告别查文档，享受 <b>100% 类型覆盖</b> 带来的极致补全体验。</p>
</div>

---


## ✨ Features

- 🔄 **协议自动同步**: 基于 OpenAPI 自动构建，与 NapCat 上游定义零时差同步。
- 🧘 **原生无框架**: 拒绝框架"黑魔法"，纯粹 Python 语法，零心智负担。
- 💎 **极致类型**: 100% 类型覆盖，每一个参数都有定义，享受极致 IDE 补全。
- ⚡ **完全异步**: 基于 `websockets` + `asyncio` 原生开发，无惧高并发。
- 🔌 **双模支持**: 完美支持正向 (Client) 与反向 (Server) WebSocket 连接。
- 🌐 **远程 RPC**: 内置透明网关，让外部应用跨语言调用 NapCat API。
- 🤖 **CLI 集成**: 支持 MCP、Skills、CLI，让 AI 助手实时查询 SDK 文档。
- 📦 **极轻量级**: 仅依赖 `websockets` 和 `orjson`，极速安装，拒绝臃肿。

---

## 📦 Installation

```bash
uv add napcat-sdk
# or
pip install napcat-sdk
```

---

## 🤖 CLI

CLI 是自举的：只要记住入口 `uv run napcat-sdk`（安装后也可以直接用 `napcat-sdk`），其余用法都可以从命令本身继续发现。

```bash
uv run napcat-sdk --help
uv run napcat-sdk tldr
uv run napcat-sdk doc agent
uv run napcat-sdk doc agent --full --with-code
uv run napcat-sdk mcp doc
```

它适合做三件事：管理本地实例、查询 SDK/API 文档、给 AI agent 一次性导出大上下文文档包。

---

## 📸 Quick Look

```python
import asyncio
from napcat import NapCatClient, GroupMessageEvent, PrivateMessageEvent

async def listen_private(client: NapCatClient):
    print(">> 私聊监听启动")
    async for event in client:
        match event:
            case PrivateMessageEvent():
                print(f"[私信] {event.sender.nickname}: {event.raw_message}")
                await event.send_msg("已阅")
            case _:
                pass

async def listen_group(client: NapCatClient):
    print(">> 群聊监听启动")
    async for event in client:
        match event:
            case GroupMessageEvent():
                print(f"[群消息] {event.group_id}: {event.raw_message}")
                await event.reply("复读")
            case _:
                pass

async def main():
    # 正向 WebSocket 连接（支持自动管理上下文）
    client = NapCatClient(ws_url="ws://localhost:3001", token="123")
    await asyncio.gather(
        listen_private(client),
        listen_group(client)
    )

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📖 Usage

`NapCatClient` 支持直接作为异步迭代器使用，并会在迭代开始/结束时自动管理连接生命周期。

<details> <summary><b>🔌 反向 WebSocket 服务端 (Server Mode)</b></summary>

如果你配置 NapCat 主动连接你的程序，请使用 `ReverseWebSocketServer`。

```python
import asyncio
from napcat import ReverseWebSocketServer, NapCatClient, GroupMessageEvent

async def handler(client: NapCatClient):
    """每个新的 WebSocket 连接都会触发此回调"""
    print(f"Bot Connected! Self ID: {client.self_id}")
    
    # 就像 Client 模式一样处理事件
    async for event in client:
        if isinstance(event, GroupMessageEvent):
            print(f"收到群 {event.group_id} 消息: {event.raw_message}")
            await event.reply("服务端已收到")

async def main():
    # 启动服务器监听 8080 端口
    server = ReverseWebSocketServer(handler, host="0.0.0.0", port=8080, token="my-token")
    await server.run_forever()

if __name__ == "__main__":
    asyncio.run(main())
```

</details>

<details> <summary><b>🖼️ 发送富媒体消息 (图片/At/回复)</b></summary>

SDK 提供了强类型的 `MessageSegment`，告别手动拼接 CQ 码。

```python
from napcat import (
    NapCatClient,
    Text,
    Image,
    At,
)

async def send_rich_media(client: NapCatClient, group_id: int):
    # 构建消息链：@某人 + 文本 + 图片
    message = [
        At(qq="12345678"),
        Text(text=" 来看这张图："),
        Image(file="https://example.com/image.jpg"),
    ]
    
    # 直接发送列表
    await client.send_group_msg(group_id=group_id, message=message)
```

</details>

<details> <summary><b>🔗 调用 OneBot API (100% 类型提示)</b></summary>

所有 API 方法都直接挂载在 `client` 上，拥有完整的参数类型检查。

```python
async def managing_bot(client: NapCatClient):
    # 获取登录号信息
    login_info = await client.get_login_info()
    print(f"当前登录: {login_info['nickname']}")

    # 获取群成员列表
    members = await client.get_group_member_list(
        group_id=123456, 
        no_cache=True
    )
    for member in members:
        print(f"成员: {member['card'] or member['nickname']}")
    
    # 动态调用（针对未收录的 API）
    await client.call_action("some_new_action", {"param": 1})
```

</details>

<details> <summary><b>⚠️ 错误处理 (异常类型)</b></summary>

SDK 提供了明确的异常类型，方便区分错误来源：

```python
from napcat import NapCatAPIError, NapCatProtocolError, NapCatStateError

try:
    await client.get_login_info()
except NapCatAPIError as exc:
    print("API 失败:", exc)
    print("action=", exc.action, "retcode=", exc.retcode)
except NapCatProtocolError as exc:
    print("上报数据异常:", exc)
except NapCatStateError as exc:
    print("客户端状态错误:", exc)
```

</details>

---

## 🛠️ Development

本项目使用 [uv](https://github.com/astral-sh/uv) 进行包管理。

1. **克隆项目并同步环境**:
```
git clone --recursive https://github.com/faithleysath/napcat-sdk.git
cd napcat-sdk
uv sync
corepack enable
corepack prepare pnpm@latest --activate
cd NapCatQQ
pnpm install --frozen-lockfile
cd ..
```

2. **同步协议定义**: SDK 的核心代码由 OpenAPI 规范自动生成，请运行以下命令重新生成代码：
```
uv run scripts/schema-codegen.py
```
*这会自动更新 `src/napcat/types/messages/generated.py`、`src/napcat/types/schemas.py`、`src/napcat/client_api.py` 以及相关的 `__init__.py`。如果你的环境里没有全局 `pnpm`，请先在 `NapCatQQ` 中执行 `corepack pnpm --filter napcat-schema run build:openapi`，然后改用 `uv run scripts/schema-codegen.py --no-openapi-pre-codegen`。*

3. **如需同步 `notice` 事件定义**:
```
OPENAI_API_KEY=你的key uv run scripts/notice-codegen.py
uv run scripts/update-init.py
```
*脚本默认已经配置好 Google 的 OpenAI-compatible `base_url` 和模型；通常只需要传 `OPENAI_API_KEY`。*

4. **运行测试**:
```
# 运行 tests
uv run pytest src/tests -q
```

---

## 📄 License

MIT License © 2025 [faithleysath](https://github.com/faithleysath)

<a href="https://star-history.com/#faithleysath/napcat-sdk&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=faithleysath/napcat-sdk&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=faithleysath/napcat-sdk&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=faithleysath/napcat-sdk&type=Date" />
 </picture>
</a>
