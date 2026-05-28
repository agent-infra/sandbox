# Bash 管道

`/v1/bash` 是基于 subprocess pipe 的命令执行服务，适合 Agent 工具调用和程序化使用。它不同于基于 PTY 的 [Shell 终端](/zh/guide/basic/shell)：Bash 管道会分离 `stdout` / `stderr`，并支持按 offset 增量读取输出。

## Shell vs Bash

| | `/v1/shell` | `/v1/bash` |
| --- | --- | --- |
| 后端 | 终端 / PTY | subprocess pipe |
| 适合场景 | 交互式终端、WebSocket UI、人工接管 | Agent 工具调用、短命令、长命令轮询 |
| 输出 | 单一 `output` 字段 | 分离的 `stdout` 和 `stderr` |
| 读取方式 | 终端快照和等待 | `offset` / `stderr_offset` 增量读取 |
| stdin | 终端输入流 | 写入运行中进程的 stdin pipe |
| 命令标识 | session 维度 | 每条命令有 `command_id` |

## 执行短命令

大部分工具调用可以一次 `exec` 完成。`status` 表示命令生命周期，`exit_code` 才表示命令是否成功。

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

典型响应结构：

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

## SDK 示例

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

## 长命令与增量输出

当命令超过 `timeout` 仍未完成时，`/v1/bash/exec` 会返回 `status: "running"`，命令继续在后台执行。随后使用 `/v1/bash/output` 获取增量输出。

```bash
# 1. 启动命令；如果 1 秒内没有完成，会返回 running
curl -X POST "http://localhost:8080/v1/bash/exec" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "sleep 3; echo done",
    "timeout": 1,
    "hard_timeout": 30
  }'
```

```bash
# 2. 使用返回的 session_id、offset 和 stderr_offset 继续读取
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

`wait=false` 会立即返回当前已有输出；`wait=true` 会长轮询，直到有新输出、命令结束或 `wait_timeout` 到期。Agent 轮询长命令时推荐使用 `wait=true`，减少无意义的空轮询。

## 长驻进程

对不会自行退出的服务，使用 `async_mode: true` 立即返回，然后读取启动日志，用完后调用 `/kill`。

```bash
curl -X POST "http://localhost:8080/v1/bash/exec" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "python3 -m http.server 3000 --directory /tmp",
    "async_mode": true,
    "hard_timeout": 3600
  }'
```

读取日志：

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

停止进程：

```bash
curl -X POST "http://localhost:8080/v1/bash/kill" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID",
    "signal": "SIGTERM"
  }'
```

## 写入 stdin

`/v1/bash/write` 会写入运行中进程的 stdin pipe。适合 `cat`、脚本提示输入、REPL 等场景。面向行缓冲程序时，输入末尾通常需要包含 `\n`。

```bash
# 启动一个等待 stdin 的进程
curl -X POST "http://localhost:8080/v1/bash/exec" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "cat",
    "async_mode": true,
    "hard_timeout": 120
  }'
```

```bash
# 写入一行输入
curl -X POST "http://localhost:8080/v1/bash/write" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID",
    "input": "hello from stdin\n"
  }'
```

```bash
# 读取刚写入的输出
curl -X POST "http://localhost:8080/v1/bash/output" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID",
    "offset": 0,
    "wait": true,
    "wait_timeout": 5
  }'
```

有些程序会把提示符写到 `stderr`，例如部分 REPL 或交互式命令。接入时应同时读取 `stdout` 和 `stderr`。

## Session 状态

`/v1/bash` 是每次 `exec` 创建一个新进程的模型。同一 `session_id` 会保留 API 级状态，例如默认工作目录；但命令内部的 `cd`、`export` 不会影响后续调用。

使用 `exec_dir` 设置 session 默认工作目录：

```bash
curl -X POST "http://localhost:8080/v1/bash/exec" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "pwd",
    "exec_dir": "/tmp"
  }'
```

复用同一 session：

```bash
curl -X POST "http://localhost:8080/v1/bash/exec" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID",
    "command": "pwd && echo ${MY_VAR:-unset}"
  }'
```

如果希望后续命令继续使用某个目录，请继续传 `exec_dir` 或在 API 层更新 session 默认目录，不要依赖命令内部的 `cd`。

## 参数速查

`POST /v1/bash/exec` 常用参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `command` | string | 要执行的 shell 命令 |
| `session_id` | string | 目标 session；不传会自动创建 |
| `exec_dir` | string | 工作目录，必须是绝对路径；会更新 session 默认目录 |
| `env` | object | 仅对本次命令生效的环境变量 |
| `async_mode` | boolean | 为 `true` 时立即返回 `running` |
| `timeout` | number | 软超时；超时后返回 `running`，命令后台继续 |
| `hard_timeout` | number | 硬超时；到期后终止进程，状态为 `timed_out` |
| `max_output_length` | number | 同步响应里 `stdout` / `stderr` 的最大长度；默认 `50000`，设为 `0` 可关闭本次截断 |

`POST /v1/bash/output` 常用参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `session_id` | string | 目标 session |
| `command_id` | string | 可选，指定某条异步命令 |
| `offset` | number | 从哪个 stdout offset 开始读 |
| `stderr_offset` | number | 从哪个 stderr offset 开始读 |
| `wait` | boolean | 是否长轮询等待新输出 |
| `wait_timeout` | number | `wait=true` 时的最长等待秒数 |

## 错误处理

`/v1/bash` 的 HTTP 成功只表示请求被服务接受，不表示命令本身成功。推荐判断顺序：

1. 先看 HTTP 状态码。
2. 再看响应体里的 `success`。
3. 读取 `data.status` 判断命令生命周期。
4. 当 `status="completed"` 时，再用 `exit_code` 判断命令是否成功。

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

## 相关接口

- `POST /v1/bash/exec`
- `POST /v1/bash/output`
- `POST /v1/bash/write`
- `POST /v1/bash/kill`
- `GET /v1/bash/sessions`
- `POST /v1/bash/sessions/create`
- `POST /v1/bash/sessions/{session_id}/close`
