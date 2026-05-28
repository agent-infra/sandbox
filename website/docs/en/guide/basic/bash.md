# Bash Pipe

`/v1/bash` is a subprocess pipe-based command execution service for programmatic and agent-friendly workflows. It is different from the PTY-based [Shell Terminal](/guide/basic/shell): Bash Pipe keeps `stdout` and `stderr` separate and supports incremental output reads with offsets.

## Shell vs Bash

| | `/v1/shell` | `/v1/bash` |
| --- | --- | --- |
| Backend | Terminal / PTY | subprocess pipe |
| Best for | Interactive terminals, WebSocket UI, human takeover | Agent tool calls, short commands, long command polling |
| Output | One combined `output` field | Separate `stdout` and `stderr` |
| Read model | Terminal snapshots and waits | Incremental reads with `offset` / `stderr_offset` |
| stdin | Terminal input stream | Writes to the running process stdin pipe |
| Command identity | Session-level | Each command has a `command_id` |

## Execute Short Commands

Most tool calls can complete with a single `exec` request. `status` is the command lifecycle state; `exit_code` is the command success indicator.

```bash
curl -X POST "http://localhost:8080/v1/bash/exec" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "pwd && ls -la",
    "exec_dir": "/home/gem",
    "timeout": 30,
    "hard_timeout": 120
  }'
```

Typical response shape:

```json
{
  "success": true,
  "data": {
    "session_id": "SESSION_ID",
    "command_id": "COMMAND_ID",
    "command": "pwd && ls -la",
    "status": "completed",
    "stdout": "/home/gem\n...",
    "stderr": null,
    "exit_code": 0,
    "offset": 128,
    "stderr_offset": 0
  }
}
```

## SDK Examples

Python:

```python
from agent_sandbox import Sandbox

client = Sandbox(base_url="http://localhost:8080")

result = client.bash.exec(
    command='printf "out\\n" && printf "err\\n" >&2',
    timeout=30,
    hard_timeout=120,
).data

print(result.stdout)
print(result.stderr)
print(result.exit_code)
```

TypeScript:

```typescript
import { SandboxClient } from "@agent-infra/sandbox";

const client = new SandboxClient({ baseUrl: "http://localhost:8080" });

const response = await client.bash.exec({
  command: 'printf "out\\n" && printf "err\\n" >&2',
  timeout: 30,
  hard_timeout: 120,
});

if (!response.ok) {
  throw new Error("Bash exec failed");
}

console.log(response.body.data?.stdout);
console.log(response.body.data?.stderr);
console.log(response.body.data?.exit_code);
```

## Long Commands And Incremental Output

When a command is still running after `timeout`, `/v1/bash/exec` returns `status: "running"` and the command continues in the background. Use `/v1/bash/output` to read incremental output.

```bash
# 1. Start a command. If it is not done within 1 second, it returns running.
curl -X POST "http://localhost:8080/v1/bash/exec" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "sleep 3; echo done",
    "timeout": 1,
    "hard_timeout": 30
  }'
```

```bash
# 2. Continue reading with the returned session_id, offset, and stderr_offset.
curl -X POST "http://localhost:8080/v1/bash/output" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID",
    "offset": 0,
    "stderr_offset": 0,
    "wait": true,
    "wait_timeout": 10
  }'
```

`wait=false` returns the currently available output immediately. `wait=true` long-polls until new output arrives, the command finishes, or `wait_timeout` expires. For agent polling, prefer `wait=true` to avoid unnecessary empty polling.

## Long-Lived Processes

For services that do not exit on their own, use `async_mode: true`, read startup logs, and call `/kill` when done.

```bash
curl -X POST "http://localhost:8080/v1/bash/exec" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "python3 -m http.server 3000 --directory /tmp",
    "async_mode": true,
    "hard_timeout": 3600
  }'
```

Read logs:

```bash
curl -X POST "http://localhost:8080/v1/bash/output" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID",
    "offset": 0,
    "stderr_offset": 0,
    "wait": true,
    "wait_timeout": 5
  }'
```

