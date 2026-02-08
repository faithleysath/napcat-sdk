---
icon: lucide/wrench
---

# 开发指南

如果你需要参与贡献或同步协议定义，可以参考本节。

## 环境准备

项目使用 [uv](https://github.com/astral-sh/uv) 管理依赖：

```bash
git clone https://github.com/faithleysath/napcat-sdk.git
cd napcat-sdk
uv sync
```

## 协议同步与代码生成

SDK 的类型与 API 定义由 OpenAPI 自动生成，更新协议后执行：

```bash
uv run scripts/schema-codegen.py
```

生成内容包括：

- `src/napcat/types/messages/generated.py`
- `src/napcat/types/schemas.py`
- `src/napcat/client_api.py`

## 运行测试

```bash
uv run pytest src/tests -m "not static" -q
```

## 提交规范建议

- 重要改动请同步更新文档与类型定义
- 如遇上游新增 API，可先使用动态调用进行临时验证
