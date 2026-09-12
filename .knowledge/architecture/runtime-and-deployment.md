---
type: architecture
---

# Runtime and Deployment

Describes how the AIO Sandbox runtime is deployed, configured, and
distributed. See also [runtime distribution model](../decisions/runtime-distribution-model.md).

## Container topology

The runtime is a single Docker container exposing one public port (8080) that
fronts many internal services. From `docker-compose.yaml`:

| Internal service | Port | Notes |
|---|---|---|
| Proxy server / public entry | 8080 | Everything is reached through this |
| Auth backend | 8081 | Optional API-key/JWT enforcement |
| WebSocket proxy | 6080 | VNC streaming |
| GEM server | 8088 | |
| MCP hub | 8079 | Aggregates browser/file/terminal/markitdown MCP servers |
| Sandbox service (srv) | 8091 | |
| JupyterLab | 8888 | Optional (`DISABLE_JUPYTER`) |
| code-server | 8200 | Optional (`DISABLE_CODE_SERVER`) |
| MCP browser server | 8100 | |
| MCP markitdown server | 8101 | |
| MCP chrome-devtools server | 8102 | |
| Browser remote debugging (CDP) | 9222 | |
| Tinyproxy | 8118 | Outbound HTTP proxy |
| VNC server | 5900 | |

`WAIT_PORTS: "8079,8091"` indicates the container's entrypoint waits for the
MCP hub and sandbox service before declaring readiness.

## Resource and security configuration

- `security_opt: seccomp:unconfined` — required for Chrome/Chromium inside
  the container. This is a hard constraint for all deployment paths; every
  documented `docker run` invocation includes it.
- `shm_size: 2gb`, `mem_limit: 8g`, `cpus: 4` — sized for a headless browser
  plus tooling.
- Host-side port binding is deliberately `127.0.0.1:8080` in all examples:
  the sandbox listens on `0.0.0.0` inside the container, so exposing it
  directly would be unsafe. The docs mandate keeping port 8080 private behind
  a reverse proxy/Ingress for cloud deployment, with optional
  `SANDBOX_API_KEY` or JWT auth at the proxy/auth-backend layer.

## Environment model

Configuration is entirely environment-variable driven (see
`docker-compose.yaml` and `website/docs/en/guide/advanced/env-config.md`).
Notable groups:

- Networking: `PROXY_SERVER`, `DNS_OVER_HTTPS_TEMPLATES` (defaults to
  Cloudflare DoH), `TINYPROXY`-related settings.
- Auth: `SANDBOX_API_KEY` (three injection methods: `X-AIO-API-Key` header,
  `Authorization: Bearer`, `?api_key=` query), `JWT_PUBLIC_KEY` (base64
  RS256 public key; enables Bearer verification and short-lived `?ticket=`
  one-time tickets for header-less clients like VNC).
- Package mirrors: `PIP_INDEX_URL`, `UV_DEFAULT_INDEX`, `NPM_CONFIG_REGISTRY`.
- UX: `DISPLAY_WIDTH/HEIGHT` (VNC resolution), `TZ`, `HOMEPAGE`.
- Skills: `AIO_SKILLS_PATH` (Claude-style skills mounting).
- Features: `DISABLE_JUPYTER`, `DISABLE_CODE_SERVER`.

## Image distribution

Two distribution channels, mirrored:

1. **Upstream**: `enterprise-public-cn-beijing.cr.volces.com/vefaas-public/all-in-one-sandbox`
   (Volcengine registry, mainland-China friendly).
2. **GHCR**: `ghcr.io/agent-infra/sandbox` — populated by the release
   workflow, which mirrors (not builds) the upstream image; see
   [image mirroring CI](../decisions/image-mirror-cd.md).

Version tags: releases strip the leading `v` from GitHub release tags
(v1.0.0.1 → 1.0.0.1) and additionally publish `:latest`.

## Cloud deployment

For managed sandbox lifecycles, both SDKs ship a `VolcengineProvider`
(VEFAAS) that creates/gets/lists/deletes sandbox instances by `functionId`,
with signed requests using Volcengine access keys. Region defaults to
`cn-beijing`. The cloud deployment guide lives at
`website/docs/en/guide/start/cloud-deployment.mdx`.

## Related knowledge

- [System overview](system-overview.md)
- [Cloud provider abstraction](../decisions/cloud-provider-abstraction.md)
- [Image mirroring CI](../decisions/image-mirror-cd.md)
