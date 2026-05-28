# Jupyter

AIO Sandbox includes Jupyter kernel execution for Python code. It is useful for data processing, charts, notebooks, and stateful Python workflows.

## Execute Code

```bash
curl -X POST "http://localhost:8080/v1/jupyter/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "x = 40 + 2\nprint(x)"
  }'
```

## Stateful Sessions

Use `session_id` to keep variables across requests:

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

## Kernel Info

```bash
curl "http://localhost:8080/v1/jupyter/info"
```

## Session Management

```bash
curl "http://localhost:8080/v1/jupyter/sessions"
curl -X DELETE "http://localhost:8080/v1/jupyter/sessions/analysis"
```

## Tips

- Use Jupyter for Python code that benefits from stateful variables or rich output.
- Use `/v1/code/execute` when you want a language-neutral entry point.
- Store generated files in the workspace so browser, shell, and file APIs can access them.

