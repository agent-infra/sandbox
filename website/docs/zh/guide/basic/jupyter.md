# Jupyter

AIO Sandbox 内置 Jupyter kernel 执行能力，适合 Python 数据处理、图表生成、Notebook 兼容和有状态 Python 工作流。

## 执行代码

```bash
curl -X POST "http://localhost:8080/v1/jupyter/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "x = 40 + 2\nprint(x)"
  }'
```

## 有状态会话

使用 `session_id` 可以在多次请求之间保留变量：

```bash
curl -X POST "http://localhost:8080/v1/jupyter/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "analysis",
    "code": "data = [1, 2, 3]"
  }'

curl -X POST "http://localhost:8080/v1/jupyter/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "analysis",
    "code": "print(sum(data))"
  }'
```

## 内核信息

```bash
curl "http://localhost:8080/v1/jupyter/info"
```

## 会话管理

```bash
curl "http://localhost:8080/v1/jupyter/sessions"
curl -X DELETE "http://localhost:8080/v1/jupyter/sessions/analysis"
```

## 使用建议

- Python 代码需要变量状态或富输出时，优先使用 Jupyter。
- 需要语言无关入口时，使用 `/v1/code/execute`。
- 生成文件建议写入工作目录，便于浏览器、Shell 和文件 API 共享访问。

