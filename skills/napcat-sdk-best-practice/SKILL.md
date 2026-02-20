---
name: napcat-sdk-best-practice
description: |
  Best practices for developing QQ bots using NapCat SDK Python library. Use
  when the user wants to write bot code, handle events, send messages, use
  pattern matching, or understand SDK architecture. Covers client/server modes,
  event handling, message segments, and API usage patterns.
---

# NapCat SDK Best Practices

A type-safe, async-ready, framework-free Python SDK for NapCat/OneBot protocol.

## Installation

```bash
uv add napcat-sdk
# or
pip install napcat-sdk
```

## Core Philosophy

### Configuration vs Execution Separation
Creating `NapCatClient` only creates a configuration blueprint - no connection is established. The actual connection is lazily established when entering context or iterating.

### Automatic Lifecycle Management
- `async with client:` → auto-connect on enter, auto-disconnect on exit
- `async for event in client:` → auto-connect → receive event stream → auto-disconnect on completion

## Client Mode (Active Connection)

```python
from napcat import NapCatClient, GroupMessageEvent

async with NapCatClient(ws_url="ws://127.0.0.1:3001", token="xxx") as client:
    async for event in client:
        if isinstance(event, GroupMessageEvent):
            await event.reply("Received!")
```

## Server Mode (Reverse WebSocket)

NapCat connects to your program:

```python
from napcat import ReverseWebSocketServer, NapCatClient, GroupMessageEvent

async def handler(client: NapCatClient):
    async for event in client:
        if isinstance(event, GroupMessageEvent):
            await event.reply("Received!")

server = ReverseWebSocketServer(handler, port=8080, token="xxx")
await server.run_forever()
```

**Important**: Don't use `while True` inside handler - let it exit naturally on disconnect, server will wait for reconnection.

## Event Handling

### Event Hierarchy
```
NapCatEvent
├── MessageEvent → GroupMessageEvent, PrivateMessageEvent
├── NoticeEvent → PokeEvent, GroupBanEvent, ...
├── RequestEvent → FriendRequestEvent, GroupRequestEvent
└── MetaEvent
```

### Pattern Matching (Recommended)

```python
from napcat import GroupMessageEvent, PrivateMessageEvent, Text, At, Image

match event:
    # Match group message, extract group_id
    case GroupMessageEvent(group_id=gid, sender=sender):
        print(f"Group {gid} received message")

    # Match specific group + specific command
    case GroupMessageEvent(group_id=123456, raw_message="ping"):
        await event.reply("pong")

    # Match message structure: text + @ + image
    case GroupMessageEvent(message=[Text(text=t), At(qq=uid), Image(url=url)]):
        print(f"Command: {t}, Target: {uid}, Image: {url}")

    # Wildcard: message contains image
    case GroupMessageEvent(message=[*_, Image(url=url), *_]):
        print(f"Got image: {url}")

    case _:
        pass
```

### ⚠️ Pattern Matching Trap

```python
# ❌ Wrong: Python treats target_group as new variable assignment
case GroupMessageEvent(group_id=target_group): ...

# ✅ Correct: Use Guard (if clause)
case GroupMessageEvent(group_id=gid) if gid == target_group: ...
```

## Sending Messages

### Simple Text

```python
await client.send_group_msg(group_id=123, message="Hello")
await client.send_private_msg(user_id=456, message="Hi")
```

### Rich Media Messages

```python
from napcat import Text, At, Image, Face, Dice, Poke

# Build message chain
message = [
    At(qq="12345678"),
    Text(text=" Check this out: "),
    Image(file="https://example.com/image.jpg"),
]

await client.send_group_msg(group_id=123, message=message)
```

### Message Segment Types

| Type | Usage |
|------|-------|
| `Text(text="...")` | Plain text |
| `At(qq="123456")` | @Mention user |
| `At(qq="all")` | @All members |
| `Image(file="url")` | Image (URL, path, or base64) |
| `Face(id="123")` | QQ face emoji |
| `Record(file="url")` | Voice message |
| `Video(file="url")` | Video |
| `Dice(result=6)` | Dice (1-6) |
| `Poke(qq="123456")` | Poke |
| `Reply(id="123456")` | Reply to message |

## Event Quick Reference

### GroupMessageEvent
- `group_id: int` - Group number
- `user_id: int` - Sender QQ
- `message: list[MessageSegment]` - Message segments
- `raw_message: str` - Plain text message
- `sender: MessageSender` - Sender info (includes `role`, `nickname`)
- `reply(msg)` - Quick reply method

### PrivateMessageEvent
- `user_id: int` - Sender QQ
- `message: list[MessageSegment]` - Message segments
- `reply(msg)` - Quick reply method

### FriendRequestEvent
- `user_id: int` - Applicant QQ
- `comment: str` - Application note
- `approve(remark)` - Accept request
- `reject()` - Reject request

## API Usage

### Type-Safe API Calls

All 160+ APIs are mounted directly on client with full type hints:

```python
# Get login info
login_info = await client.get_login_info()
print(f"Logged in as: {login_info['nickname']}")

# Get group member list
members = await client.get_group_member_list(group_id=123456, no_cache=True)
for member in members:
    print(f"Member: {member['card'] or member['nickname']}")
```

### Dynamic API Calls

For APIs not yet included in SDK:

```python
await client.call_action("some_new_action", {"param": 1})
```

## Error Handling

```python
from napcat import NapCatAPIError, NapCatProtocolError, NapCatStateError

try:
    await client.get_login_info()
except NapCatAPIError as exc:
    print("API failed:", exc)
    print("action=", exc.action, "retcode=", exc.retcode)
except NapCatProtocolError as exc:
    print("Protocol error:", exc)
except NapCatStateError as exc:
    print("Client state error:", exc)
```

## RPC Mode (Cross-Process)

Events can be serialized for cross-process consumption:

```python
# Process A: Serialize
data = event.to_dict()
# Send via message queue...

# Process B: Deserialize and handle
event = NapCatEvent.from_dict(data, client=client)
await event.reply("Reply from remote process")
```

## Common Patterns

### Multi-Event Listener

```python
async def handle_events(client: NapCatClient):
    async for event in client:
        match event:
            case GroupMessageEvent(group_id=gid, raw_message=msg) if msg.startswith("/"):
                await handle_command(event)
            case PrivateMessageEvent():
                await handle_private(event)
            case FriendRequestEvent():
                await event.approve()
            case _:
                pass
```

### Parallel Listeners

```python
import asyncio

async def main():
    client = NapCatClient(ws_url="ws://localhost:3001", token="123")
    await asyncio.gather(
        listen_group(client),
        listen_private(client),
    )

asyncio.run(main())
```

## Resources

- **GitHub**: https://github.com/faithleysath/napcat-sdk
- **Docs**: https://faithleysath.github.io/napcat-sdk/
- **API Reference**: Use `napcat-sdk doc apis` CLI command
