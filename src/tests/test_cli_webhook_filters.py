from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from napcat.cli.commands.webhook import cmd_webhook
from napcat.cli.config import InstanceConfig


def _prepare_instance(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    name: str = "demo",
) -> InstanceConfig:
    monkeypatch.setattr(InstanceConfig, "BASE_DIR", tmp_path)
    config = InstanceConfig(name)
    config.update(ws_url="ws://127.0.0.1:3001")
    return config


def test_webhook_rm_by_url_removes_all_matching_rules_offline(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = _prepare_instance(monkeypatch, tmp_path)
    config.add_webhook("https://a.example.com/hook", ["message"])
    config.add_webhook("https://a.example.com/hook", ["notice"])
    config.add_webhook("https://b.example.com/hook", ["request"])

    exit_code = cmd_webhook("demo", "rm", url="https://a.example.com/hook")

    assert exit_code == 0
    remaining = config.load()["webhooks"]
    assert len(remaining) == 1
    assert remaining[0].get("url") == "https://b.example.com/hook"


def test_webhook_rm_without_filters_removes_all_rules_offline(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = _prepare_instance(monkeypatch, tmp_path)
    config.add_webhook("https://a.example.com/hook", ["message"])
    config.add_webhook("https://b.example.com/hook", ["notice"])

    exit_code = cmd_webhook("demo", "rm")

    assert exit_code == 0
    assert config.load()["webhooks"] == []


def test_webhook_list_filters_by_event_when_url_not_provided(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config = _prepare_instance(monkeypatch, tmp_path)
    config.add_webhook("https://all.example.com/hook")
    config.add_webhook("https://message.example.com/hook", ["message"])
    config.add_webhook("https://notice.example.com/hook", ["notice"])

    exit_code = cmd_webhook("demo", "list", events=["message"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "https://all.example.com/hook" in captured.out
    assert "https://message.example.com/hook" in captured.out
    assert "https://notice.example.com/hook" not in captured.out


def test_webhook_url_and_event_filters_are_combined_for_remove(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = _prepare_instance(monkeypatch, tmp_path)
    config.add_webhook("https://a.example.com/hook", ["message"])
    config.add_webhook("https://a.example.com/hook", ["notice"])
    config.add_webhook("https://b.example.com/hook", ["meta"])

    exit_code = cmd_webhook(
        "demo",
        "rm",
        url="https://a.example.com/hook",
        events=["notice"],
    )

    assert exit_code == 0
    remaining = config.load()["webhooks"]
    assert [wh.get("url") for wh in remaining] == [
        "https://a.example.com/hook",
        "https://b.example.com/hook",
    ]
    assert [wh.get("events") for wh in remaining] == [["message"], ["meta"]]


def test_webhook_list_with_url_and_event_filters_uses_intersection(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config = _prepare_instance(monkeypatch, tmp_path)
    config.add_webhook("https://a.example.com/hook", ["message"])
    config.add_webhook("https://a.example.com/hook", ["notice"])
    config.add_webhook("https://b.example.com/hook", ["notice"])

    exit_code = cmd_webhook(
        "demo",
        "list",
        url="https://a.example.com/hook",
        events=["notice"],
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "https://a.example.com/hook" in captured.out
    assert "notice" in captured.out
    assert "message" not in captured.out
    assert "https://b.example.com/hook" not in captured.out


def test_webhook_rm_by_url_removes_all_matching_rules_online(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _prepare_instance(monkeypatch, tmp_path)

    state: list[dict[str, Any]] = [
        {"url": "https://a.example.com/hook", "events": ["message"]},
        {"url": "https://a.example.com/hook", "events": ["notice"]},
        {"url": "https://b.example.com/hook", "events": ["request"]},
    ]

    class FakeGatewayClient:
        def __init__(self, _socket_path: Path):
            pass

        async def list_webhooks(self) -> list[dict[str, Any]]:
            return [dict(item) for item in state]

        async def remove_webhook(
            self,
            url: str | None = None,
            index: int | None = None,
        ) -> bool:
            _ = url
            if index is None:
                return False
            if 0 <= index < len(state):
                state.pop(index)
                return True
            return False

    import napcat.cli.commands.webhook as webhook_module

    def always_running(_self: InstanceConfig) -> bool:
        return True

    monkeypatch.setattr(InstanceConfig, "is_running", always_running)
    monkeypatch.setattr(webhook_module, "GatewayClient", FakeGatewayClient)

    exit_code = cmd_webhook("demo", "rm", url="https://a.example.com/hook")

    assert exit_code == 0
    assert [item["url"] for item in state] == ["https://b.example.com/hook"]
