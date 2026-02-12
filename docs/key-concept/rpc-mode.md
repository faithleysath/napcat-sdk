---
icon: lucide/network
---

# 远程 RPC 模式

`NapCatClient` 的 **RPC 模式** 将客户端转化为透明的 WebSocket 网关，让外部应用可以通过网络接入 NapCat，而无需直接建立连接。

这在跨语言调用、分布式部署或多服务共享单个 NapCat 实例的场景中非常实用。

## 1. 核心概念：透明代理

在 RPC 模式下，`NapCatClient` 不再只是一个本地客户端，而是同时扮演了以下两个角色：

1. **与 NapCat 通信的客户端**：正常建立 WebSocket 连接，接收事件，发送 API 请求。
2. **面向外部应用的 RPC 服务端**：监听指定端口，接受外部客户端的连接，并将请求转发给 NapCat，再将响应返回。

### 双流设计

为了实现透明转发，SDK 在连接层面采用了 **双流架构**：

- **`event_stream`**：仅包含 OneBot 事件，供 Python 客户端本地消费。
- **`proxy_stream`**：包含 OneBot 事件 + 外部 RPC 响应，供 RPC 服务器广播使用。

这种分离确保了本地事件监听不会被外部 API 响应污染。

## 2. 快速开始

### 启动 RPC 服务器

只需在创建 `NapCatClient` 时启用 `rpc_mode`，即可自动启动内置的 RPC 服务器：

```python
import asyncio
from napcat import NapCatClient

async def main():
    # 启用 RPC 模式
    client = NapCatClient(
        ws_url="ws://localhost:3001",
        token="123",
        rpc_mode=True,        # 启用 RPC 服务器
        rpc_host="0.0.0.0",   # 监听所有网络接口
        rpc_port=8080,        # RPC 服务器端口（0 表示自动分配）
        rpc_token="my_secret" # RPC 鉴权令牌（可选）
    )
    
    async with client:
        print(f"RPC 服务器已启动：{client.rpc_url}")
        print(f"认证令牌：{client.rpc_token}")
        
        # 本地也可以正常处理事件
        async for event in client:
            print(f"本地收到事件: {event.post_type}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `rpc_mode` | `bool` | `False` | 是否启用 RPC 服务器 |
| `rpc_host` | `str` | `"0.0.0.0"` | 监听地址（`0.0.0.0` 表示所有接口） |
| `rpc_port` | `int` | `0` | 监听端口（`0` 表示自动分配） |
| `rpc_token` | `str \| None` | `None` | 鉴权令牌（`None` 自动生成，`""` 表示不鉴权） |

## 3. 外部客户端连接

外部应用可以通过 WebSocket 连接到 RPC 服务器，并使用标准的 OneBot 协议格式发送请求。

### 连接鉴权

RPC 服务器支持两种鉴权方式：

1. **HTTP Header 鉴权**：
   ```
   Authorization: Bearer <token>
   ```

2. **Query 参数鉴权**：
   ```
   ws://localhost:8080?token=<token>
   ```

> 🔒 **安全提示**：出于安全考虑，强烈建议在生产环境中设置 `rpc_token`。未经认证的连接会被立即拒绝（HTTP 403）。

### 发送请求

外部客户端需要按照 **OneBot 标准格式** 发送请求：

```json
{
  "action": "send_group_msg",
  "params": {
    "group_id": 123456,
    "message": "Hello from external client!"
  },
  "echo": "request-123"
}
```

RPC 服务器会将请求转发给 NapCat，并将响应原样返回：

```json
{
  "status": "ok",
  "retcode": 0,
  "data": {
    "message_id": 12345
  },
  "echo": "request-123"
}
```

## 4. 使用场景

### 场景一：跨语言调用

如果你的主程序使用 JavaScript / Java / Go 等语言，但希望复用 Python 侧的 NapCat 连接：

```
┌─────────────┐       ┌──────────────────┐       ┌─────────┐
│ Node.js App │──WS──>│ NapCat-SDK (RPC) │──WS──>│ NapCat  │
└─────────────┘       └──────────────────┘       └─────────┘
                              ↑
                              │ 本地事件处理
                              ↓
                      [ Python 业务逻辑 ]
