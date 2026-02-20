from __future__ import annotations

import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import pytest
from websockets.asyncio.server import unix_serve

import napcat.cli as cli_module
from napcat.cli.gateway.client import GatewayClient
from napcat.cli.gateway.protocol import GatewayError, GatewayRequest, GatewayResponse
from napcat.cli.gateway.server import Gateway


def test_cli_mcp_doc_dispatches_to_doc_server(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False

    def fake_doc_server_main() -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(cli_module, "run_doc_mcp_server", fake_doc_server_main)

    exit_code = cli_module.main(["mcp", "doc"])
    assert exit_code == 0
    assert called is True


def test_gateway_client_unix_socket_roundtrip_and_error() -> None:
    async def _run() -> None:
        with TemporaryDirectory() as tmpdir:
            socket_path = Path(tmpdir) / "gateway.sock"

            async def handler(ws: Any) -> None:
                async for raw_message in ws:
                    req = GatewayRequest.from_json(raw_message)
                    if req.method == "fail":
                        resp = GatewayResponse.error_response(
                            code=GatewayResponse.INVALID_PARAMS,
                            message="bad params",
                            request_id=req.id,
                            data={"field": "x"},
                        )
                    else:
                        resp = GatewayResponse.success({"method": req.method}, req.id)
                    await ws.send(resp.to_json())

            server = await unix_serve(handler, path=str(socket_path))
            try:
                client = GatewayClient(socket_path, timeout=1.0)

                result = await client.call("ping")
                assert result == {"method": "ping"}

                with pytest.raises(GatewayError) as exc_info:
                    await client.call("fail")

                assert exc_info.value.code == GatewayResponse.INVALID_PARAMS
                assert exc_info.value.data == {"field": "x"}
            finally:
                server.close()
                await server.wait_closed()

    asyncio.run(_run())


def test_gateway_socket_server_uses_unix_mode(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, Any] = {}
    state = {
        "closed": False,
        "wait_closed_called": False,
    }

    class FakeServer:
        def close(self) -> None:
            state["closed"] = True

        async def wait_closed(self) -> None:
            state["wait_closed_called"] = True

    class FakeServeContext:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            captured["args"] = args
            captured["kwargs"] = kwargs
            self._server = FakeServer()

        async def __aenter__(self) -> FakeServer:
            # _run_socket_server 会在进入上下文后 chmod socket 文件，
            # 这里创建占位文件以模拟真实 unix socket 已就绪的状态。
            Path(captured["kwargs"]["path"]).touch()
            return self._server

        async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: Any,
        ) -> bool:
            return False

    def fake_serve(*args: Any, **kwargs: Any) -> FakeServeContext:
        return FakeServeContext(*args, **kwargs)

    import napcat.cli.gateway.server as gateway_server_module

    monkeypatch.setattr(gateway_server_module, "serve", fake_serve)

    socket_path = tmp_path / "gateway.sock"
    gateway = Gateway(
        instance_name="test-instance",
        ws_url="ws://127.0.0.1:3001",
        socket_path=socket_path,
    )
    running_attr = "_running"
    run_socket_server_attr = "_run_socket_server"
    setattr(gateway, running_attr, False)

    async def _run() -> None:
        run_socket_server = getattr(gateway, run_socket_server_attr)
        await run_socket_server()

    asyncio.run(_run())

    assert captured["kwargs"]["unix"] is True
    assert captured["kwargs"]["path"] == str(socket_path)
    assert state["closed"] is True
    assert state["wait_closed_called"] is True


def test_gateway_remove_webhook_invalid_index_returns_invalid_params() -> None:
    gateway = Gateway(
        instance_name="test-instance",
        ws_url="ws://127.0.0.1:3001",
    )

    req = GatewayRequest(
        method="remove_webhook",
        params={"index": "abc"},
    )
    resp = gateway._handle_remove_webhook(req)  # pyright: ignore[reportPrivateUsage]

    assert resp.error is not None
    assert resp.error["code"] == GatewayResponse.INVALID_PARAMS
    assert "index" in resp.error["message"]


def test_gateway_start_passes_rpc_options_to_napcat_client(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, Any] = {}

    class FakeNapCatClient:
        def __init__(self, **kwargs: Any) -> None:
            captured.update(kwargs)
            self.is_running = True
            self.rpc_url_host = kwargs.get("rpc_public_host") or kwargs.get("rpc_host", "0.0.0.0")
            self.rpc_port = kwargs.get("rpc_port", 0)
            self.rpc_token = kwargs.get("rpc_token")

        async def __aenter__(self) -> FakeNapCatClient:
            return self

        async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: Any,
        ) -> bool:
            return False

        def __aiter__(self) -> Any:
            async def _empty() -> Any:
                if False:
                    yield None

            return _empty()

    async def fake_run_socket_server(_self: Gateway) -> None:
        return None

    import napcat.cli.gateway.server as gateway_server_module

    monkeypatch.setattr(gateway_server_module, "NapCatClient", FakeNapCatClient)
    monkeypatch.setattr(Gateway, "_run_socket_server", fake_run_socket_server)

    gateway = Gateway(
        instance_name="rpc-instance",
        ws_url="ws://127.0.0.1:3001",
        socket_path=tmp_path / "gateway.sock",
        rpc_mode=True,
        rpc_host="127.0.0.1",
        rpc_port=18080,
        rpc_token="secret-token",
        rpc_public_host="example.com",
    )

    asyncio.run(gateway.start())

    assert captured["rpc_mode"] is True
    assert captured["rpc_host"] == "127.0.0.1"
    assert captured["rpc_port"] == 18080
    assert captured["rpc_token"] == "secret-token"
    assert captured["rpc_public_host"] == "example.com"
