# Deployment & Operations

`aiod` is built to run unattended under any process supervisor: one binary, no build step. It exposes a `/health` plus `/v1/capabilities` split that lets orchestration tell a live process apart from a fully ready one.

This page goes in deployment order: install the binary, hand it to a supervisor, require a key, wire the two checks into orchestration, then logs, variables and troubleshooting.

## Place the binary

The install script downloads the build for the machine, verifies it against the release's `SHA256SUMS`, and installs it. Pin the version a deployment is built on and put the binary where the supervisor expects it:

```bash
curl -fsSL https://aio-static.tos-cn-beijing.volces.com/install.sh \
  | AIOD_VERSION=0.9.2 AIOD_INSTALL_DIR=/usr/local/bin sh

aiod version
# aio-daemon 0.9.2+<commit>
```

Add `AIOD_WITH_COMPUTER_USE=1` on a host that runs the desktop worker. Every release directory (`/v<version>/<platform>/`) also carries the raw binaries and `SHA256SUMS` for an image build that fetches them itself.

Pick the platform directory that matches the target platform: `linux-x86_64`, `linux-arm64`, `linux-riscv64`, or `windows-x86_64` (`aiod.exe`). `latest/<platform>/aiod` always points at the newest stable release.

Pin `v<version>/<platform>/aiod` for a specific one. Release notes and per-file checksums are at [Daemon Releases](/daemon/start/releases).

## Run under a supervisor

`aiod start` stays in the foreground and has no daemonize flag: the supervisor owns restarts, logging and the environment. Use whatever already manages the host. The examples below all set the service to port `8091`.

**systemd:**

```ini
[Unit]
Description=aiod sandbox daemon
After=network.target

[Service]
ExecStart=/usr/local/bin/aiod start
Environment=AIO_API_KEY=my-secret-key
Environment=AIO_PORT=8091
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**supervisord:** the prebuilt images run aiod this way, next to nginx and Chromium:

```ini
[program:aiod]
command=/usr/local/bin/aiod start
environment=AIO_PORT="8091",AIO_API_KEY="my-secret-key"
autorestart=true
stdout_logfile=/var/log/aiod.log
redirect_stderr=true
```

**Image `CMD`:** copy the binary into any image and make it the command:

```dockerfile
FROM your-base-image
COPY aiod /usr/local/bin/aiod
RUN chmod +x /usr/local/bin/aiod
ENV AIO_PORT=8091
EXPOSE 8091
CMD ["aiod", "start"]
```

**Docker Compose:** the same container with `/health` as the healthcheck:

```yaml
services:
  sandbox:
    build: .
    ports:
      - "8091:8091"
    environment:
      AIO_PORT: 8091
      AIO_API_KEY: ${AIO_API_KEY:-}
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://127.0.0.1:8091/health"]
      interval: 10s
      timeout: 3s
      retries: 5
```

**Windows:** `aiod.exe` runs as a normal process or registers as an SCM service (Session 0). See [Windows](/daemon/basic/windows).

The daemon always starts, even with no bash, no interpreter, no browser, and no desktop reachable. A missing capability degrades its own routes to `503`. It does not block startup.

## Require an API key

Pass a key to require authentication on every non-public route:

```bash
aiod start --api-key my-secret-key
# or: AIO_API_KEY=my-secret-key aiod start
```

Clients send `Authorization: Bearer <key>` or `x-api-key: <key>`. A WebSocket, download, or other URL that cannot set headers takes `?api_key=` instead.

These routes stay open either way:

- `/`
- `/health`
- `/v1/ping`
- `/v1/openapi.json`
- `/v2/openapi.json`
- `/internal/auth`

With no key set, every route is open. Bind to a private interface, or keep the port off any public network.

## Health vs. capability readiness

| Check | Path | Answers |
| --- | --- | --- |
| Liveness | `GET /health` | The process is up (public, no key) |
| Capability readiness | `GET /v1/capabilities` | Which domains are usable now |

`/v1/capabilities` is cached for 5 s and refreshed in the background. Add `?refresh=true` to force a fresh probe. The domains it reports are `files`, `exec`, `code_interpreter`, `browser`, and `computer`.

Restart on a failing `/health`. Gate traffic on `/v1/capabilities`, not on `/health` alone.

A healthy process can still report a degraded or absent capability:

- no bash on the host
- no interpreter
- no reachable Chromium
- no desktop

Check both directly:

```bash
curl -fsS "$BASE_URL/health"
curl -fsS "$BASE_URL/v1/capabilities?refresh=true" -H "Authorization: Bearer $AIO_API_KEY"
```

## Logs

aiod writes structured JSON to stdout, one line per request. Each line is tagged `HTTP_REQUEST` with method, path, status, `duration_ms`, `logid`, and `client_ip`.

Point the container log driver or supervisor at stdout. There is no separate log file to tail. `AIO_RUST_LOG_LEVEL` (default `info`) controls verbosity.

## Environment variables

| Variable | Default | Meaning |
| --- | --- | --- |
| `AIO_HOST` | `0.0.0.0` | bind address |
| `AIO_PORT` | `18091` | bind port |
| `AIO_API_KEY` | unset | require a key on protected routes |
| `AIO_RUNTIME_DIR` | auto | pid, sockets, scratch state |
| `AIO_DEFAULT_USER` | daemon account | account used for commands, interpreters, and file ownership (Linux only) |
| `AIO_API_SURFACE` | `full` | `full` (v1 + v2) or `v2` only |
| `AIO_RUST_LOG_LEVEL` | `info` | log filter |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | unset | set to turn on OTLP trace export |

Every flag has a matching environment variable (`--host`/`AIO_HOST`, `--port`/`AIO_PORT`, …). The flag wins when both are set.

## Troubleshooting

- **`503` on `/v1/nodejs`, `/v1/code`, `/v2/code`** — no matching interpreter on the host. Install `python3` or `node`; `capabilities.code_interpreter.missing` says what is missing.
- **`501` on `/v1/jupyter`** — no `ipykernel` importable and no `AIO_JUPYTER_ENDPOINT` set. Install `ipykernel`, or point `AIO_JUPYTER_ENDPOINT` at a Jupyter server.
- **`503` on `/v1/browser/*`** — no Chromium at `BROWSER_REMOTE_DEBUGGING_HOST:PORT` (default `127.0.0.1:9222`). Start Chromium with `--remote-debugging-port=9222`.
- **`503` on `/v2/computer/*`** — the `computer-use` worker is not reachable. Start it; check `AIO_COMPUTER_USE_URL` (default `http://127.0.0.1:18100`).
- **Every `/v1/*` or `/v2/*` call answers `401`** — `AIO_API_KEY` is set. Send `Authorization: Bearer <key>` or `x-api-key: <key>`; `?api_key=` for WebSocket and downloads.
- **`400` on `/v1/shell/ws` right after connecting** — `durable=true` or `restore=true` without a `session_id`. `POST /v1/shell/sessions/create`, then attach with `?session_id=<id>`.

Full request/response details for every route are in the OpenAPI spec the running daemon serves: `/v1/openapi.json`, `/v2/openapi.json`. The v2 reference is also published as the [API Reference](/daemon/api). Kubernetes-specific guidance is in [Kubernetes](/daemon/ops/kubernetes).
