# 代理与网络

AIO Sandbox 支持出站代理配置，也支持把容器内运行的服务通过主 HTTP 端口反向代理出来进行预览。

## 出站代理

当浏览器或工具流量需要经过上游 HTTP/HTTPS 代理时，设置 `PROXY_SERVER`：

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 127.0.0.1:8080:8080 \
  -e PROXY_SERVER=http://proxy.example.com:3128 \
  ghcr.io/agent-infra/sandbox:latest
```

可选的包含和排除列表：

```bash
-e PROXY_EXCLUDE=localhost,127.0.0.1,.example.org
-e PROXY_INCLUDE=.example.com
```

## 入站预览代理

在沙盒内启动的应用，可以通过主 HTTP 端口预览。

路径代理：

```text
http://localhost:8080/proxy/3000/
http://localhost:8080/absproxy/3000/
```

后端服务优先使用 `/proxy/{port}/`，前端应用如果依赖绝对路径，可使用 `/absproxy/{port}/`。

请求头代理：

```bash
curl -H 'x-aio-proxy-port: 3000' \
  http://localhost:8080/
```

`x-aio-proxy-port` 适合由公网网关或自建反向代理注入，用于不方便通过子域名表达端口的环境。沙盒会把请求转发到 `127.0.0.1:<port>`，并在转发给目标服务前移除该控制 header。该 header 应由可信代理覆盖设置，不建议直接信任终端用户传入的同名 header。

## 运行时代理 API

代理也可以通过 REST 端点查看和更新：

- `GET /v1/proxy/health`
- `GET /v1/proxy/upstream`
- `GET /v1/proxy/mappings`
- `POST /v1/proxy/mappings`
- `DELETE /v1/proxy/mappings/{source}`

## 建议

- 本地开发流量能直连时尽量不经过上游代理。
- 需要可复现配置时优先使用环境变量。
- 单次任务的临时映射可使用运行时 API。
