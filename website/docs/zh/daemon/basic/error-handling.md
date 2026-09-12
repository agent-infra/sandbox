# 错误处理

错误可能出现在四层：HTTP 状态码、统一返回结构、JSON-RPC 的 `error` 对象，以及 MCP `tools/call` 结果中的 `isError` 标记。

通常按以下顺序检查，再看具体 API 的字段：命令看 `status` 和 `exit_code`，文件看 `data.error_type`，代码单元看 `outputs`。流式接口例外：WebSocket 可能在握手成功后才报告错误。

## 失败位置

不同 plane 的失败表现并不相同，这是有意设计的。例如，退出码为 `1` 表示命令已经执行，只是命令本身失败；而不存在的文件则根本没有读成功。

| Plane | 操作失败时返回 | 接着读 |
| --- | --- | --- |
| 文件，v2 | 表达失败类别的状态码 | `data.error_type`、`data.errno_name` |
| 文件，v1 | `200` 加 `success: false` | `data.error_type`、`data.errno_name` |
| Watch | `404`、`400`、`429` 或 `503` | `message` |
| 命令、终端 | `200` 加 `success: true` | `data.status`，然后 `exit_code` |
| 代码、Node.js、Jupyter | `200` 加 `success: false` | `data.status`、`outputs[].ename` |
| 浏览器 | 没有 CDP 是 `503`，选择器匹配不到元素是 `404` | `message` |
| 桌面 GUI | 没有 worker 是 `503`，操作系统拒绝输入是 `403` | `data.reason` |
| 下载 | 成功返回原始字节，失败返回状态码 | 状态码 |
| MCP 工具 | `200`，结果上带 `isError: true` | `content` 里的文本 |

- 非零退出码不是传输层错误。例如执行 `exit 3` 时，`POST /v2/commands` 仍返回 `200`、`success: true`、`status: "completed"` 和 `exit_code: 3`。
- 如果等待时间到了但命令仍在运行，返回 `status: "running"`，而不是超时错误。
- 代码单元失败时，响应返回 `200` 和 `success: false`，`data.status` 为 `"error"`，错误信息在 `outputs` 的 traceback 中。
- 不存在的会话或命令 id，在各执行 API 上都返回 `404`。
  WebSocket 会先以 `101` 完成握手，再发送 `{"type": "error", "data": "Session not found"}` 并关闭连接。监听器的 SSE 流会在建立连接前返回 `404`。

## 返回结构

v1 和大多数 v2 接口共用同一个返回结构：

```json
{
  "success": true,
  "message": "Operation successful",
  "data": {},
  "hint": null
}
```

`success: false` 表示 aiod 已理解请求，但操作失败。此时读取 `message`；如果 `hint` 不为空，也一并读取。它不是传输层错误。

## 校验错误

请求未通过 schema 校验时返回 `422`，每个 plane 都一样：

```json
{
  "success": false,
  "message": "Request data validation failed",
  "data": null,
  "errors": [
    {
      "location": [
        "body",
        "command"
      ],
      "message": "missing field `command` at line 1 column 2",
      "type": "value_error.missing"
    }
  ]
}
```

query 字段使用同一套校验。字段缺失时，`location` 是 `["query", "path"]`；类型错误时，`location` 只有 `["query"]`。

反序列化器会给出错误原因（例如 `invalid digit found in string`），但不会指出具体字段名。

请求体缺失按 `{}` 处理：字段全是可选的路由可以不带 body 调用，带必填字段的路由则返回校验错误。

## 文件错误

文件接口的失败带一个结构化的 `data` 对象，而不是一段 message 文本：

```json
{
  "success": false,
  "message": "Failed to read file: No such file or directory (os error 2)",
  "data": {
    "errno": 2,
    "errno_name": "ENOENT",
    "error_type": "not_found",
    "exception_type": "FileNotFoundError",
    "message": "Failed to read file: No such file or directory (os error 2)",
    "operation": "read",
    "path": "/workspace/missing.txt",
    "retryable": false
  },
  "hint": null
}
```

`/v2/fs` 和 `/v1/file` 返回相同的 `data` 对象，区别只在外层 HTTP 状态码。

`retryable` 用来区分两类失败：锁被短暂占用等临时性失败，重试可能成功；路径写错等持续性失败，在修正原因前重试不会成功。

