"""
Gateway 通信协议

定义 CLI 与 Gateway 之间的 JSON-RPC 2.0 风格通信协议。
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

import orjson


@dataclass
class GatewayRequest:
    """
    Gateway 请求

    JSON-RPC 2.0 风格的请求格式:
    {
        "jsonrpc": "2.0",
        "id": "uuid-string",
        "method": "method_name",
        "params": {...}
    }
    """

    method: str
    params: dict[str, Any] = field(default_factory=dict[str, Any])
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    jsonrpc: str = "2.0"

    def to_dict(self) -> dict[str, Any]:
        return {
            "jsonrpc": self.jsonrpc,
            "id": self.id,
            "method": self.method,
            "params": self.params,
        }

    def to_json(self) -> str:
        return orjson.dumps(self.to_dict()).decode("utf-8")

    @classmethod
    def from_json(cls, data: str | bytes) -> GatewayRequest:
        obj = orjson.loads(data)
        return cls(
            id=obj.get("id", str(uuid.uuid4())),
            method=obj["method"],
            params=obj.get("params", {}),
            jsonrpc=obj.get("jsonrpc", "2.0"),
        )


@dataclass
class GatewayResponse:
    """
    Gateway 响应

    JSON-RPC 2.0 风格的响应格式:
    {
        "jsonrpc": "2.0",
        "id": "uuid-string",
        "result": {...} | null,
        "error": {"code": -32600, "message": "..."} | null
    }
    """

    id: str
    result: Any = None
    error: dict[str, Any] | None = None
    jsonrpc: str = "2.0"

    def to_dict(self) -> dict[str, Any]:
        return {
            "jsonrpc": self.jsonrpc,
            "id": self.id,
            "result": self.result,
            "error": self.error,
        }

    def to_json(self) -> str:
        return orjson.dumps(self.to_dict()).decode("utf-8")

    @classmethod
    def success(cls, result: Any, request_id: str = "") -> GatewayResponse:
        return cls(id=request_id, result=result, error=None)

    @classmethod
    def error_response(
        cls,
        code: int,
        message: str,
        request_id: str = "",
        data: Any = None,
    ) -> GatewayResponse:
        error_obj: dict[str, Any] = {"code": code, "message": message}
        if data is not None:
            error_obj["data"] = data
        return cls(id=request_id, result=None, error=error_obj)

    @classmethod
    def from_json(cls, data: str | bytes) -> GatewayResponse:
        obj = orjson.loads(data)
        return cls(
            id=obj.get("id", ""),
            result=obj.get("result"),
            error=obj.get("error"),
            jsonrpc=obj.get("jsonrpc", "2.0"),
        )

    # 标准错误码
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

    # 自定义错误码
    CLIENT_NOT_CONNECTED = -4001
    GATEWAY_SHUTTING_DOWN = -4002


class GatewayError(Exception):
    """Gateway 错误"""

    def __init__(
        self,
        message: str,
        code: int = GatewayResponse.INTERNAL_ERROR,
        data: Any = None,
    ):
        super().__init__(message)
        self.code = code
        self.data = data