Stop the process:

```bash
curl -X POST "http://localhost:8080/v1/bash/kill" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID",
    "signal": "SIGTERM"
  }'
```

## Write To stdin

`/v1/bash/write` writes to the stdin pipe of the running process. Use it for `cat`, prompt-driven scripts, REPLs, and similar programs. For line-buffered programs, include `\n` at the end of each line.

```bash
# Start a process that waits for stdin.
curl -X POST "http://localhost:8080/v1/bash/exec" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "cat",
    "async_mode": true,
    "hard_timeout": 120
  }'
```

```bash
# Write one line of input.
curl -X POST "http://localhost:8080/v1/bash/write" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID",
    "input": "hello from stdin\n"
  }'
```

```bash
# Read the echoed output.
curl -X POST "http://localhost:8080/v1/bash/output" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID",
    "offset": 0,
    "wait": true,
    "wait_timeout": 5
  }'
```

Some programs write prompts to `stderr`, including some REPLs and interactive commands. Consumers should inspect both `stdout` and `stderr`.

## Session State

`/v1/bash` creates a new process for each `exec`. The same `session_id` preserves API-level state, such as the default working directory, but command-internal `cd` and `export` calls do not affect later requests.

Set the session default working directory with `exec_dir`:

```bash
curl -X POST "http://localhost:8080/v1/bash/exec" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "pwd",
    "exec_dir": "/tmp"
  }'
```

Reuse the same session:

```bash
curl -X POST "http://localhost:8080/v1/bash/exec" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID",
    "command": "pwd && echo ${MY_VAR:-unset}"
  }'
```

If later commands should continue in a directory, pass `exec_dir` again or update the API-level session default. Do not rely on `cd` inside a command.

## Parameters

Common `POST /v1/bash/exec` parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| `command` | string | Shell command to execute |
| `session_id` | string | Target session; auto-created when omitted |
| `exec_dir` | string | Absolute working directory; updates the session default |
| `env` | object | Extra environment variables for this command only |
| `async_mode` | boolean | Return `running` immediately when `true` |
| `timeout` | number | Soft timeout; returns `running` while the command continues in the background |
| `hard_timeout` | number | Hard timeout; kills the process and returns `timed_out` |
| `max_output_length` | number | Maximum inline `stdout` / `stderr` length for sync responses; default `50000`, set `0` to disable truncation for the request |

Common `POST /v1/bash/output` parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| `session_id` | string | Target session |
| `command_id` | string | Optional target async command |
| `offset` | number | stdout byte offset to read from |
| `stderr_offset` | number | stderr byte offset to read from |
| `wait` | boolean | Whether to long-poll for new output |
| `wait_timeout` | number | Maximum wait time when `wait=true` |

## Error Handling

HTTP success for `/v1/bash` means the request was accepted by the service. It does not mean the command itself succeeded. Recommended order:

1. Check the HTTP status code.
2. Check response `success`.
3. Use `data.status` for the command lifecycle.
4. When `status="completed"`, use `exit_code` for command success.

```python
import requests

response = requests.post(
    "http://localhost:8080/v1/bash/exec",
    json={"command": "python3 missing.py", "timeout": 30},
)
response.raise_for_status()

payload = response.json()
result = payload["data"]

if result["status"] == "running":
    print("command is still running; call /v1/bash/output")
elif result["status"] == "completed" and result["exit_code"] != 0:
    print("command completed with a non-zero exit code")
elif result["status"] in {"timed_out", "killed"}:
    print(f"command interrupted: {result['status']}")
```

## Related APIs

- `POST /v1/bash/exec`
- `POST /v1/bash/output`
- `POST /v1/bash/write`
- `POST /v1/bash/kill`
- `GET /v1/bash/sessions`
- `POST /v1/bash/sessions/create`
- `POST /v1/bash/sessions/{session_id}/close`
