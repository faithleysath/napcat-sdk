"""
call 命令

调用 OneBot API。
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from ..config import InstanceConfig
from ..gateway.client import GatewayClient
from ..gateway.protocol import GatewayError
from ..utils import print_error, print_instance_create_hint, print_instance_start_hint, print_json


def cmd_call(
    instance_name: str,
    action: str,
    params_json: str | None = None,
) -> int:
    """
    调用 OneBot API

    Args:
        instance_name: 实例名称
        action: API 端点名
        params_json: JSON 格式的参数 (可选)

    Returns:
        退出码
    """
    config = InstanceConfig(instance_name)

    if not config.exists():
        print_error(f"Instance '{instance_name}' does not exist.")
        print_instance_create_hint(instance_name)
        return 1

    if not config.is_running():
        print_error(f"Instance '{instance_name}' is not running.")
        print_instance_start_hint(instance_name)
        return 1

    # 解析参数
    params: dict[str, Any] = {}
    if params_json:
        try:
            params = json.loads(params_json)
        except json.JSONDecodeError as e:
            print_error(f"Invalid JSON params: {e}")
            print(f"Inspect the schema with: napcat-sdk doc api {action}")
            return 1

    # 调用 API
    client = GatewayClient(config.socket_file)

    async def do_call() -> Any:
        return await client.call_api(action, params)

    try:
        result = asyncio.run(do_call())
        if result is not None:
            print_json(result)
        return 0
    except GatewayError as e:
        print_error(f"API error: {e}")
        print(f"Inspect the schema with: napcat-sdk doc api {action}")
        return 1
    except ConnectionError as e:
        print_error(f"Connection error: {e}")
        return 1
    except TimeoutError:
        print_error("Request timeout.")
        return 1
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return 1
