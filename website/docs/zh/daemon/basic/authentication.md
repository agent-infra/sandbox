# 鉴权

aiod 只支持一个可选的启动期 key。

未设置 key 时，所有路由都会放行，aiod 处于完全开放状态。此时请将它绑定到 `127.0.0.1`，或放在自带鉴权的网关后面。

## 启动时设置 API key

命令行参数和环境变量设置的是同一个 key：

```bash
aiod start --api-key my-secret-key
# equivalently
AIO_API_KEY=my-secret-key aiod start
```

## 请求中携带 API key

三种等价形式：

```bash
curl "$BASE_URL/v1/sandbox" -H "Authorization: Bearer my-secret-key"
curl "$BASE_URL/v1/sandbox" -H "x-api-key: my-secret-key"
curl "$BASE_URL/v1/sandbox?api_key=my-secret-key"
```

| 通道 | 什么时候用 | 说明 |
| --- | --- | --- |
| `Authorization: Bearer` | HTTP 客户端的默认选择 | 标准的 bearer token |
| `x-api-key` | 客户端原本使用的 header | 预构建镜像的网关同时接受 `X-AIO-API-Key` |
| `?api_key=` | 只在没法带 header 时用 | 已废弃；比较前会先做 percent 解码 |

三种通道都用常数时间比较，所以 key 的长度和猜中了多少前缀都不会从响应耗时里泄漏出来。

URL 中的凭证可能出现在访问日志、浏览器历史和后续请求的 `Referer` 中。

因此，只有无法设置请求头时才使用 query 参数，例如浏览器原生 WebSocket 或 VNC 页面：

```text
{ws_base_url}/v1/shell/ws?session_id=SESSION_ID&api_key=my-secret-key
```

WebSocket 会在升级前完成鉴权。没有有效 key 时，握手直接返回 `401`，不会先建立连接再断开。

除下文列出的公开路由外，其他请求没有有效 key 时都返回 `401`，响应体使用统一结构：

```json
{
  "success": false,
  "message": "Unauthorized",
  "data": null,
  "hint": null
}
```

## 公开路由

以下路由跳过 key 校验：

- `/`
- `/health`
- `/v1/ping`
- `/v1/openapi.json`
- `/v2/openapi.json`
- `/internal/auth`

公开路径按前缀匹配。例如，`/health` 也会覆盖 `/health/details`；但 `/` 只覆盖自身，不会放行整个 API。

公开也不代表一定有响应内容：daemon 不提供 `/` 的内容，该路径通常留给网关放置首页。

设置 key 后其余路由都需要带 key，`/metrics` 也不例外——指标暴露的是路由名和流量形态，运维端点没有豁免。

## 放在网关后面

`/internal/auth` 是供 nginx `auth_request` 调用的子请求端点。它从 `X-Original-URI` 读取原始请求路径，并按同一套规则检查 key：

- 请求已获授权、目标是公开路径，或未配置 key 时，返回 `204`。
- 其他情况返回 `401`。
- 该端点始终不返回响应体。

这样，网关只需配置一个 `auth_request`，就能保护前面的所有入口，包括不经过 aiod 中间件的 VNC 流。

直接调用 `/internal/auth` 时没有 `X-Original-URI`，此时会改为检查当前请求自己的凭证。

## CORS

CORS 有意开放：aiod 自己不做 origin 校验，交由前面的网关处理。CDP 端口（默认 `9222`）不要暴露到不可信网络，它本身没有任何鉴权。

## 身份：执行身份与归属身份

请求里的 `user` 在不同接口上含义不同，`AIO_DEFAULT_USER` 提供同样的默认值：

> 在 commands、PTY 和 code 中，`user` 决定进程以哪个账户运行；在 files 中，它只决定新建对象归谁所有。

在 files 中，daemon 仍然以自己的权限读写文件，不会因为 `user` 改变执行权限。

这套语义只在 Linux 上生效。Windows 上显式传 `user` 返回 `400`，`AIO_DEFAULT_USER` 一旦生效就返回 `503`，详见 [Windows](/zh/daemon/basic/windows)。

## 相关页面

- [错误处理](/zh/daemon/basic/error-handling) —— `401` 与其他状态码的关系
- [可观测性](/zh/daemon/basic/observability) —— key 在请求日志里是脱敏的
- [File（文件）](/zh/daemon/basic/file#文件归属) —— 文件 API 中的文件归属
