# Unified Code Execution

`/v1/code/execute` provides a single entry point for running code. The sandbox routes supported languages to the matching runtime.

## Supported Runtimes

| Language | Runtime |
| --- | --- |
| Python | Jupyter kernel |
| JavaScript | Node.js |

Use the dedicated [Jupyter](/guide/basic/jupyter) or [Node.js](/guide/basic/nodejs) APIs when you need runtime-specific session management or advanced options.

## Execute Python

```bash
curl -X POST "http://localhost:8080/v1/code/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "python",
    "code": "print(sum([1, 2, 3]))"
  }'
```

## Execute JavaScript

```bash
curl -X POST "http://localhost:8080/v1/code/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "javascript",
    "code": "console.log([1, 2, 3].reduce((a, b) => a + b, 0));"
  }'
```

## Runtime Info

```bash
curl "http://localhost:8080/v1/code/info"
```

## Error Handling

Successful request handling does not guarantee successful code execution. Check the returned execution status and output fields. See [Error Handling](/guide/basic/error-handling).

