# Node.js

AIO Sandbox 内置 Node.js 运行时，适合 JavaScript 脚本、JSON 处理、Web 工具链和基于 JavaScript 的自动化。

## 无状态执行

```bash
curl -X POST "http://localhost:8080/v1/nodejs/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "console.log(process.version); console.log(JSON.stringify({ ok: true }));"
  }'
```

## 有状态会话

如果后续请求需要复用前一次变量，可以指定 session：

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

## 运行时信息

```bash
curl "http://localhost:8080/v1/nodejs/info"
```

## 会话管理

```bash
curl "http://localhost:8080/v1/nodejs/sessions"
curl -X DELETE "http://localhost:8080/v1/nodejs/sessions/js-repl"
```

## 如何选择接口

- JavaScript 专属执行使用 `/v1/nodejs/execute`。
- Agent 动态选择语言时使用 `/v1/code/execute`。
- 需要执行 `npm install` 等 Shell 命令时使用 `/v1/bash/exec`。

