---
icon: lucide/wrench
---

# 开发指南

如果你准备同步上游 `NapCatQQ`、重新生成 SDK 类型，或者维护 `notice` 事件，可以直接照下面的流程执行。

## 一次性准备

### 需要的工具

- [uv](https://github.com/astral-sh/uv)
- Git
- Node.js
- Corepack

建议先确认工具可用：

```bash
uv --version
git --version
node --version
corepack --version
```

## 从 GitHub 克隆仓库

首次克隆请带上 `--recursive`，这样会把 `NapCatQQ` 子模块一起拉下来：

```bash
git clone --recursive https://github.com/faithleysath/napcat-sdk.git
cd napcat-sdk
```

如果你以前已经克隆过仓库，但当时没有加 `--recursive`，补这一条即可：

```bash
git submodule update --init --recursive
```

## 初始化本地环境

先同步 Python 依赖，再准备 `pnpm` 和子模块依赖：

```bash
uv sync

corepack enable
corepack prepare pnpm@latest --activate
pnpm -v

cd NapCatQQ
pnpm install --frozen-lockfile
cd ..
```

如果你不想全局激活 `pnpm`，也可以只在当前命令前加 `corepack`。不过要注意：`scripts/schema-codegen.py` 的默认流程内部会直接调用裸 `pnpm`，所以没有全局 `pnpm` 时，需要走下面文档里的“兼容写法”。

## 日常同步流程

下面这套流程适合“我刚把 `NapCatQQ` 拉到最新，接下来同步 SDK”的场景。

### 1. 更新 `NapCatQQ` 子模块

```bash
cd NapCatQQ
git checkout main
git pull --ff-only origin main
cd ..
```

如果你是从顶层仓库里更新子模块指针，也可以先看一下当前状态：

```bash
git status
git submodule status
```

### 2. 重新生成 OpenAPI 和 SDK 类型

如果你的环境里已经能直接调用 `pnpm`，最简单的方式就是：

```bash
uv run scripts/schema-codegen.py
```

这条命令会自动完成：

- 在 `NapCatQQ` 中执行 `pnpm run build:openapi`
- 重新生成 SDK 的类型和 API 包装
- 更新相关的 `__init__.py`

通常会改动这些文件：

- `src/napcat/types/messages/generated.py`
- `src/napcat/types/schemas.py`
- `src/napcat/client_api.py`
- `src/napcat/types/messages/__init__.py`
- `src/napcat/types/events/__init__.py`
- `src/napcat/types/__init__.py`
- `src/napcat/__init__.py`

如果你的机器没有全局 `pnpm`，用下面这组兼容写法：

```bash
cd NapCatQQ
corepack pnpm --filter napcat-schema run build:openapi
cd ..

uv run scripts/schema-codegen.py --no-openapi-pre-codegen
```

### 3. 重新生成 `notice` 事件（需要 LLM）

`notice` 事件类由 `scripts/notice-codegen.py` 生成。现在脚本默认已经配置好了 Google 的 OpenAI-compatible 端点和模型，所以大多数情况下只需要传 `OPENAI_API_KEY`：

```bash
OPENAI_API_KEY=你的key uv run scripts/notice-codegen.py
uv run scripts/update-init.py
```

这一步通常会更新：

- `src/napcat/types/events/notice/*.py`
- `src/napcat/types/events/notice/__init__.py`
- `src/napcat/types/events/__init__.py`
- `src/napcat/types/__init__.py`
- `src/napcat/__init__.py`

如果你要换成别的兼容服务，再手动覆盖：

```bash
OPENAI_API_KEY=你的key \
OPENAI_BASE_URL=https://your-openai-compatible-endpoint/v1 \
OPENAI_MODEL_NAME=your-model \
uv run scripts/notice-codegen.py
```

### 4. 运行测试

```bash
uv run pytest src/tests -q
```

同步完成后，建议再看一眼变更范围：

```bash
git status
git diff --stat
```

## 提交流程

确认变更符合预期后提交。最常见的是顶层仓库记录以下几类变更：

- `NapCatQQ` 子模块指针
- `schemas.py` / `generated.py` / `client_api.py`
- `notice` 事件生成文件
- 上层聚合导出文件

一个常用提交流程如下：

```bash
git add NapCatQQ \
  src/napcat/client_api.py \
  src/napcat/types/messages/generated.py \
  src/napcat/types/schemas.py \
  src/napcat/types/events/notice \
  src/napcat/types/events/__init__.py \
  src/napcat/types/__init__.py \
  src/napcat/__init__.py

git commit -m "chore: sync SDK with NapCatQQ"
git push origin main
```

如果这次没有跑 `notice-codegen.py`，就把 `notice` 相关文件从 `git add` 里去掉即可。

## 常见问题

### 克隆时忘了加 `--recursive`

直接执行：

```bash
git submodule update --init --recursive
```

### 只有 `npm`，没有 `pnpm`

优先使用：

```bash
corepack enable
corepack prepare pnpm@latest --activate
```

如果你不想全局激活 `pnpm`，就按上面的兼容写法使用 `corepack pnpm ...`。

### `notice-codegen.py` 需要传哪些环境变量

默认情况下只需要：

```bash
OPENAI_API_KEY=你的key
```

脚本当前默认值是：

- `OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/`
- `OPENAI_MODEL_NAME=models/gemini-3-flash-preview`