`error_type` 与状态码的对应关系见 [File（文件）](/zh/daemon/basic/file#错误处理)。

## HTTP 状态码约定

| 状态码 | 含义 | 典型场景 |
| --- | --- | --- |
| `400` | 参数或操作不合法 | `lang` 取值未知、锚点匹配到两处 |
| `401` | 未携带 key 或 key 无效 | 设置了 `AIO_API_KEY` 时访问任何受保护路由 |
| `403` | 这次操作被拒绝 | daemon 账户读不了的文件 |
| `404` | 路由或对象不存在 | 已下线的端点、未知的会话或命令 id |
| `409` | 目标已存在 | 复制或移动到已存在的路径 |
| `413` | 请求体过大 | 超过 8 MiB 的 MCP 调用、超过 4 GiB 的 tar body |
| `422` | 校验失败 | 请求体或 query 字段缺失、类型不对 |
| `429` | 数量达到上限 | 第 21 个原生代码会话 |
| `501` | 此 daemon 未实现 | 在 Windows 上调用仅 Linux 的路由 |
| `503` | 对应能力现在不可用 | 宿主机没有 bash |

这些状态码在不同路由上可能有多种触发原因：

| 状态码 | 常见原因 |
| --- | --- |
| `400` | 参数或操作不合法：`lang` 取值未知、锚点不唯一，或尝试修改已有会话的 `user` |
| `403` | 权限不足：daemon 账户无法访问目标路径，或 Windows secure desktop 拒绝模拟输入；后者的响应中 `data.status` 为 `denied` |
| `422` | 请求参数或文本格式不正确：query 字段缺失或类型错误、不支持的 `language`，或读取非 UTF-8 文件 |
| `429` | 资源数量超限：第 6 个 kernel 会话、第 21 个原生代码会话，或第 129 个文件监听器 |
| `501` | 功能不可用：未安装 `ipykernel` 时调用 `/v1/jupyter/*`，或对内嵌 kernel 调用 `interrupt`/`restart` |
| `503` | 依赖的能力暂不可用或等待超时：没有解释器、computer-use worker 已停止、没有 display，或 `wait` 超时 |

## MCP 工具错误

`tools/call` 在工具内部失败时，仍返回正常的 JSON-RPC 结果，只是带有 `isError` 标记。这不是 HTTP 错误：传输成功了，但工具执行失败。

`isError` 包括以下情况：

- 参数缺失或非法，例如 `sandbox_execute_bash` 不带 `cmd` 时返回 `cmd is required`。
- 文件 API 的任何失败，此时结构化错误对象会作为结果文本返回。
- CDP 端口无响应时调用 `browser_get_info`，或没有 computer-use worker 时调用 `browser_gui_screenshot`、`browser_gui_execute_action`。
- 调用 `EXTRA_MCP_SERVERS` 中已停止的上游。此类上游也不会出现在 `tools/list` 中。

名字不存在则属于协议错误：`/mcp` 返回 `200`，响应体是 JSON-RPC 的 `error` 对象，方法名不存在是 `-32601`，工具名不存在是 `-32602`。请求体不是 JSON 则是 `-32700`。

## 客户端处理

返回结构和 plane 自己的执行结果是两层信息，都需要检查。客户端通常只负责处理 `success: false`；退出码和代码单元状态仍需由调用方读取：

```python
from agent_sandbox import Sandbox

client = Sandbox(base_url="http://127.0.0.1:18091")

missing = client.file.read_file(file="/tmp/demo/missing.txt")
print(missing.success, missing.data.error_type, missing.data.retryable)
# False not_found False

command = client.bash.exec(command="exit 3").data
print(command.status, command.exit_code)
# completed 3

cell = client.code.execute_code(language="python", code="1/0")
print(cell.success, cell.data.status, cell.data.outputs[0]["ename"])
# False error ZeroDivisionError
```

同样三次读取的 TypeScript 版本：

```ts
import { SandboxClient } from "@agent-infra/sandbox";

const client = new SandboxClient({ environment: "http://127.0.0.1:18091" });

const missing = await client.file.readFile({ file: "/tmp/demo/missing.txt" });
const failure = missing.body?.data as any;
console.log(missing.body?.success, failure.error_type, failure.retryable);
// false not_found false

const run = await client.bash.exec({ command: "exit 3" });
const command = run.body?.data as any;
console.log(command.status, command.exit_code);
// completed 3

const cell = await client.code.executeCode({ language: "python", code: "1/0" });
const result = cell.body?.data as any;
console.log(cell.body?.success, result.status, result.outputs[0].ename);
// false error ZeroDivisionError
```

遇到 `retryable: true` 或 `503` 可以重试；`429` 则应退避后再试。`400`、`404`、`409` 和 `422` 通常不会自行恢复，直接重试没有意义。

## 相关页面

- [File（文件）](/zh/daemon/basic/file) —— 结构化文件错误及其状态码
- [Commands（命令执行）](/zh/daemon/basic/bash) —— 命令生命周期和退出码
- [Terminals（PTY 终端）](/zh/daemon/basic/shell) —— 会话和流式接口的失败
- [鉴权](/zh/daemon/basic/authentication) —— 什么情况返回 `401`
