# Node.js

AIO Sandbox includes a Node.js runtime for JavaScript execution. Use it for scripts, JSON processing, web tooling, and JavaScript-based automation.

## Stateless Execution

```bash
curl -X POST "http://localhost:8080/v1/nodejs/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "console.log(process.version); console.log(JSON.stringify({ ok: true }));"
  }'
```

## Stateful Sessions

Use a session when later requests need previous variables:

```bash
curl -X POST "http://localhost:8080/v1/nodejs/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "js-repl",
    "code": "globalThis.count = 1"
  }'

curl -X POST "http://localhost:8080/v1/nodejs/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "js-repl",
    "code": "globalThis.count += 1; console.log(globalThis.count)"
  }'
```

## Runtime Info

```bash
curl "http://localhost:8080/v1/nodejs/info"
```

## Session Management

```bash
curl "http://localhost:8080/v1/nodejs/sessions"
curl -X DELETE "http://localhost:8080/v1/nodejs/sessions/js-repl"
```

## Choosing An API

- Use `/v1/nodejs/execute` for JavaScript-specific execution.
- Use `/v1/code/execute` when your agent chooses the language dynamically.
- Use `/v1/bash/exec` when you need shell commands such as `npm install`.

