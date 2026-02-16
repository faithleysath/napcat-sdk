from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from napcat.cli.commands.start import cmd_start
from napcat.cli.config import InstanceConfig
from napcat.cli.mcp import doc_server


def test_start_foreground_returns_error_when_gateway_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(InstanceConfig, "BASE_DIR", tmp_path)

    config = InstanceConfig("broken")
    config.update(ws_url="ws://127.0.0.1:3001")

    class FakeGateway:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            pass

        async def start(self) -> None:
            raise RuntimeError("startup failed")

    import napcat.cli.commands.start as start_module

    def fake_setup_signal_handlers(_cb: Callable[[], None]) -> None:
        return None

    monkeypatch.setattr(start_module, "Gateway", FakeGateway)
    monkeypatch.setattr(start_module, "setup_signal_handlers", fake_setup_signal_handlers)

    exit_code = cmd_start("broken", foreground=True)
    assert exit_code == 1


def test_doc_server_can_read_main_client_file() -> None:
    content = doc_server.logic_get_code_file("client.py")
    assert "class NapCatClient" in content


def test_doc_server_reads_llms_txt_content() -> None:
    content = doc_server.logic_get_llms_txt()
    assert content.startswith("# napcat-sdk")
