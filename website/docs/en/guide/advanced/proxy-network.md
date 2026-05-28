# Proxy And Network

AIO Sandbox supports outbound proxy configuration and inbound preview proxying for services running inside the container.

## Outbound Proxy

Use `PROXY_SERVER` when browser or tool traffic needs an upstream HTTP/HTTPS proxy:

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 8080:8080 \
  -e PROXY_SERVER=http://proxy.example.com:3128 \
  ghcr.io/agent-infra/sandbox:latest
```

Optional allow and deny lists:

```bash
-e PROXY_EXCLUDE=localhost,127.0.0.1,.example.org
-e PROXY_INCLUDE=.example.com
```

## Inbound Preview Proxy

Applications started inside the sandbox can be previewed through the main HTTP port.

Path-style proxy:

```text
http://localhost:8080/proxy/3000/
http://localhost:8080/absproxy/3000/
```

Use `/proxy/{port}/` for backend-style services and `/absproxy/{port}/` when a frontend app expects absolute paths.

Header-style proxy:

```bash
curl -H 'x-aio-proxy-port: 3000' \
  http://localhost:8080/
```

`x-aio-proxy-port` is useful when a public gateway or custom reverse proxy cannot encode the target port in a subdomain. The sandbox forwards the request to `127.0.0.1:<port>` and removes the control header before the request reaches the target service. Set or overwrite this header only at a trusted proxy layer; do not rely on a client-supplied value.

## Runtime Proxy APIs

The proxy can also be inspected and updated through REST endpoints:

- `GET /v1/proxy/health`
- `GET /v1/proxy/upstream`
- `GET /v1/proxy/mappings`
- `POST /v1/proxy/mappings`
- `DELETE /v1/proxy/mappings/{source}`

## Tips

- Keep local development traffic out of upstream proxies when possible.
- Prefer environment variables for reproducible startup configuration.
- Use runtime APIs for temporary mappings during a single task.
