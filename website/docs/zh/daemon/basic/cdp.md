# CDP 接入

aiod 通过 CDP（Chrome DevTools Protocol，Chrome 开发者工具协议）连接已经启动的 Chromium。

如果要让外部客户端连接，还需要在 aiod 前配置反向代理，把 Chromium 的 `9222` 端口映射到公开地址。

## aiod 负责什么

aiod 连接 `BROWSER_REMOTE_DEBUGGING_HOST:PORT`，默认是 `127.0.0.1:9222`。

响应 `GET /v1/browser/info`，返回客户端连接 Chromium 所需的 `cdp_url`。如果服务经过反向代理，地址会使用代理后的公开地址。

aiod 不提供 `/cdp/*`，这部分由反向代理负责。

## nginx 配置

预构建镜像已经通过 nginx 配置好 CDP 路由，关键配置如下：

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

第一段处理 Chromium 返回的连接信息，并将地址改成公开地址；第二段转发 DevTools 的 WebSocket 连接。

`$cdp_scheme`、`$cdp_host` 和 `$cdp_prefix` 根据 `X-Forwarded-*` 请求头生成，因此即使前面还有其他代理或路径前缀，返回的 `cdp_url` 也能保持正确。

## 没有 nginx 时

如果不使用镜像自带的网关，需要由自己的反向代理完成同样的配置：

- 转发 `/cdp/json/*`，并改写返回内容中的连接地址；
- 将 `/cdp/devtools/*` 转发到 Chromium 的 `9222` 端口；
- 支持 WebSocket；
- 正确传递 `X-Forwarded-*` 请求头。

Windows 部署也需要在宿主机前配置反向代理。

## 连接 Chromium

Playwright 的 `connect_over_cdp` 和 Puppeteer 的 `browserWSEndpoint` 可以直接使用 `cdp_url`。

```text
wss://sandbox.example.com/cdp/devtools/browser/<id>
```

有些客户端只接受 `http://host:port`，不支持带路径的地址。这种情况下，需要为 Chromium 提供独立的主机名或端口，再由代理转发到 `9222`。

## 鉴权

浏览器 WebSocket 通常不能设置请求头。如果网关要求 API key，请将它加到 `cdp_url` 的查询参数中：

```text
?api_key=<key>
```

`GET /v1/browser/info?api_key=<key>` 返回的地址会保留这个参数，可以直接使用。

Chromium 的 `9222` 端口本身没有鉴权，不要将它直接暴露到可信网络之外。

## Chromium 启动示例

自建镜像时，先安装 Chromium，再用 `supervisord` 管理启动进程：

```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      chromium chromium-sandbox && \
    rm -rf /var/lib/apt/lists/*

ENV BROWSER_EXECUTABLE_PATH=/usr/bin/chromium
ENV BROWSER_REMOTE_DEBUGGING_PORT=9222
```

```bash
#!/bin/sh
exec "${BROWSER_EXECUTABLE_PATH}" \
  --user-data-dir=/home/sandbox/.config/browser \
  --remote-debugging-address=127.0.0.1 \
  --remote-debugging-port="${BROWSER_REMOTE_DEBUGGING_PORT}" \
  --remote-allow-origins=* \
  about:blank
```

```ini
[program:chromium]
command=/usr/local/bin/start-chromium.sh
environment=DISPLAY=":99",HOME="/home/sandbox",USER="sandbox"
user=sandbox
autostart=true
autorestart=true
stopsignal=INT
stdout_logfile=/var/log/chromium.log
redirect_stderr=true
```

容器部署还需要允许 Chromium 使用 sandbox，并为 `/dev/shm` 分配足够空间。

## 相关页面

- [浏览器 API](/zh/daemon/basic/browser) —— 浏览器 REST API
- [浏览器（CDP）示例](/zh/daemon/examples/browser-cdp) —— Playwright 和 Puppeteer 示例
