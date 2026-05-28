# Error Handling

AIO Sandbox APIs expose several layers of errors. A robust client should not rely on HTTP status alone.

## Recommended Order

1. Check the HTTP status code.
2. If the response is JSON, check `success`.
3. For execution APIs, inspect domain fields such as `status`, `exit_code`, `stdout`, and `stderr`.
4. For WebSocket and streaming APIs, handle connection close and partial output separately.

## HTTP Errors

Common HTTP failures include:

| Status | Meaning |
| --- | --- |
| `400` | Invalid request or failed validation |
| `401` / `403` | Missing or invalid authentication |
| `404` | Endpoint or target resource not found |
| `422` | Request body validation failed |
| `500+` | Sandbox service error |

## Tool-Level Errors

Some APIs can return HTTP 200 while reporting a tool failure:

```json
{
  "success": false,
  "message": "command failed",
  "data": null
}
```

Treat `success: false` as a handled operation failure. Show `message` to the user or pass it back to your agent.

## Execution Errors

Shell, Bash, Jupyter, Node.js, and unified code execution may return process-level details:

```json
{
  "success": true,
  "data": {
    "status": "finished",
    "exit_code": 1,
    "stdout": "",
    "stderr": "command not found"
  }
}
```

For these APIs, `success: true` only means the sandbox handled the request. The executed command or code can still fail.

## Client Pattern

```python
def assert_sandbox_response(response):
    if getattr(response, "success", True) is False:
        raise RuntimeError(response.message)

    data = getattr(response, "data", None)
    if data is not None and getattr(data, "exit_code", 0) not in (0, None):
        raise RuntimeError(getattr(data, "stderr", "execution failed"))

    return data
```

## Further Reading

- [Bash Pipe](/guide/basic/bash)
- [Shell Terminal](/guide/basic/shell)
- [Unified Code Execution](/guide/basic/code)
- [Authentication](/guide/basic/authentication)
