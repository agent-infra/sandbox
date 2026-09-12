# CDP Access

aiod connects to an already running Chromium over CDP (Chrome DevTools Protocol).

For external clients to connect, a reverse proxy in front of aiod also has to map Chromium's port `9222` to a public address.

## What aiod does

aiod connects to `BROWSER_REMOTE_DEBUGGING_HOST:PORT`, `127.0.0.1:9222` by default.

It answers `GET /v1/browser/info` with the `cdp_url` a client needs to connect to Chromium. Behind a reverse proxy, the address uses the proxy's public address.

aiod does not serve `/cdp/*`. That part is the reverse proxy's job.

## nginx configuration

The prebuilt images already route CDP through nginx. The relevant config:

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

The first block handles the connection info Chromium returns and rewrites its addresses to the public one. The second forwards the DevTools WebSocket connection.

`$cdp_scheme`, `$cdp_host`, and `$cdp_prefix` come from the `X-Forwarded-*` headers, so `cdp_url` stays correct behind another proxy or a path prefix.

## Without nginx

Without the image's gateway, your own reverse proxy has to do the same:

- forward `/cdp/json/*` and rewrite the connection addresses in the response;
- forward `/cdp/devtools/*` to Chromium's port `9222`;
- support WebSocket;
- pass the `X-Forwarded-*` headers through.

Windows deployments also need a reverse proxy in front of the host.

## Connecting to Chromium

Playwright's `connect_over_cdp` and Puppeteer's `browserWSEndpoint` accept `cdp_url` as is.

```text
wss://sandbox.example.com/cdp/devtools/browser/<id>
```

Some clients accept only `http://host:port` with no path. Give Chromium its own hostname or port and have the proxy forward it to `9222`.

## Authentication

A browser-side WebSocket usually cannot set request headers. If the gateway requires an API key, add it to `cdp_url` as a query parameter:

```text
?api_key=<key>
```

`GET /v1/browser/info?api_key=<key>` returns an address that keeps this parameter, ready to use.

Chromium's port `9222` has no authentication of its own. Do not expose it outside a trusted network.

## Chromium startup example

For a custom image, install Chromium and manage the process with `supervisord`:

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

Container deployments also need to allow Chromium's sandbox and give `/dev/shm` enough space.

## Related

- [Browser API](/daemon/basic/browser) — the browser REST API
- [Browser (CDP) example](/daemon/examples/browser-cdp) — Playwright and Puppeteer examples
