"""
Gateway 守护进程模块

提供 Unix Socket 服务器、客户端和通信协议。
"""

from .client import GatewayClient
from .protocol import GatewayError, GatewayRequest, GatewayResponse

__all__ = [
    "GatewayRequest",
    "GatewayResponse",
    "GatewayError",
    "GatewayClient",
]
