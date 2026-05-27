"""NapCat 异步客户端。

本模块提供 ``NapCatClient``，用于通过 OneBot WebSocket 与 NapCatQQ
通信。客户端支持主动连接 NapCat，也支持复用反向 WebSocket 服务端接收到的
连接，并把事件流、API 调用和事件等待统一到一个 Python 原生异步对象上。
"""

import asyncio
import logging
from collections.abc import AsyncGenerator, Callable, Mapping
from types import TracebackType
from typing import Any, Self, cast

from websockets.asyncio.client import connect as ws_connect

from .client_api import NapCatAPIMixin
from .connection import Connection
from .exceptions import NapCatAPIError, NapCatError, NapCatStateError
from .types import NapCatEvent
from .types.messages import Message

logger = logging.getLogger("napcat.client")
type WaitPredicate = Callable[[NapCatEvent], bool]


class NapCatClient(NapCatAPIMixin):
    """NapCat 的异步 WebSocket 客户端。

    这个对象负责管理 WebSocket 生命周期、接收并解析事件、调用 OneBot
    API，并提供等待特定事件的轻量工具。它既可以作为异步上下文管理器用于
    直接 API 调用，也可以直接作为异步迭代器消费事件。

    Args:
        ws_url: NapCat 正向 WebSocket 地址。通过 ``from_connection`` 复用
            外部连接时可以省略。
        token: 可选访问令牌。主动连接时会以 Bearer token 的形式发送。

    Attributes:
        self_id: 连接建立后获取到的机器人账号 ID。获取失败或尚未连接时为
            ``None``。
    """

    def __init__(
        self,
        ws_url: str | None = None,
        token: str | None = None,
    ):
        self.ws_url = ws_url
        self.token = token
        self._conn: Connection | None = None
        self._has_external_conn = False
        self._ws_ctx: ws_connect | None = None
        self._entered = False
        self._context_refs = 0
        self._lifecycle_lock = asyncio.Lock()
        self.self_id: int | None = None

    @classmethod
    def from_connection(cls, conn: Connection) -> Self:
        """从已有 WebSocket 连接创建客户端。

        这个构造器主要供 ``ReverseWebSocketServer`` 使用，用于把反向
        WebSocket 接入转换成和主动连接一致的 ``NapCatClient`` 接口。

        Args:
            conn: 已经建立的底层连接。

        Returns:
            复用该连接的客户端实例。
        """

        client = cls()
        client._conn = conn
        client._has_external_conn = True
        return client

    def _connection_running(self) -> bool:
        return bool(self._conn and self._conn.is_running)

    @property
    def is_running(self) -> bool:
        """当前客户端连接是否正在运行。"""

        return self._connection_running()

    async def __aenter__(self):
        """进入客户端连接上下文。

        如果客户端尚未连接，会根据初始化参数建立连接；如果连接已经运行，
        则复用当前连接并增加上下文引用计数。

        Returns:
            已连接的客户端实例。

        Raises:
            ValueError: 未提供 WebSocket 地址且没有可复用连接时抛出。
            NapCatError: 初始化连接后获取登录信息失败以外的 SDK 错误。
        """

        async with self._lifecycle_lock:
            self._context_refs += 1

            # 已有活跃连接时，仅增加上下文引用计数即可
            # 不依赖引用计数值判断复用，直接以连接运行状态为准
            if self._connection_running():
                self._entered = True
                return self

            # 用于跟踪已打开的资源，便于异常时回滚
            ws_ctx_entered = False
            conn_entered = False

            try:
                # 如果是 Server 模式，直接启动 from_connection 传入的连接
                if self._has_external_conn:
                    if not self._conn:
                        raise ValueError("Invalid Client: Missing existing connection")
                    await self._conn.__aenter__()
                    conn_entered = True
                # 如果是 Client 模式（主动连接），建立连接并包装
                elif self.ws_url:
                    headers = (
                        {"Authorization": f"Bearer {self.token}"} if self.token else {}
                    )
                    self._ws_ctx = ws_connect(self.ws_url, additional_headers=headers)
                    ws = await self._ws_ctx.__aenter__()
                    ws_ctx_entered = True
                    self._conn = Connection(ws)
                    await self._conn.__aenter__()
                    conn_entered = True
                else:
                    raise ValueError(
                        "Invalid Client: No URL and no existing connection"
                    )

                self._entered = True
                # 获取自身 ID (增加容错处理)
                try:
                    resp = await self.get_login_info()
                    self.self_id = resp["user_id"]
                except NapCatError as e:
                    logger.warning("Failed to get self_id: %s", e)
                    self.self_id = None

                return self
            except Exception:
                # 异常时回滚已打开的资源
                if conn_entered and self._conn:
                    try:
                        await self._conn.__aexit__(None, None, None)
                    except Exception:
                        pass
                if ws_ctx_entered and self._ws_ctx:
                    try:
                        await self._ws_ctx.__aexit__(None, None, None)
                    except Exception:
                        pass
                # 清理状态
                if not self._has_external_conn:
                    self._conn = None
                self._ws_ctx = None
                self._context_refs -= 1
                if self._context_refs == 0:
                    self._entered = False
                raise

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        """退出客户端连接上下文。

        当最后一个上下文引用退出时关闭底层连接。若用户代码已经抛出异常，
        清理阶段的异常只会记录日志，不会覆盖原始异常。

        Args:
            exc_type: 上下文中的异常类型。
            exc_val: 上下文中的异常实例。
            exc_tb: 上下文中的异常调用栈。

        Raises:
            BaseException: 没有原始异常且清理失败时，重新抛出清理异常。
        """

        async with self._lifecycle_lock:
            if self._context_refs == 0:
                return

            self._context_refs -= 1
            if self._context_refs > 0:
                return

            # 级联关闭：Client -> Connection -> WebSocket
            conn = self._conn
            ws_ctx = self._ws_ctx
            cleanup_errors: list[BaseException] = []

            try:
                if conn:
                    try:
                        await conn.__aexit__(exc_type, exc_val, exc_tb)
                    except Exception as e:
                        cleanup_errors.append(e)
                # 仅在 Client 模式下关闭 ws_ctx（Server 模式由外部管理）
                if ws_ctx and not self._has_external_conn:
                    try:
                        await ws_ctx.__aexit__(exc_type, exc_val, exc_tb)
                    except Exception as e:
                        cleanup_errors.append(e)
            finally:
                self._entered = False
                if not self._has_external_conn:
                    self._conn = None
                self._ws_ctx = None

            if cleanup_errors:
                for err in cleanup_errors:
                    logger.warning("Cleanup error: %s", err)
                if exc_type is None:
                    raise cleanup_errors[0]

    async def _events(self) -> AsyncGenerator[NapCatEvent, None]:
        if not self._conn:
            raise NapCatStateError("Client not connected")
        if not self._connection_running():
            raise NapCatStateError("Client not connected or already closed")

        async for event in self._conn.events():
            event = NapCatEvent.from_dict(event)
            object.__setattr__(event, "_client", self)
            yield event

    def events(self) -> AsyncGenerator[NapCatEvent, None]:
        """迭代接收到的 NapCat 事件。

        主动连接模式下，这个方法会在迭代开始和结束时自动管理连接生命
        周期。反向连接模式下，连接生命周期由外部服务器管理。

        Yields:
            已解析并绑定当前客户端的 NapCat 事件对象。

        Raises:
            NapCatStateError: 客户端未连接或连接已经关闭时抛出。
        """

        if self._has_external_conn:
            return self._events()

        async def _iter() -> AsyncGenerator[NapCatEvent, None]:
            async with self:
                async for event in self._events():
                    yield event

        return _iter()

    def __aiter__(self) -> AsyncGenerator[NapCatEvent, None]:
        """把客户端作为异步事件迭代器使用。

        Returns:
            默认事件流，等价于调用 ``events()``。
        """

        return self.events()

    async def wait_event(
        self,
        predicate: WaitPredicate,
        timeout: float | None = None,
    ) -> NapCatEvent:
        """等待第一个满足条件的事件。

        这个方法会创建一个独立的事件观察流。它不会消费或隐藏事件，因此同一
        个事件仍然会出现在其他 ``events()`` 迭代器中，也可以同时唤醒多个
        ``wait_event`` 调用。

        Args:
            predicate: 接收事件并返回布尔值的判断函数。
            timeout: 最长等待秒数。为 ``None`` 时一直等待。

        Returns:
            第一个满足 ``predicate`` 的事件对象。

        Raises:
            TimeoutError: 在指定时间内没有等到匹配事件时抛出。
            NapCatStateError: 客户端关闭且没有等到匹配事件时抛出。
        """

        async def _wait() -> NapCatEvent:
            events = self.events()
            try:
                async for event in events:
                    if predicate(event):
                        return event
            finally:
                await events.aclose()
            raise NapCatStateError(
                "Client closed before wait_event received a matching event"
            )

        if timeout is None:
            return await _wait()
        async with asyncio.timeout(timeout):
            return await _wait()

    async def _send(self, data: dict[str, Any], timeout: float = 10.0) -> dict[str, Any]:
        if not self._conn:
            raise NapCatStateError("Client not connected")
        return await self._conn.send(data, timeout)

    async def call_action(
        self,
        action: str,
        params: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any] | None:
        """调用原始 OneBot action。

        这个方法是所有自动生成 API 方法的底层入口，也可以用于调用尚未手工
        封装的新接口。

        Args:
            action: OneBot action 名称。
            params: action 参数映射。省略时使用空参数。

        Returns:
            响应中的 ``data`` 字段。如果响应没有 data，则返回 ``None``。

        Raises:
            NapCatAPIError: NapCat 返回非成功状态或非零 retcode 时抛出。
            NapCatStateError: 客户端未连接时抛出。
        """

        if params is None:
            params = {}

        if (
            action in {"send_private_msg", "send_group_msg", "send_msg"}
            and "message" in params
        ):
            normalized_params = dict(params)
            message_for_send = cast(
                str | list[Message] | Message, normalized_params["message"]
            )
            normalized_params["message"] = self._normalize_message_for_send(
                message_for_send
            )
            params = normalized_params
        elif (
            action
            in {
                "send_forward_msg",
                "send_group_forward_msg",
                "send_private_forward_msg",
            }
            and "messages" in params
        ):
            normalized_params = dict(params)
            message_for_send = cast(
                str | list[Message] | Message, normalized_params["messages"]
            )
            normalized_params["messages"] = self._normalize_message_for_send(
                message_for_send
            )
            params = normalized_params
        elif action == ".handle_quick_operation":
            params = self._normalize_quick_operation_params(params)

        resp = await self._send({"action": action, "params": params})
        if resp.get("status") != "ok" or resp.get("retcode") != 0:
            raise NapCatAPIError(
                f"API call failed: {resp}",
                action=action,
                retcode=resp.get("retcode"),
                response=resp,
            )
        return resp.get("data", None)

    @staticmethod
    def _normalize_message_for_send(
        message: str | list[Message] | Message,
    ) -> str | list[dict[str, Any]] | dict[str, Any]:
        """把 SDK 消息对象转换为 NapCat 可发送的数据结构。"""

        if isinstance(message, str):
            return message
        if isinstance(message, list):
            return [dict(segment) for segment in message]
        return dict(message)

    @classmethod
    def _normalize_quick_operation_params(
        cls,
        params: Mapping[str, Any],
    ) -> dict[str, Any]:
        """规范化快速操作参数中的回复消息。"""

        operation = params.get("operation")
        if not isinstance(operation, Mapping) or "reply" not in operation:
            return dict(params)

        operation_mapping = cast(Mapping[str, Any], operation)
        reply = operation_mapping["reply"]
        if reply is None:
            return dict(params)

        normalized_params: dict[str, Any] = dict(params)
        normalized_operation: dict[str, Any] = dict(operation_mapping)
        normalized_operation["reply"] = cls._normalize_message_for_send(
            cast(str | list[Message] | Message, reply)
        )
        normalized_params["operation"] = normalized_operation
        return normalized_params

    # --- 黑魔法区域 ---

    def __getattr__(self, item: str):
        """把未知公开属性转换为动态 API 调用。

        这个 fallback 用于兼容尚未封装成方法的新 OneBot action。私有属性和
        ``send`` 不会走动态调用，以避免隐藏真实的属性错误。

        Args:
            item: 被访问的属性名，也会作为 OneBot action 名称。

        Returns:
            一个异步函数，调用后会把关键字参数传给 ``call_action``。

        Raises:
            AttributeError: 访问私有属性或被保留的属性名时抛出。
        """

        if item.startswith("_") or item == "send":
            raise AttributeError(item)

        async def dynamic_api_call(**kwargs: Any) -> Mapping[str, Any] | None:
            return await self.call_action(item, kwargs)

        return dynamic_api_call
