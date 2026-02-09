---
icon: lucide/download
---

# 安装

欢迎来到 NapCat-SDK 的世界。在开始编写你的第一个 Bot 之前，我们需要准备好开发环境。

为了获得最佳的类型提示和 `match-case` 模式匹配体验，我们强烈建议使用较新的 Python 版本。

## 环境要求

- **Python**: `3.12` 或更高版本 (强烈推荐)
- **NapCat**: 确保你已经运行了 NapCat (OneBot 11) 服务端

## 安装 SDK

打开你的终端，使用 pip 进行安装：

```bash
pip install napcat-sdk
```

> **注**：如果在安装过程中遇到网络问题，可以尝试使用国内镜像源： `pip install napcat-sdk -i https://pypi.tuna.tsinghua.edu.cn/simple`

## 验证安装

安装完成后，你可以新建一个 `test.py` 文件，输入以下代码来验证是否安装成功：

```python
import napcat
print(napcat.__version__)
```

如果没有报错并输出了版本号，恭喜你，环境准备就绪！

---

## 下一步

环境已经准备好了，接下来让我们编写第一行代码，建立与 NapCat 的连接。

👉 **前往：[第一个机器人](./first-bot.md)**
