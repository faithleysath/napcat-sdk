"""单文件复杂插件示例：群请假 / 审批机器人。"""

from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import Coroutine, Sequence
from dataclasses import dataclass, field
from typing import Literal

from napcat import (
    At,
    GroupMessageEvent,
    Image,
    Message,
    MessageSender,
    NapCatAPIError,
    NapCatClient,
    Text,
)
from napcat.matcher import event_match

logger = logging.getLogger("examples.leave_approval_plugin")

type SessionKey = tuple[int, str]
type LeaveStatus = Literal["pending", "approved", "rejected"]


class FlowCancelled(Exception):
    """用户主动取消当前多轮交互。"""


@dataclass(slots=True)
class LeaveApplication:
    request_id: str
    group_id: int
    applicant_id: str
    applicant_name: str
    start_time: str
    duration: str
    reason: str
    proof_ref: str | None = None
    status: LeaveStatus = "pending"
    reviewer_id: str | None = None
    reviewer_name: str | None = None
    review_note: str | None = None


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"缺少必填环境变量：{name}")
    return value


def parse_approver_ids(raw: str | None) -> set[str]:
    if not raw:
        return set()
    return {part.strip() for part in raw.split(",") if part.strip()}


def display_name(sender: MessageSender) -> str:
    return sender.card or sender.nickname


def first_image_ref(segments: Sequence[object]) -> str | None:
    for segment in segments:
        if isinstance(segment, Image):
            return segment.url or segment.file or segment.path
    return None


def normalize_decision(value: str) -> Literal["同意", "拒绝"] | None:
    text = value.strip()
    if text in {"同意", "批准", "通过", "approve"}:
        return "同意"
    if text in {"拒绝", "驳回", "不通过", "reject"}:
        return "拒绝"
    return None


def new_applications() -> dict[str, LeaveApplication]:
    return {}


def new_active_sessions() -> set[SessionKey]:
    return set()


def new_background_tasks() -> set[asyncio.Task[None]]:
    return set()


