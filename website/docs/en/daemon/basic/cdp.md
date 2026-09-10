# CDP Access

CDP access in aiod splits by design into two roles: the daemon connects to Chromium as a client, and a reverse proxy in front of it exposes Chromium's debugging port to the outside.

The daemon implements only the client role. This page describes that split and what a deployment has to provide for the other half.

## What the daemon does

- It connects to `BROWSER_REMOTE_DEBUGGING_HOST:PORT` (default `127.0.0.1:9222`) for its own browser tools, for capability probing, and for the browser MCP tools.
- It answers `GET /v1/browser/info` with `cdp_url`, built from the request's `X-Forwarded-Proto`, `X-Forwarded-Host`, and `X-Forwarded-Prefix` headers. `Host` is the fallback. The shape: `<scheme>://<host><prefix>/cdp/devtools/browser/<id>`.

The daemon does not serve `/cdp/*`. The shape is fixed — Chromium reachable under the sandbox's single public origin, at the `/cdp/` prefix — but not the component behind it: serving that path is the deployment's job.

## Why the proxy must serve `/cdp/*`

Serving `/cdp/json/*` and relaying `/cdp/devtools/*` WebSockets are both a reverse proxy's job:

- Discovery is a string rewrite: Chromium's `/json/version` and `/json/list` return URLs starting with `ws://127.0.0.1:9222/`. The proxy replaces that prefix with the public origin plus `/cdp/`, and the `ws=` form inside `devtoolsFrontendUrl` the same way.
- The DevTools WebSocket is plain forwarding: `/cdp/devtools/<rest>` becomes `/devtools/<rest>` on port 9222. The `Upgrade` headers pass through, with a long read timeout.

Two details make the rewrite work:

- Chromium rejects `/json/*` requests whose `Host` is not an IP address or `localhost`. The proxy sends `Host: 127.0.0.1:9222` upstream.
- The response body must be uncompressed for the substitution to apply. The proxy sends an empty `Accept-Encoding` upstream.

## CDP on the prebuilt images

nginx on the AIO and Computer images implements both locations. Here is the config:

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

`$cdp_scheme`, `$cdp_host`, and `$cdp_prefix` are derived from the `X-Forwarded-*` headers. `cdp_url` stays correct behind a second proxy or an ingress that adds a path prefix.

For example, set these request headers:

```text
X-Forwarded-Proto: https
X-Forwarded-Host: sandbox.example.com
X-Forwarded-Prefix: /s/abc
```

`info` then answers `wss://sandbox.example.com/s/abc/cdp/devtools/browser/<id>`.

## Without nginx

On a host without the image's gateway, the deployment's own reverse proxy does the same two things. On Windows this is the reverse proxy in front of the host. It rewrites the discovery JSON and forwards `/cdp/devtools/*` to port 9222, with the same header rules.

Any proxy that can forward WebSockets and rewrite a response body works. The daemon needs only the `X-Forwarded-*` headers from it.

## Path or port access

`cdp_url` is path-shaped: `wss://sandbox.example.com/cdp/devtools/browser/<id>`. Playwright's `connect_over_cdp` and Puppeteer's `browserWSEndpoint` accept it as is. Playwright also accepts `{base_url}/cdp` as an HTTP endpoint: it appends `json/version/` and keeps the query string.

Some clients accept only `http://host:port` with no path:

- Puppeteer's `browserURL`
- chrome-devtools-mcp's `--browserUrl`
- Selenium
- OSWorld

They need port-shaped access, a hostname that terminates at Chromium's port 9222. A deployment that gives each sandbox its own hostname can expose the port as a subdomain or a dedicated listener. The same proxy forwards it to 9222.

The daemon is not involved in either shape. Its browser tools keep connecting to `BROWSER_REMOTE_DEBUGGING_PORT`, whether Chromium or a forwarder answers there.

## Keys

A browser-side WebSocket cannot set headers. When the gateway requires a key, append `?api_key=<key>` to `cdp_url`. `info` echoes its own query string onto both URLs it returns, so `GET /v1/browser/info?api_key=<key>` hands back a `cdp_url` that connects as is. The rule is the same as for every other WebSocket route.

Never expose port 9222 outside a trusted network: Chromium's debugging port has no authentication of its own.

## Related

- [Browser API](/daemon/basic/browser) — the REST tools and client examples
- [Browser (CDP) example](/daemon/examples/browser-cdp) — Playwright and Puppeteer end to end
