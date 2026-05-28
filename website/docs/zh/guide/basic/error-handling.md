# 错误处理

AIO Sandbox 的 API 错误是分层的。稳健的客户端不应只依赖 HTTP 状态码。

## 推荐顺序

1. 先检查 HTTP 状态码。
2. 如果响应是 JSON，继续检查 `success`。
3. 对执行类接口，继续检查 `status`、`exit_code`、`stdout`、`stderr` 等领域字段。
4. 对 WebSocket 和流式接口，单独处理连接关闭与部分输出。

## HTTP 错误

常见 HTTP 错误包括：

| 状态码 | 含义 |
| --- | --- |
| `400` | 请求非法或业务校验失败 |
| `401` / `403` | 缺少鉴权或鉴权无效 |
| `404` | 路由或目标资源不存在 |
| `422` | 请求体校验失败 |
| `500+` | 沙盒服务内部错误 |

## 工具级错误

部分接口可能返回 HTTP 200，但工具执行失败：

```json
{
  "success": false,
  "message": "command failed",
  "data": null
}
```

应将 `success: false` 视为已处理的业务失败，并把 `message` 展示给用户或传回 Agent。

## 执行错误

Shell、Bash、Jupyter、Node.js 和统一代码执行接口会返回进程级信息：

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

这类接口中，`success: true` 只表示沙盒成功处理了请求，命令或代码本身仍可能失败。

## 客户端模式

```python
def assert_sandbox_response(response):
    if getattr(response, "success", True) is False:
        raise RuntimeError(response.message)

    data = getattr(response, "data", None)
    if data is not None and getattr(data, "exit_code", 0) not in (0, None):
        raise RuntimeError(getattr(data, "stderr", "execution failed"))

    return data
```

## 相关阅读

- [Bash 管道](/zh/guide/basic/bash)
- [Shell 终端](/zh/guide/basic/shell)
- [统一代码执行](/zh/guide/basic/code)
- [鉴权](/zh/guide/basic/authentication)