```

### 场景二：分布式部署

在微服务架构中，可以将 NapCat 连接层单独部署，其他服务通过 RPC 接口调用：

```
┌──────────┐       ┌──────────┐
│ Service A│──┐    │          │
└──────────┘  │    │ NapCat   │
              ├───>│ (RPC)    │──────> NapCat
┌──────────┐  │    │          │
│ Service B│──┘    └──────────┘
└──────────┘
```

### 场景三：调试与监控

启动一个 RPC 服务器，通过 WebSocket 客户端工具（如 wscat）实时监控 OneBot 事件与 API 响应：

```bash
# 连接到 RPC 服务器
wscat -c "ws://localhost:8080?token=my_secret"

# 发送测试请求
> {"action":"get_login_info","params":{},"echo":"test"}
< {"status":"ok","retcode":0,"data":{"user_id":123456,"nickname":"Bot"},"echo":"test"}
```

## 5. 最佳实践

### ✅ 推荐做法

1. **设置强密码**：使用足够复杂的 `rpc_token`，避免使用空字符串。
2. **限制监听地址**：在仅本地使用时，设置 `rpc_host="127.0.0.1"` 以避免外部访问。
3. **使用 TLS 加密**：在公网部署时，建议在前端部署反向代理（如 Nginx）并启用 HTTPS/WSS。
4. **日志监控**：记录所有 RPC 连接的来源 IP，便于审计。

### ❌ 避免的做法

1. **不要暴露在公网**：如果没有额外的安全措施（如防火墙、VPN），不要将 RPC 服务器直接暴露在公网。
2. **不要禁用鉴权**：即使在内网环境，也建议保留 Token 鉴权机制。
3. **不要在 RPC 模式下运行高负载任务**：RPC 服务器会引入额外的网络开销，不适合高频 API 调用场景。

## 6. 生命周期管理

### 自动启动与停止

RPC 服务器的生命周期与 `NapCatClient` 绑定：

- **连接时**：自动在后台启动 RPC 服务器。
- **断开时**：自动停止服务器并断开所有 RPC 客户端。

```python
async with NapCatClient(..., rpc_mode=True) as client:
    # RPC 服务器已启动
    print(f"RPC 运行中: {client.rpc_url}")

# 离开上下文后，RPC 服务器自动停止
```

### 手动控制

你也可以通过内部方法手动控制（不推荐，仅供高级用户）：

```python
client = NapCatClient(..., rpc_mode=True)
await client.connect()  # 自动启动 RPC

# ... 运行一段时间

await client._stop_rpc()  # 手动停止 RPC 服务器
await client.disconnect()
```

## 7. 错误处理

### 鉴权失败

如果客户端提供的 Token 不匹配，连接会被拒绝：

```
HTTP/1.1 403 Forbidden
```

### 端口占用

如果指定的 `rpc_port` 已被占用，`connect()` 方法会抛出异常：

```python
try:
    await client.connect()
except OSError as exc:
    print(f"RPC 服务器启动失败: {exc}")
```

建议使用 `rpc_port=0` 让系统自动分配可用端口，然后通过 `client.rpc_url` 获取实际监听地址。

## 8. API 参考

### 实例属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `rpc_url` | `str \| None` | RPC 服务器的 WebSocket URL（仅在 RPC 模式下可用） |
| `rpc_token` | `str \| None` | RPC 鉴权令牌（仅在 RPC 模式下可用） |

### 配置参数

在实例化 `NapCatClient` 时传入：

```python
NapCatClient(
    ws_url="ws://localhost:3001",
    token="napcat_token",
    rpc_mode=True,         # 必须启用
    rpc_host="0.0.0.0",
    rpc_port=8080,
    rpc_token="my_secret"
)
```

---

## 总结

RPC 模式让 NapCat-SDK 从单纯的 Python 客户端，升级为可跨语言、跨服务调用的网络代理。它在保持 Python 侧完整功能的同时，向外部世界开放了标准化的 API 接口。

**核心要点：**

1. **透明转发**：外部请求通过 WebSocket 进入，经由 SDK 转发给 NapCat，响应原路返回。
2. **双流隔离**：本地事件流与 RPC 响应流互不干扰。
3. **安全优先**：支持 Token 鉴权，建议在生产环境启用。
4. **生命周期绑定**：RPC 服务器随 Client 连接自动启停。

