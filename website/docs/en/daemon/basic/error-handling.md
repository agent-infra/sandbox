# Error Handling

Errors can appear in four layers: the HTTP status, the standard envelope, the JSON-RPC `error` object, and the `isError` flag on an MCP `tools/call` result.

Check them in that order, then read the API's own fields: `status` and `exit_code` for commands, `data.error_type` for files, and `outputs` for code cells. Streaming is the exception: a WebSocket can report an error after the handshake succeeds.

## Where a failure shows up

Different planes report failures differently, by design. An exit code of `1` means the command ran and failed; a missing file was never read successfully.

| Plane | A failed operation answers | Then read |
| --- | --- | --- |
| Files, v2 | A status naming the failure | `data.error_type`, `data.errno_name` |
| Files, v1 | `200` with `success: false` | `data.error_type`, `data.errno_name` |
| Watch | `404`, `400`, `429`, or `503` | `message` |
| Commands, terminals | `200` with `success: true` | `data.status`, then `exit_code` |
| Code, Node.js, Jupyter | `200` with `success: false` | `data.status`, `outputs[].ename` |
| Browser | `503` without CDP, `404` for a selector that matches nothing | `message` |
| Desktop | `503` without a worker, `403` when the OS refused the input | `data.reason` |
| Download | Raw bytes on success, a status on failure | The status |
| MCP tools | `200` with `isError: true` on the result | The `content` text |

- A non-zero exit code is not a transport error. Running `exit 3` at `POST /v2/commands` still answers `200`, `success: true`, `status: "completed"`, and `exit_code: 3`. If the wait expires while the command is still running, the answer is `status: "running"`, not a timeout error.
- A failed code cell returns `200` and `success: false`; `data.status` is `"error"`, and the traceback is in `outputs`.
- A missing session or command id answers `404` on every execution API. WebSocket is different: the handshake still completes with `101`, then the socket receives `{"type": "error", "data": "Session not found"}` and closes. A watcher's SSE stream returns `404` before opening.

## Response envelope

v1 and most v2 responses share one shape:

```json
{
  "success": true,
  "message": "Operation successful",
  "data": {},
  "hint": null
}
```

`success: false` means aiod understood the request, but the operation failed. Read `message`, and read `hint` when it is not null. This is not a transport error.

## Validation errors

A request that fails schema validation answers `422`, whatever the plane:

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

A query field uses the same validation. `location` is `["query", "path"]` when the field is missing, and `["query"]` alone for a type error. The deserializer gives the reason (for example, `invalid digit found in string`) but not the field name.

An absent request body reads as `{}`: a route whose fields are all optional accepts a call with no body, and one with a required field answers as above.

## File errors

File-plane failures carry a structured `data` object, not a bare message:

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

The `data` object is the same on `/v2/fs` and `/v1/file`; only the outer HTTP status differs.

`retryable` distinguishes two kinds of failure. A transient one, such as a briefly held lock, may succeed on retry. A persistent one, such as a bad path, will fail again until its cause is fixed. The `error_type` to status mapping is in [File (FS)](/daemon/basic/file#error-handling).

## HTTP status conventions

| Status | Meaning | Example |
| --- | --- | --- |
| `400` | A value the route rejects | An unknown `lang`, an anchor matching twice |
| `401` | No or wrong API key | Any protected route while `AIO_API_KEY` is set |
| `403` | The operation was refused | A file the daemon's account may not read |
| `404` | No such route or object | A removed endpoint, an unknown session or command id |
| `409` | The target already exists | A copy or move onto an existing path |
| `413` | The body is too large | An MCP call over 8 MiB, a tar body over 4 GiB |
| `422` | Failed validation | A missing or mistyped body or query field |
| `429` | Capacity reached | A 21st native code session |
| `501` | Not implemented on this daemon | A Linux-only route called on Windows |
| `503` | The capability is not available right now | No bash on the host |

These codes can have different causes depending on the route:

| Code | Common causes |
| --- | --- |
| `400` | Invalid parameter or operation: an unknown `lang`, a non-unique anchor, or changing `user` on an existing session |
| `403` | Permission denied: the daemon account cannot access the path, or Windows secure desktop rejects simulated input; the latter sets `data.status` to `denied` |
| `422` | Invalid request or text format: a missing or mistyped query field, an unsupported `language`, or reading a non-UTF-8 file as text |
| `429` | Resource limit exceeded: a 6th kernel session, a 21st native code session, or a 129th file watcher |
| `501` | Feature unavailable: `/v1/jupyter/*` without `ipykernel`, or `interrupt`/`restart` on the embedded kernel |
| `503` | A required capability is unavailable or the wait timed out: no interpreter, a stopped computer-use worker, no display, or a timed-out `wait` |

## MCP tool errors

A `tools/call` that fails inside the tool still returns a normal JSON-RPC result, with `isError` set. This is not an HTTP error: the transport succeeded, but the tool did not.

`isError` includes:

- A missing or invalid argument, such as `sandbox_execute_bash` without `cmd`, which answers `cmd is required`.
- Any file API failure; the structured error object arrives as the result text.
- `browser_get_info` with nothing on the CDP port, or `browser_gui_screenshot` and `browser_gui_execute_action` without a running computer-use worker.
- A call to a stopped `EXTRA_MCP_SERVERS` upstream. Its tools are also absent from `tools/list`.

A name that does not exist is a protocol error instead: `/mcp` answers `200` with a JSON-RPC `error` object, `-32601` for an unknown method and `-32602` for an unknown tool. A body that is not JSON is `-32700`.

## Client pattern

The envelope and the plane's own outcome are separate checks. A client can handle `success: false`; the caller still reads the exit code and cell status:

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

The same three reads in TypeScript:

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

Retry `retryable: true` and `503`; retry `429` after a pause. Retrying `400`, `404`, `409`, or `422` unchanged is usually pointless because nothing on the daemon side will change.

## Related

- [File (FS)](/daemon/basic/file) — the structured file error and its statuses
- [Commands (Bash)](/daemon/basic/bash) — command lifecycle and exit codes
- [Terminals (PTY)](/daemon/basic/shell) — session and stream failures
- [Authentication](/daemon/basic/authentication) — what answers `401`
