# CDP 接入

aiod 里的 CDP（Chrome DevTools Protocol，Chrome 开发者工具协议）接入分为两部分：daemon 作为客户端连接 Chromium；daemon 前面的反向代理负责把 Chromium 的调试端口暴露给外部。

daemon 只负责连接 Chromium。下面说明这部分职责，以及部署方需要提供的另一部分能力。

## daemon 的职责

- 连接 `BROWSER_REMOTE_DEBUGGING_HOST:PORT`（默认 `127.0.0.1:9222`），供自己的浏览器工具、能力探测和浏览器 MCP 工具使用。
- 响应 `GET /v1/browser/info`，其中的 `cdp_url` 由请求头 `X-Forwarded-Proto`、`X-Forwarded-Host`、`X-Forwarded-Prefix` 拼出，缺失时回退到 `Host`。格式：`<scheme>://<host><prefix>/cdp/devtools/browser/<id>`。

daemon 不提供 `/cdp/*`。

`cdp_url` 的格式固定为沙箱公开地址下的 `/cdp/` 路径，但具体由哪个代理提供这条路径取决于部署方式。

## 为什么要由代理提供 `/cdp/*`

反向代理需要完成两件事：提供 `/cdp/json/*`，以及转发 `/cdp/devtools/*` 的 WebSocket。

- 发现接口只是字符串替换：Chromium 的 `/json/version` 和 `/json/list` 返回以 `ws://127.0.0.1:9222/` 开头的 URL。代理把该前缀换成公开 origin 加 `/cdp/`，`devtoolsFrontendUrl` 里的 `ws=` 形式同样处理。
- DevTools WebSocket 只是普通转发：`/cdp/devtools/<rest>` 变成 9222 端口上的 `/devtools/<rest>`。`Upgrade` 请求头会原样转发，并设置较长的读取超时。

要让替换生效，还需要满足两个条件：

- Chromium 会拒绝 `Host` 不是 IP 或 `localhost` 的 `/json/*` 请求。代理向上游发送 `Host: 127.0.0.1:9222`。
- 响应体必须是未压缩的，替换才看得到内容。代理向上游发送空的 `Accept-Encoding`。

## 预构建镜像中的 CDP

AIO 镜像和 Computer 镜像里的 nginx 实现了这两个 location，配置如下：

```nginx
location /cdp/json/ {
    rewrite ^/cdp(/.*)$ $1 break;
    proxy_pass http://127.0.0.1:9222;
    proxy_set_header Host 127.0.0.1:9222;
    proxy_set_header Accept-Encoding "";
    sub_filter_types application/json;
    sub_filter_once off;
    sub_filter 'ws://127.0.0.1:9222/' '$cdp_scheme://$cdp_host$cdp_prefix/cdp/';
    sub_filter 'ws=127.0.0.1:9222/' 'ws=$cdp_host$cdp_prefix/cdp/';
}

location ~ ^/cdp/devtools/ {
    rewrite ^/cdp(/.*)$ $1 break;
    proxy_pass http://127.0.0.1:9222;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $connection_upgrade;
}
```

`$cdp_scheme`、`$cdp_host` 和 `$cdp_prefix` 由 `X-Forwarded-*` 请求头推导。

即使 daemon 位于第二层代理或带路径前缀的 ingress 后面，`cdp_url` 仍然正确。

例如，设置以下请求头：

```text
X-Forwarded-Proto: https
X-Forwarded-Host: sandbox.example.com
X-Forwarded-Prefix: /s/abc
```

此时，`info` 返回 `wss://sandbox.example.com/s/abc/cdp/devtools/browser/<id>`。

## 没有 nginx 时

没有镜像网关时，由部署方自己的反向代理完成同样的工作。Windows 上也需要在主机前配置反向代理。

代理需要重写发现接口返回的 JSON，并按同样的请求头规则把 `/cdp/devtools/*` 转发到 9222 端口。

只要代理能够转发 WebSocket、改写响应体，并提供 `X-Forwarded-*` 请求头即可。

## 通过路径或端口访问

`cdp_url` 使用路径形式，例如 `wss://sandbox.example.com/cdp/devtools/browser/<id>`。

Playwright 的 `connect_over_cdp` 和 Puppeteer 的 `browserWSEndpoint` 可以直接使用该地址。Playwright 也接受 `{base_url}/cdp` 作为 HTTP 端点，并会自动追加 `json/version/`，同时保留 query 参数。

有些客户端只接受不带路径的 `http://host:port`：

- Puppeteer 的 `browserURL`
- chrome-devtools-mcp 的 `--browserUrl`
- Selenium
- OSWorld

这些客户端需要端口形式的接入：主机名直接指向 Chromium 的 9222 端口。为每个沙箱分配独立主机名的部署，可以把该端口暴露成子域名或专用监听地址，仍由同一个代理转发到 9222。

这两种形式都不经过 daemon。aiod 的浏览器工具始终连接 `BROWSER_REMOTE_DEBUGGING_PORT`，无论该地址对应的是 Chromium 还是转发器。

## 密钥

浏览器端的 WebSocket 无法设置请求头，因此网关要求 key 时，需要在 `cdp_url` 后追加 `?api_key=<key>`。

调用 `info` 时，如果请求带有查询参数，返回的两个 URL 都会保留这些参数。因此 `GET /v1/browser/info?api_key=<key>` 返回的 `cdp_url` 可以直接连接。规则与其他 WebSocket 路由相同。

不要把 9222 端口暴露到可信网络之外：Chromium 的调试端口没有任何鉴权。

## 相关页面

- [浏览器 API](/zh/daemon/basic/browser) —— REST 工具和客户端示例
- [浏览器（CDP）示例](/zh/daemon/examples/browser-cdp) —— Playwright 和 Puppeteer 完整流程
