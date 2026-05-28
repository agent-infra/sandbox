# 统一代码执行

`/v1/code/execute` 提供统一代码执行入口。沙盒会根据语言把代码路由到对应运行时。

## 支持的运行时

| 语言 | 运行时 |
| --- | --- |
| Python | Jupyter kernel |
| JavaScript | Node.js |

如果需要运行时专属的会话管理或高级参数，请使用 [Jupyter](/zh/guide/basic/jupyter) 或 [Node.js](/zh/guide/basic/nodejs) API。

## 执行 Python

```bash
curl -X POST "http://localhost:8080/v1/code/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "python",
    "code": "print(sum([1, 2, 3]))"
  }'
```

## 执行 JavaScript

```bash
curl -X POST "http://localhost:8080/v1/code/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "javascript",
    "code": "console.log([1, 2, 3].reduce((a, b) => a + b, 0));"
  }'
```

## 运行时信息

```bash
curl "http://localhost:8080/v1/code/info"
```

## 错误处理

请求成功不代表代码执行成功。调用方仍需检查响应中的执行状态和输出字段。详见 [错误处理](/zh/guide/basic/error-handling)。

