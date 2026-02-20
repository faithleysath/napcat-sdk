from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from napcat.cli.commands.call import cmd_call
from napcat.cli.config import InstanceConfig
from napcat.cli.gateway.protocol import GatewayError


def _prepare_instance(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(InstanceConfig, "BASE_DIR", tmp_path)
    config = InstanceConfig("demo")
    config.update(ws_url="ws://127.0.0.1:3001")


def _always_running(_self: InstanceConfig) -> bool:
    return True


def test_cmd_call_returns_success_when_api_result_is_none(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _prepare_instance(monkeypatch, tmp_path)

    class FakeGatewayClient:
        def __init__(self, _socket_path: Path):
            pass

        async def call_api(
            self,
            action: str,
            params: dict[str, Any] | None = None,
        ) -> Any:
            assert action == "friend_poke"
            assert params == {"user_id": 123456}
            return None

    import napcat.cli.commands.call as call_module

    monkeypatch.setattr(InstanceConfig, "is_running", _always_running)
    monkeypatch.setattr(call_module, "GatewayClient", FakeGatewayClient)

    exit_code = cmd_call("demo", "friend_poke", '{"user_id": 123456}')
    assert exit_code == 0


def test_cmd_call_returns_error_when_gateway_raises(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _prepare_instance(monkeypatch, tmp_path)

    class FakeGatewayClient:
        def __init__(self, _socket_path: Path):
            pass

        async def call_api(
            self,
            _action: str,
            _params: dict[str, Any] | None = None,
        ) -> Any:
            raise GatewayError("boom")

    import napcat.cli.commands.call as call_module

    monkeypatch.setattr(InstanceConfig, "is_running", _always_running)
    monkeypatch.setattr(call_module, "GatewayClient", FakeGatewayClient)

    exit_code = cmd_call("demo", "friend_poke", '{"user_id": 123456}')
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "API error: boom" in captured.err
