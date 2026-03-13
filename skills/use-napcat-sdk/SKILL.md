---
name: use-napcat-sdk
description: Explain and apply napcat-sdk for Python bots, scripts, and small apps. Use when Codex needs to install napcat-sdk, choose the right command path for the user's environment, understand the SDK's core mental model, or build code that talks to NapCat over forward or reverse WebSocket, handles typed events, replies to messages, waits for matching events, or calls typed OneBot APIs.
---

# Use NapCat SDK

## Overview

Use this skill to work with `napcat-sdk` while keeping context small.

Treat the installed package CLI as the source of truth for SDK documentation, including source-code lookup.

Prefer narrow CLI lookups over large one-shot doc dumps.

## Explain the SDK

Explain `napcat-sdk` as a typed, async Python SDK for connecting to NapCat over OneBot WebSocket.

Treat it as a thin, strongly typed layer around three core jobs:

- connect to NapCat
- consume typed events
- send replies or call typed APIs

## Choose an installation path

Confirm the target environment is running Python 3.12 or newer before suggesting installation commands or writing code against this SDK.

If the user's environment is on Python 3.11 or below, tell them to upgrade Python first instead of continuing with package installation steps.

Inspect the user's environment before suggesting or running installation commands.

Use this order:

1. Prefer `uv add napcat-sdk` when the user is already in a `uv`-managed project, `uv.lock` exists, or the user is already using `uv`.
2. Otherwise, prefer `pip install napcat-sdk` when a virtual environment or Conda environment is already active.
3. Use `uvx --from napcat-sdk napcat-sdk ...` when the user only needs the CLI temporarily and you should not modify project dependencies.
4. Use `pipx run napcat-sdk ...` only when `uv` is unavailable and `pipx` is available.
5. Avoid telling the user to install both the `uv` and `pip` variants unless they explicitly want both.

Treat `VIRTUAL_ENV` and `CONDA_PREFIX` as strong signals that an environment is already active.

## Choose a documentation path

Prefer the smallest command that answers the question.

Use this order:

1. If `napcat-sdk` is already on `PATH` in the active environment, call it directly.
2. If working inside this repository with synced dependencies, use `uv run napcat-sdk ...`.
3. If the package is not installed but `uvx` is available, use `uvx --from napcat-sdk napcat-sdk ...`.
4. If `uv` is unavailable but `pipx` is available, use `pipx run napcat-sdk ...`.

Prefer these focused commands:

- `napcat-sdk doc files`: list the SDK source index so you can discover which file to inspect next.
- `napcat-sdk doc apis`: list all exposed API actions when you need to find the right action name.
- `napcat-sdk doc api send_group_msg`: inspect one API action, including its signature, request shape, and response details.
- `napcat-sdk doc class NapCatClient`: inspect one class definition when you need the public structure or methods of a core type.
- `napcat-sdk doc code client.py`: inspect one specific source file when class or API docs are not enough and you need implementation details.

Do not default to `napcat-sdk doc agent --full --with-code`.

Use that command only if the user explicitly asks for a large one-shot context dump and the extra context cost is acceptable.

## Use the SDK mental model

Model most tasks around these building blocks:

- `NapCatClient`: forward WebSocket client and async event iterator.
- `client.events(filter_waiters=False)`: explicit event stream entrypoint; use it when you need options like waiter filtering.
- `ReverseWebSocketServer`: reverse WebSocket server for NapCat-initiated connections.
- Event and message dataclasses in `napcat.types`: typed Python objects for incoming payloads.
- Message segments like `Text`, `Image`, and `At`: structured outgoing messages instead of hand-written CQ code.
- Event helpers like `reply()`, `send_msg()`, `approve()`, and `reject()`: common actions live on the event objects themselves.
- Prefer client method calls over `call_action(...)`. Use generated typed methods when available, and keep using method syntax for newly added APIs when the action name is a valid Python identifier. Use `call_action(...)` only when the action name cannot be expressed cleanly as a Python method name or when an explicit action string is required.
- `event_match(...)` plus `wait_event(...)`: use for one-shot waits; use `async for event in client` or `async for event in client.events(...)` for ongoing routing.

## Keep context small

Use this lookup order:

1. Query specific CLI docs for the exact API or class you need.
2. Use `napcat-sdk doc files` to discover relevant source files.
3. Use `napcat-sdk doc code <PATH>` only for the single file you need.
4. Use `napcat-sdk doc class <NAME>` when the class definition is enough.
5. Use `napcat-sdk doc api <ACTION>` when you need request and response details for one action.
6. Avoid `napcat-sdk doc agent --full --with-code` unless the user explicitly wants a large bundle.

## Watch for common gotchas

- Outgoing API parameters often expect IDs like `group_id` and `user_id` as `str`, while incoming event objects often expose many of them as `int`.
- `NapCatClient` supports `async for event in client`, and that is shorthand for iterating `client.events()`.
- Use `client.events(filter_waiters=True)` when you need waiter-matched events to be filtered out of the main event loop during multi-step interaction flows.
- Use `async with client:` when you need explicit lifecycle control, especially around `wait_event(...)`.
- Prefer typed message segments over manual raw payload assembly.
- If the user is asking about SDK maintenance, codegen, or the `NapCatQQ` submodule, this skill is the wrong tool; those topics belong to SDK development rather than SDK usage.
