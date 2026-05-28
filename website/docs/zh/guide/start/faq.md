# 常见问题

本 FAQ 面向开源 Docker 与 SDK 使用方式。

## Docker

### 8080 端口被占用怎么办？

把容器端口映射到另一个宿主机端口：

```bash
docker run --security-opt seccomp=unconfined --rm -it -p 3000:8080 ghcr.io/agent-infra/sandbox:latest
```

之后将沙盒地址配置为 `http://localhost:3000`。

### 浏览器启动失败怎么办？

先确认容器有足够内存，并使用推荐的 seccomp 参数启动：

```bash
docker run --security-opt seccomp=unconfined --rm -it -p 8080:8080 ghcr.io/agent-infra/sandbox:latest
```

如果运行在受限容器环境中，还需要检查 Chromium 沙箱能力和共享内存限制。

## SDK 与 API

### SDK 连接不上怎么办？

确认 `base_url` 指向了正确的宿主机端口：

```python
from agent_sandbox import Sandbox

client = Sandbox(base_url="http://localhost:8080")
print(client.sandbox.get_context())
```

### 错误应该怎么处理？

建议分层处理：

- 非 2xx HTTP 响应通常表示传输、参数、鉴权或服务错误。
- JSON 响应里的 `success: false` 表示工具级失败。
- 执行类接口还需要继续查看 `status`、`exit_code` 或 stderr 输出。

详见 [错误处理](/zh/guide/basic/error-handling)。

## 浏览器

### 截图正常，但自动化操作失败怎么办？

检查页面是否加载完成、目标元素是否可见，以及所选接口是否适合任务。DOM 级操作优先使用 CDP 或 page API，视觉桌面级操作使用 GUI actions。

### 下载的文件在哪里？

Chromium 默认会把文件下载到用户下载目录，例如 `/home/gem/Downloads`。可以通过文件 API 查看或下载这些文件。

## MCP

### 还需要单独启动 MCP Server 吗？

不需要。AIO Sandbox 已经在 `/mcp` 暴露聚合 MCP 入口，兼容 MCP 的客户端可以直接连接。

### 为什么有些底层浏览器工具默认看不到？

默认 MCP 入口优先暴露常用工具。除非需要底层 CDP 行为，否则建议优先使用文档中的浏览器 API 或高层 MCP 工具。

## 定制

### 如何预装依赖？

基于公开 AIO Sandbox 镜像构建自定义镜像，在 Dockerfile 中安装依赖即可。只需要启动时配置时，也可以使用 [AIO Hooks](/zh/guide/advanced/lifecycle)。

### 如何设置默认工作目录？

启动容器时设置 `WORKSPACE`。详见 [工作目录](/zh/guide/advanced/workspace)。
