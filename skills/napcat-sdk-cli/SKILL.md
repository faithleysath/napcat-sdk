---
name: napcat-sdk-cli
description: |
  NapCat SDK CLI tool for managing QQ bot instances. Use when the user wants to
  configure, start, stop bot instances, call OneBot APIs via command line,
  manage webhooks, or query SDK documentation. Supports instance management,
  API calls, webhook configuration, and MCP integration.
---

# NapCat SDK CLI

A command-line tool for managing QQ bot instances based on NapCat/OneBot protocol.

## Installation

```bash
uvx napcat-sdk
# or
pip install napcat-sdk
napcat-sdk --help
```

## Quick Reference

### Instance Management

```bash
# Configure an instance
napcat-sdk config <NAME> --ws ws://127.0.0.1:3001 --token <TOKEN>

# Enable RPC mode (for cross-process access)
napcat-sdk config <NAME> --rpc-mode on --rpc-host 0.0.0.0 --rpc-port 8080

# Start / Stop / Restart
napcat-sdk start <NAME>
napcat-sdk stop <NAME>
napcat-sdk restart <NAME>

# List all instances
napcat-sdk list
```

### Calling OneBot APIs

```bash
# Get login info
napcat-sdk call <NAME> get_login_info

# Send private message
napcat-sdk call <NAME> send_private_msg '{"user_id":123456,"message":"Hello"}'

# Send group message
napcat-sdk call <NAME> send_group_msg '{"group_id":123456,"message":"Hello"}'

# Send poke
napcat-sdk call <NAME> friend_poke '{"user_id":"123456"}'

# Send dice
napcat-sdk call <NAME> send_private_msg '{"user_id":"123456","message":[{"type":"dice","data":{"result":6}}]}'

# Set QQ profile
napcat-sdk call <NAME> set_qq_profile '{"nickname":"NewName","personal_note":"My signature"}'
```

### Webhook Management

```bash
# Add webhook (with optional event filter)
napcat-sdk webhook <NAME> add <URL> --event message --event notice

# List webhooks
napcat-sdk webhook <NAME> list

# Remove webhook
napcat-sdk webhook <NAME> rm <URL>
```

### Documentation Query

```bash
# List all available APIs
napcat-sdk doc apis

# Get specific API details
napcat-sdk doc api send_private_msg
napcat-sdk doc api get_login_info

# View source code files
napcat-sdk doc files
napcat-sdk doc code cli/commands/call.py

# View class definition
napcat-sdk doc class NapCatClient
napcat-sdk doc class Dice
```

### Logs

```bash
# View instance logs
napcat-sdk log <NAME>
```

## Common Parameters

### Message Types

```json
// Text
{"type": "text", "data": {"text": "Hello"}}

// Image (URL or base64)
{"type": "image", "data": {"file": "https://example.com/image.jpg"}}

// @Mention
{"type": "at", "data": {"qq": "123456"}}

// Dice (1-6)
{"type": "dice", "data": {"result": 6}}

// Face emoji
{"type": "face", "data": {"id": "123"}}

// Voice
{"type": "record", "data": {"file": "https://example.com/voice.mp3"}}

// Reply to message
{"type": "reply", "data": {"id": "123456"}}
```

### Composite Messages

```json
{
  "user_id": "123456",
  "message": [
    {"type": "at", "data": {"qq": "123456"}},
    {"type": "text", "data": {"text": " Hello!"}},
    {"type": "image", "data": {"file": "https://example.com/image.jpg"}}
  ]
}
```

## Notes

- API responses with `status: "ok"` and `retcode: 0` indicate success
- Some APIs (like poke) return empty data on success
- Token can be configured per instance or passed via `--token`
- WebSocket URL format: `ws://host:port` or `wss://host:port`