@dataclass(slots=True)
class LeaveApprovalPlugin:
    client: NapCatClient
    approver_ids: set[str]
    applications: dict[str, LeaveApplication] = field(default_factory=new_applications)
    active_sessions: set[SessionKey] = field(default_factory=new_active_sessions)
    background_tasks: set[asyncio.Task[None]] = field(default_factory=new_background_tasks)
    next_request_number: int = 1

    def is_approver(self, user_id: int | str) -> bool:
        return str(user_id) in self.approver_ids

    def session_key_for(self, event: GroupMessageEvent) -> SessionKey:
        return (event.group_id, str(event.user_id))

    def start_session(
        self,
        key: SessionKey,
        coro: Coroutine[object, object, None],
    ) -> bool:
        if key in self.active_sessions:
            return False

        self.active_sessions.add(key)
        task = asyncio.create_task(self._run_session(key, coro))
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)
        return True

    async def _run_session(
        self,
        key: SessionKey,
        coro: Coroutine[object, object, None],
    ) -> None:
        try:
            await coro
        except FlowCancelled:
            logger.info("会话已取消：%s", key)
        except TimeoutError:
            logger.info("会话超时：%s", key)
        except Exception:
            logger.exception("会话异常：%s", key)
        finally:
            self.active_sessions.discard(key)

    async def run(self) -> None:
        print("请假审批插件已启动。")
        print("命令：/请假、/审批、/审批 列表、/帮助")

        # filter_waiters=True 可以避免多轮交互阶段的消息再次流回主分发循环。
        async for event in self.client.events(filter_waiters=True):
            match event:
                case GroupMessageEvent(message=[Text(text=text)]) if text.strip() in {
                    "/帮助",
                    "/help",
                }:
                    await self.send_help(event)

                case GroupMessageEvent(message=[Text(text=text)]) if text.strip().startswith("/请假"):
                    key = self.session_key_for(event)
                    started = self.start_session(
                        key,
                        self.handle_leave_command(event, text.strip()),
                    )
                    if not started:
                        await event.reply(
                            "你当前已有一个进行中的交互，请按提示继续，或回复 取消。",
                            at=True,
                        )

                case GroupMessageEvent(message=[Text(text=text)]) if text.strip().startswith("/审批"):
                    if not self.is_approver(event.user_id):
                        await event.reply("只有审批人可以使用 /审批。", at=True)
                        continue

                    key = self.session_key_for(event)
                    started = self.start_session(
                        key,
                        self.handle_review_command(event, text.strip()),
                    )
                    if not started:
                        await event.reply(
                            "你当前已有一个进行中的审批交互，请先完成它，或回复 取消。",
                            at=True,
                        )

                case _:
                    continue

    async def send_help(self, event: GroupMessageEvent) -> None:
        help_text = (
            "请假插件命令说明：\n"
            "1. /请假\n"
            "   进入多轮补参流程。\n"
            "2. /请假 开始时间 | 时长 | 原因\n"
            "   例如：/请假 明天下午两点 | 2小时 | 去医院复查\n"
            "3. /审批 列表\n"
            "   查看当前群待审批的请假单。\n"
            "4. /审批 单号 同意 [备注]\n"
            "5. /审批 单号 拒绝 [原因]\n"
            "多轮交互期间可随时回复：取消"
        )
        await event.reply(help_text, at=True)

    async def handle_leave_command(
        self,
        event: GroupMessageEvent,
        command_text: str,
    ) -> None:
        payload = command_text.removeprefix("/请假").strip()
        if payload == "取消":
            await event.reply("当前没有可直接取消的旧会话，请在交互提示里回复 取消。", at=True)
            return

        start_time, duration, reason = self.parse_leave_payload(payload)

        try:
            if start_time is None:
                start_time = await self.ask_text(
                    event,
                    prompt="请回复请假开始时间，例如：明天下午两点",
                )

            if duration is None:
                duration = await self.ask_text(
                    event,
                    prompt="请回复请假时长，例如：2小时 或 今天全天",
                )

            if reason is None:
                reason = await self.ask_text(
                    event,
                    prompt="请回复请假原因，例如：去医院复查",
                )

            proof_ref = await self.ask_optional_image(
                event,
                prompt="如果有请假证明，请发送一张图片；没有就回复 跳过。",
            )
        except FlowCancelled:
            await event.reply("已取消当前请假流程。", at=True)
            raise
        except TimeoutError:
            await event.reply("等待超时，请重新发送 /请假 开始新的流程。", at=True)
            raise

        application = LeaveApplication(
            request_id=f"L{self.next_request_number:04d}",
            group_id=event.group_id,
            applicant_id=str(event.user_id),
            applicant_name=display_name(event.sender),
            start_time=start_time,
            duration=duration,
            reason=reason,
            proof_ref=proof_ref,
        )
        self.next_request_number += 1
        self.applications[application.request_id] = application

        await event.reply(
            f"请假单 {application.request_id} 已创建，正在通知审批人。",
            at=True,
        )
        await self.broadcast_new_application(application)

    async def handle_review_command(
        self,
        event: GroupMessageEvent,
        command_text: str,
    ) -> None:
        payload = command_text.removeprefix("/审批").strip()
        if payload == "列表":
            await event.reply(self.render_pending_list(event.group_id), at=True)
            return

        if not payload:
            await event.reply(
                "用法：/审批 单号 同意 [备注]\n"
                "或：/审批 单号 拒绝 [原因]\n"
                "也可以先发：/审批 列表",
                at=True,
            )
            return

        tokens = payload.split(maxsplit=2)
        request_id = tokens[0]
        decision_text = tokens[1] if len(tokens) >= 2 else None
        note = tokens[2] if len(tokens) >= 3 else None

        application = self.applications.get(request_id)
        if application is None or application.group_id != event.group_id:
            await event.reply(f"未找到请假单：{request_id}", at=True)
            return

        if application.status != "pending":
            await event.reply(
                f"请假单 {request_id} 当前状态是 {application.status}，不能重复审批。",
                at=True,
            )
            return

        try:
            decision = await self.resolve_decision(event, decision_text)

            if decision == "拒绝":
                final_note = note or await self.ask_text(
                    event,
                    prompt="请回复驳回原因。",
                )
            else:
                final_note = note or await self.ask_optional_text(
                    event,
                    prompt="如需附加审批备注，请回复文本；没有就回复 跳过。",
                )
        except FlowCancelled:
            await event.reply("已取消当前审批流程。", at=True)
            raise
        except TimeoutError:
            await event.reply("审批等待超时，请重新发送 /审批。", at=True)
            raise

        application.status = "approved" if decision == "同意" else "rejected"
        application.reviewer_id = str(event.user_id)
        application.reviewer_name = display_name(event.sender)
        application.review_note = final_note

        await event.reply(
            f"已完成审批：{application.request_id} -> {decision}",
            at=True,
        )
        await self.broadcast_review_result(application, decision)
        await self.notify_applicant(application, decision)

    def parse_leave_payload(
        self,
        payload: str,
    ) -> tuple[str | None, str | None, str | None]:
        if not payload:
            return None, None, None

        parts = [part.strip() for part in payload.split("|")]
        start_time = parts[0] if len(parts) >= 1 and parts[0] else None
        duration = parts[1] if len(parts) >= 2 and parts[1] else None
        reason = " | ".join(part for part in parts[2:] if part) if len(parts) >= 3 else None

        return start_time, duration, reason

    async def wait_same_group_user_message(
        self,
        origin: GroupMessageEvent,
        *,
        timeout: float = 180.0,
    ) -> GroupMessageEvent:
        waited = await self.client.wait_event(
            event_match(
                GroupMessageEvent,
                group_id=origin.group_id,
                user_id=origin.user_id,
            ),
            timeout=timeout,
        )
        if not isinstance(waited, GroupMessageEvent):
            raise RuntimeError("wait_event 返回了意料之外的事件类型")
        return waited

    async def ask_text(
        self,
        origin: GroupMessageEvent,
        *,
        prompt: str,
    ) -> str:
        await origin.reply(f"{prompt}\n回复 取消 可终止当前流程。", at=True)

        while True:
            event = await self.wait_same_group_user_message(origin)
            match event:
                case GroupMessageEvent(message=[Text(text=text)]):
                    normalized = text.strip()
                    if normalized == "取消":
                        raise FlowCancelled
                    if not normalized:
                        await event.reply("请输入非空文本，或回复 取消。", at=True)
                        continue
                    if normalized.startswith("/"):
                        await event.reply(
                            "当前正在进行多轮交互，请先按提示回复，或发送 取消。",
                            at=True,
                        )
                        continue
                    return normalized
                case _:
                    await event.reply("请回复纯文本，或发送 取消。", at=True)

    async def ask_optional_text(
        self,
        origin: GroupMessageEvent,
        *,
        prompt: str,
    ) -> str | None:
        await origin.reply(f"{prompt}\n回复 跳过 可跳过，回复 取消 可终止流程。", at=True)

        while True:
            event = await self.wait_same_group_user_message(origin)
            match event:
                case GroupMessageEvent(message=[Text(text=text)]):
                    normalized = text.strip()
                    if normalized == "取消":
                        raise FlowCancelled
                    if normalized == "跳过":
                        return None
                    if not normalized:
                        await event.reply("请输入非空文本、跳过，或取消。", at=True)
                        continue
                    if normalized.startswith("/"):
                        await event.reply(
                            "当前正在进行多轮交互，请先按提示回复，或发送 跳过 / 取消。",
                            at=True,
                        )
                        continue
                    return normalized
                case _:
                    await event.reply("请回复纯文本，也可以发送 跳过 / 取消。", at=True)

    async def ask_optional_image(
        self,
        origin: GroupMessageEvent,
        *,
        prompt: str,
    ) -> str | None:
        await origin.reply(f"{prompt}\n回复 跳过 可跳过，回复 取消 可终止流程。", at=True)

        while True:
            event = await self.wait_same_group_user_message(origin)
            match event:
                case GroupMessageEvent(message=[Text(text=text)]):
                    normalized = text.strip()
                    if normalized == "取消":
                        raise FlowCancelled
                    if normalized == "跳过":
                        return None
                    await event.reply("请发送一张图片，或回复 跳过 / 取消。", at=True)
                case GroupMessageEvent(message=segments) if (image_ref := first_image_ref(segments)):
                    return image_ref
                case _:
                    await event.reply("请发送一张图片，或回复 跳过 / 取消。", at=True)

    async def resolve_decision(
        self,
        origin: GroupMessageEvent,
        decision_text: str | None,
    ) -> Literal["同意", "拒绝"]:
        if decision_text is not None and (decision := normalize_decision(decision_text)):
            return decision

        await origin.reply("请回复审批结论：同意 或 拒绝。", at=True)
        while True:
            event = await self.wait_same_group_user_message(origin)
            match event:
                case GroupMessageEvent(message=[Text(text=text)]):
                    normalized = text.strip()
                    if normalized == "取消":
                        raise FlowCancelled
                    decision = normalize_decision(normalized)
                    if decision is not None:
                        return decision
                    await event.reply("只接受：同意 / 拒绝，或发送 取消。", at=True)
                case _:
                    await event.reply("请回复纯文本：同意 / 拒绝，或发送 取消。", at=True)

    def render_pending_list(self, group_id: int) -> str:
        pending = [
            app
            for app in self.applications.values()
            if app.group_id == group_id and app.status == "pending"
        ]
        if not pending:
            return "当前群没有待审批的请假单。"

        lines = ["当前待审批请假单："]
        for app in pending:
            lines.append(
                f"- {app.request_id} | {app.applicant_name} | {app.start_time} | {app.duration} | {app.reason}"
            )
        return "\n".join(lines)

    async def broadcast_new_application(self, application: LeaveApplication) -> None:
        message: list[Message] = []

        for approver_id in sorted(self.approver_ids):
            message.append(At(qq=approver_id))
            message.append(Text(text=" "))

        summary = (
            f"新的请假申请 {application.request_id}\n"
            f"申请人：{application.applicant_name}\n"
            f"开始时间：{application.start_time}\n"
            f"时长：{application.duration}\n"
            f"原因：{application.reason}\n"
            f"审批命令：/审批 {application.request_id} 同意\n"
            f"或：/审批 {application.request_id} 拒绝 原因"
        )
        message.append(Text(text=summary))

        if application.proof_ref:
            message.append(Text(text="\n证明材料："))
            message.append(Image(file=application.proof_ref))

        await self.client.send_group_msg(
            group_id=str(application.group_id),
            message=message,
        )

    async def broadcast_review_result(
        self,
        application: LeaveApplication,
        decision: Literal["同意", "拒绝"],
    ) -> None:
        message: list[Message] = [
            At(qq=application.applicant_id),
            Text(
                text=(
                    f" 请假单 {application.request_id} 已{decision}\n"
                    f"审批人：{application.reviewer_name or application.reviewer_id}\n"
                    f"备注：{application.review_note or '无'}"
                )
            ),
        ]
        await self.client.send_group_msg(
            group_id=str(application.group_id),
            message=message,
        )

    async def notify_applicant(
        self,
        application: LeaveApplication,
        decision: Literal["同意", "拒绝"],
    ) -> None:
        message = (
            f"你的请假单 {application.request_id} 已{decision}\n"
            f"开始时间：{application.start_time}\n"
            f"时长：{application.duration}\n"
            f"原因：{application.reason}\n"
            f"审批人：{application.reviewer_name or application.reviewer_id}\n"
            f"备注：{application.review_note or '无'}"
        )
        try:
            await self.client.send_private_msg(
                user_id=application.applicant_id,
                message=message,
            )
        except NapCatAPIError as exc:
            logger.warning("私聊通知申请人失败: %s", exc)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    client = NapCatClient(
        ws_url=require_env("NAPCAT_WS_URL"),
        token=os.getenv("NAPCAT_TOKEN"),
    )
    approver_ids = parse_approver_ids(os.getenv("NAPCAT_APPROVER_IDS"))

    if not approver_ids:
        print("警告：未设置 NAPCAT_APPROVER_IDS，新的请假单将不会 @ 特定审批人。")

    plugin = LeaveApprovalPlugin(
        client=client,
        approver_ids=approver_ids,
    )
    await plugin.run()


if __name__ == "__main__":
    asyncio.run(main())
