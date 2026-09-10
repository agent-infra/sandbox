# Migration from 1.x

`aiod` stands in for the 1.x Python server. The public port and gateway are unchanged on the prebuilt images: most clients migrate by switching the image tag.

The v1 surface is documented in [v1 API Reference](/daemon/start/v1-api). The v2 surface is in the [API Reference](/daemon/api).

## Migrate with the prebuilt images

Replace `ghcr.io/agent-infra/sandbox:latest` (the 1.x AIO image) with `aio-daemon`, or with `aio-computer` for GUI use. The run command keeps the 1.x flags plus `--shm-size 4g` for Chromium; the commands, the gateway port and the startup timing are in [Quick Start](/daemon/start/quick-start#from-a-prebuilt-image).

Then check the client against this list:

- **API key** — `SANDBOX_API_KEY` still works. JWT and tickets are gone. See [Authentication](#authentication).
- **Removed routes** — a client calling proxy mapping, skills CRUD, or page-level browser automation needs a replacement. See [Removed routes](#removed-routes).
- **SDK coverage** — the v1 SDKs still reach most of the surface, and the three calls that fail send a method, a route, or an id the daemon does not serve. See [1.x SDK compatibility](#1x-sdk-compatibility).
- **Changed defaults on the images** — Code Server and JupyterLab are off, no kernel is prewarmed, and the shell and code backends are pinned to `native`. See [The images](#the-images).

## Route map: v1 to v2

| Plane | v2 | v1 (compatible) |
| --- | --- | --- |
| Commands | `POST /v2/commands` | `/v1/bash/*` |
| Files | `/v2/fs/*`, `/v2/watch` | `/v1/file/*` |
| Terminals | `/v2/pty/sessions/*` | `/v1/shell/*` |
| Code | `/v2/code/*` | `/v1/code/*`, `/v1/jupyter/*`, `/v1/nodejs/*` |
| Browser | `/v2/browser/*` (alias) | `/v1/browser/*` |
| Desktop | `/v2/computer/*` | `/v1/browser/actions`, `/v1/display/record` |
| MCP | `POST /mcp` | `POST /mcp` |
| Ops | `/v2/sandbox`, `/health`, `/metrics` | `/v1/sandbox`, `/v1/capabilities` |

`/metrics` needs the key. The exact routes per plane follow; the capability pages show usage in one style at a time, chosen with the API Preference switch in the sidebar.

### Commands

| Operation | v2 | v1 |
| --- | --- | --- |
| Run a command | `POST /v2/commands` | `POST /v1/bash/exec` |
| Read output | `GET /v2/commands/{command_id}` | `POST /v1/bash/output` |
| Write stdin | `POST /v2/commands/{command_id}/stdin` | `POST /v1/bash/write` |
| Kill | `POST /v2/commands/{command_id}/kill` | `POST /v1/bash/kill` |
| Create session | `POST /v2/commands/sessions` | `POST /v1/bash/sessions/create` |
| List sessions | `GET /v2/commands/sessions` | `GET /v1/bash/sessions` |
| Close session | `DELETE /v2/commands/sessions/{session_id}` | `POST /v1/bash/sessions/{session_id}/close` |

v2 treats each run as a resource: `POST /v2/commands` returns a `command_id`, output is read by offset per stream or streamed as NDJSON on the same route, and sessions are optional under `/v2/commands/sessions`; v1 keyed every call by `session_id` and created the session on first use. v2 also adds `shell` and `args`, and a session-wide `env`.

Response envelope (v1 and most v2):

- `success` — whether the call succeeded
- `message` — a one-line summary
- `data` — the payload; `null` when there is none
- `hint` — optional guidance, otherwise `null`

Validation failures answer `422` with `errors: [{location, message, type}]`, as in 1.x. File errors carry these fields under `data`:

- `errno` — the OS error number
- `errno_name` — its symbolic name, such as `ENOENT`
- `error_type` — the kind of failure: `not_found`, `permission_denied`, …
- `exception_type` — the 1.x exception class name, such as `FileNotFoundError`
- `message` — a one-line summary
- `operation` — the file operation that failed
- `path` — the path involved
- `retryable` — whether a retry can succeed

Status codes:

- `400` — malformed request
- `401` — missing or wrong API key
- `403` — input denied by the OS
- `404` — unknown route or object
- `422` — failed validation
- `429` — session or watcher capacity reached
- `501` — not implemented on this daemon: a Linux-only route on Windows, or `/v1/jupyter` without `ipykernel`
- `503` — capability unavailable right now


### Files

| Operation | v2 | v1 |
| --- | --- | --- |
| Read | `GET /v2/fs/read` | `POST /v1/file/read` |
| Write | `POST /v2/fs/write` | `POST /v1/file/write` |
| Edit | `POST /v2/fs/edit` | `POST /v1/file/str_replace_editor`, `POST /v1/file/replace` |
| Stat | `GET /v2/fs/stat` | `POST /v1/file/stat` |
| List directory | `GET /v2/fs/list` | `POST /v1/file/list` |
| Find by name | `GET /v2/fs/search` | `POST /v1/file/find`, `POST /v1/file/glob` |
| Search contents | `POST /v2/fs/grep` | `POST /v1/file/grep`, `POST /v1/file/search` |
| Create directory | `POST /v2/fs/mkdir` | `POST /v1/file/mkdir` |
| Copy | `POST /v2/fs/copy` | `POST /v1/file/copy` |
| Move | `POST /v2/fs/move` | `POST /v1/file/move` |
| Delete | `POST /v2/fs/delete` | `POST /v1/file/delete` |
| Upload | `POST /v2/fs/upload` | `POST /v1/file/upload` |
| Download | `GET /v2/fs/download` | `GET /v1/file/download` |
| Directory as tar | `GET`/`PUT /v2/fs/tree` | — |
| Create watcher | `POST /v2/watch` | `POST /v1/file/watch` |
| Poll watcher | `GET /v2/watch/{id}/poll` | `POST /v1/file/watch/{id}/poll` |
| Stream watcher | `GET /v2/watch/{id}/events` | `GET /v1/file/watch/{id}/events` |
| Stop watcher | `DELETE /v2/watch/{id}` | `DELETE /v1/file/watch/{id}` |

v2 keys every call by `path`, reads and listings are `GET`, and `?user=` selects the owner; v1 mixed `file` and `path` keys with a per-call `sudo` flag.

### Terminals

| Operation | v2 | v1 |
| --- | --- | --- |
| Create session | `POST /v2/pty/sessions` | `POST /v1/shell/sessions/create` |
| List sessions | `GET /v2/pty/sessions` | `GET /v1/shell/sessions` |
| Inspect session | `GET /v2/pty/sessions/{id}` | — |
| Resize session | `PATCH /v2/pty/sessions/{id}` | — |
| Close session | `DELETE /v2/pty/sessions/{id}` | `DELETE /v1/shell/sessions/{session_id}` |
| Run a command | `POST /v2/pty/sessions/{id}/exec` | `POST /v1/shell/exec` |
| Type input | `POST /v2/pty/sessions/{id}/input` | `POST /v1/shell/write` |
| Signal | `POST /v2/pty/sessions/{id}/signal` | `POST /v1/shell/kill` |
| Read screen | `GET /v2/pty/sessions/{id}/screen` | `POST /v1/shell/view` |
| Attach WebSocket | `GET /v2/pty/sessions/{id}/ws` | `GET /v1/shell/ws` |
| Anonymous shell | `GET /v2/pty/ws` | — |

v2 treats a terminal as a resource under `/v2/pty/sessions/{id}`, with explicit verbs (exec, input, signal, screen, resize) and a durable WebSocket attach; v1 multiplexed all of it through `/v1/shell/exec {id}` and `/v1/shell/ws`.

### Code

| Operation | v2 | v1 |
| --- | --- | --- |
| Execute | `POST /v2/code/execute` | `POST /v1/code/execute` |
| Runtime info | `GET /v2/code/info` | `GET /v1/code/info` |
| Stateful sessions | `/v2/code/execute` with `session_id`, `GET /v2/code/sessions` | `/v1/code/execute` with `session_id`, `/v1/jupyter/*`, `/v1/nodejs/*` |

v2 has one entry point, `POST /v2/code/execute {language, code, session_id?}`, with sessions under `/v2/code/sessions`; v1 split execution by language, each route with its own session semantics.

### Browser

| Operation | v2 | v1 |
| --- | --- | --- |
| Browser REST tools | `/v2/browser/*` | `/v1/browser/*` |

`/v2/browser/*` aliases `/v1/browser/*`: same routes, same bodies. v2 adds no page-level routes, since page automation belongs to CDP clients and the DevTools relay lives in the proxy.

### Desktop

| Operation | v2 | v1 |
| --- | --- | --- |
| Desktop actions | `/v2/computer/*` | `/v1/browser/actions` |
| Recording | `/v2/computer/record` | `/v1/display/record` |

The desktop surface is v2-only, under `/v2/computer/*`; `/v1/browser/actions` and `/v1/display/record` remain as aliases for 1.x clients.

### Sandbox

| Operation | v2 | v1 |
| --- | --- | --- |
| Sandbox info | `GET /v2/sandbox` | `GET /v1/sandbox` |
| Capability probe | — | `GET /v1/capabilities` |
| Python packages | `GET /v2/sandbox/packages?lang=python` | `GET /v1/sandbox/packages/python` |
| Node.js packages | `GET /v2/sandbox/packages?lang=nodejs` | `GET /v1/sandbox/packages/nodejs` |

`GET /v2/sandbox` returns identity, workspace, and capabilities as one JSON object; `/v1/sandbox` keeps the 1.x layout, a text summary in `data` with `detail`, `version`, and `workspace` at the top level. The v2 name for the workspace is `workspace_dir`; `/v1/sandbox` sends `home_dir` as well, at the top level and under `detail.system`, so the 1.x model still parses.

## Removed routes

The routes below no longer exist on `aiod`; calling them answers `404`. Two kinds: some are gone outright with no replacement, and some moved to a different entry point.

**Gone outright, no replacement:**

- `/v1/skills/*` (create/read/update/delete), `/v1/sandbox/hooks`, and `SANDBOX_SHUTDOWN_HOOKS`
- `/v1/util/convert_to_markdown`
- The `stdin` field of `POST /v1/nodejs/execute`; unknown body fields are ignored
- `/v1/sandbox/observe/*`
- Standalone Node REPL servers (`DISABLE_NODEJS_REPL`, `NODEJS_REPL_PORT*`)
- `WORKSPACE` relocation (there is no `--workspace` flag)
- `/v1/browser/captcha/*`, `/v1/browser/state/*`, `/v1/browser/restart`, the `/v1/browser/network/*` sub-routes `route`/`headers`/`scoped_headers`/`export_har` (`network/requests` still works), and `/v1/browser/proxy.pac`

**Moved to a different entry point:**

- Runtime proxy-mapping API → a static `PROXY_MAP` on the images
- `/v1/mcp/servers`, `/v1/mcp/<server>/tools`, and the other management routes → the `/mcp` hub (see [MCP](#mcp) below)
- `/v1/browser/page/*` page automation → drive the page over CDP (`BROWSER_REMOTE_DEBUGGING_HOST`/`_PORT`, default `127.0.0.1:9222`); the daemon does not proxy DevTools itself, a deployment has to expose it (nginx does on the images)
- `POST /tickets` and JWT auth → use `AIO_API_KEY` (see [Authentication](#authentication) below)

These `/v1/browser/*` routes still answer:

- `navigate`
- `screenshot`
- `click`
- `fill`
- `evaluate`
- `upload`
- `config`
- `cdp`
- `snapshot`
- `tabs`
- `cookies`
- `info`
- `network/requests`
- `actions`

## Authentication

`AIO_API_KEY` (`--api-key`) is the only credential, and it is optional. With a key set, every request except the public routes below must carry it; `SANDBOX_API_KEY` on the images sets the same key.

The three forms are equivalent; pick one:

- `Authorization: Bearer <key>`
- `x-api-key: <key>`
- `?api_key=<key>` — deprecated, but the only option for WebSocket and VNC URLs, which cannot carry headers

These routes answer without a key:

- `/`
- `/health`
- `/v1/ping`
- `/v1/openapi.json`
- `/v2/openapi.json`
- `/internal/auth`

Everything else, `/metrics` included, needs the key once one is set. The images' gateway also accepts `X-AIO-API-Key`.

Send the key as a bearer token:

```bash
KEY=<key>

curl -H "Authorization: Bearer $KEY" "$BASE_URL/v2/sandbox"
```

The 1.x ticket/JWT mechanism is gone entirely: `POST /tickets`, `GET /auth`, and `JWT_PUBLIC_KEY` verification no longer exist. A deployment that only configured `JWT_PUBLIC_KEY` is now unauthenticated, with a warning at boot — set `AIO_API_KEY` explicitly instead.

WebSocket and VNC URLs have no headers to use, so the key goes in the URL, for example `ws://127.0.0.1:8091/v2/pty/sessions/SESSION_ID/ws?api_key=$KEY`.

## Identity: user and AIO_DEFAULT_USER

On commands, PTY, and code, `user` (per request) or `AIO_DEFAULT_USER` (at startup) is the execution identity. The process runs as that account.

On file routes it is only the ownership identity. The daemon still reads and writes with its own privileges. Objects it creates belong to that account.

This applies on Linux only. Windows answers `400` for an explicit `user`, and `503` where `AIO_DEFAULT_USER` would apply.

On the images, the daemon runs as root with `AIO_DEFAULT_USER=gem`; commands run as `gem`.

The working directory is not a confinement boundary. File routes can reach the whole host filesystem. Isolation is the container's or VM's job, not the daemon's.

## MCP

`EXTRA_MCP_SERVERS` (or `--mcp-servers`) registers loopback, stateless streamable-HTTP MCP servers. Their tools are listed next to the 10 built-in ones on `POST /mcp`.

Only `http://127.0.0.1|localhost|[::1]` targets are accepted. These are skipped with a warning:

- remote servers
- `command` (stdio) servers
- session-requiring servers

The 1.x management surface is gone:

- `MCP_FILTER_SERVERS`
- `hidden`
- per-entry timeouts
- `/v1/mcp/*` management routes

List tools with `tools/list` on `/mcp` instead. On the AIO image, `mcp-server-browser` starts together with the browser.

## The images

### AIO image

`aio-daemon` bundles `aiod` with Chromium, VNC, Python and Node toolchains, and an nginx gateway.

### Computer image

`aio-computer` adds an XFCE desktop and the `computer-use` worker on top of the AIO image.

### Environment variables

Image-only environment variables:

| Variable | Default | Meaning |
| --- | --- | --- |
| `SANDBOX_API_KEY` | unset | alias of `AIO_API_KEY` |
| `BROWSER_START_MODE` | `async` | `async` keeps the browser off the readiness path; `auto` waits for it; `manual` (the Computer image default) starts no browser until the desktop's Browser launcher is used |
| `DISABLE_CODE_SERVER` | `true` | Code Server IDE is off by default |
| `DISABLE_JUPYTER` | `true` | the `/jupyter` Lab UI is off; the `/v1/jupyter` API still works |
| `EXTRA_MCP_SERVERS` | unset | same registry format as `--mcp-servers` |
| `MCP_SERVER_BROWSER_PORT` | `8100` | port `mcp-server-browser` listens on |
| `DISABLE_MCP_BROWSER` | unset | `true` stops `mcp-server-browser` from starting |
| `PROXY_SERVER` / `PROXY_MAP` | unset | static proxy mapping (the 1.x runtime mapping API is gone) |
| `WORKSPACE` | account home | must stay the account's home directory |

The Computer image adds `AIO_DESKTOP=xfce` and `ENABLE_DBUS=true`, which starts the session D-Bus that AT-SPI needs. Chromium runs with `--force-renderer-accessibility`.

### Changed defaults

`JUPYTER_POOL_SIZE` maps to `AIO_KERNEL_PREWARM`: the default is `0`, nothing warmed. `AIO_SHELL_BACKEND=native` and `AIO_CODE_BACKEND=native` are pinned on the images. They are not auto-detected.

## Build a custom image

Two starting points cover most cases. Add layers on top of `FROM enterprise-public-cn-beijing.cr.volces.com/vefaas-public/aio-daemon:1.0.0` (or `aio-computer`), or copy the `aiod` binary into any image you already have. See [Deployment](/daemon/ops/deployment).

The daemon resolves tools at request time from `PATH`. Installing packages in the Dockerfile is enough:

- Python packages and `ipykernel` for code execution
- `node` for JavaScript
- `rg` and `tmux` for search and terminals

`GET /v1/capabilities` reports what the image ended up with.

Services in the images run under supervisord. An extra long-running process becomes a supervisord program: place a `.conf` file in `/opt/gem/supervisord/`. The image's `/etc/supervisord.conf` includes that directory.

Lifecycle hooks run in the image entrypoint, each a shell command string:

- `RUN_HOOK_INIT` — runs before anything starts
- `RUN_HOOK_PRE_SERVICES` — runs before services start
- `RUN_HOOK_POST_READY` — runs after the daemon is healthy

`RUN_HOOKS_STRICT=true` makes a failing hook fatal (default `false`).

The daemon deliberately limits some capabilities. A custom image can lift each of them:

| Daemon limit | In a custom image |
| --- | --- |
| The `/mcp` hub aggregates only loopback, stateless MCP servers. | Run the MCP server inside the image as a supervisord program, and list it in `EXTRA_MCP_SERVERS`. |
| No runtime proxy-mapping API. | Set `PROXY_SERVER` / `PROXY_MAP` at start. |
| No skills CRUD API. | Put skill directories on disk and point `AIO_SKILLS_PATH` at them; the `sandbox_load_skill` MCP tool reads them. |
| Code-server and JupyterLab are off by default. | Set `DISABLE_CODE_SERVER=false` (served at `/code-server/`) and `DISABLE_JUPYTER=false` (served at `/jupyter`). |
| The daemon never launches a browser. | The image starts Chromium; `BROWSER_EXTRA_ARGS` adds flags, `HOMEPAGE` sets the start page. |
| No warm kernel by default. | Set `AIO_KERNEL_PREWARM=1`. |
| The ref suite (`snapshot`, ref `click`/`fill`/`upload`) runs on the built-in CDP backend. | Point `AIO_AGENT_BROWSER_BIN` at an agent-browser CLI to delegate it; the AIO image ships one. |
| The daemon never starts a desktop. | Use `aio-computer`, or provide an X11 display in your image and run `computer-use` next to `aiod`. |

## 1.x SDK compatibility

The 1.x SDKs call the v1 routes and work against `aiod` without changes: Python `agent-sandbox` 0.0.31 and TypeScript `@agent-infra/sandbox` 1.0.17 were verified against `aiod` 0.9.x. The Go SDK `github.com/agent-infra/sandbox-sdk-go` v0.0.5 was verified against `aiod` 0.9.2: it exposes the same modules in Go casing (`file.GrepFiles`, `code.ExecuteCode`, `nodejs.GetInfo`), every method in the table below behaves as its Python counterpart, and the same three calls fail. The SDKs cover v1 only; `/v2/*` is called over HTTP, described in the [API Reference](/daemon/api) and served by a running daemon at `/v2/openapi.json`.

### Verified methods

| Module | Methods |
| --- | --- |
| `sandbox` | `get_context`, `get_python_packages`, `get_nodejs_packages` |
| `shell` | `exec_command` and the session methods |
| `bash` | `exec`, `output`, `write`, `kill`, `create_session`, `sessions`, `close_session` |
| `file` | every method except `watch_events`: it streams Server-Sent Events, which the generated clients decode as JSON (verified in Go); read that route over HTTP |
| `jupyter` | `execute_code`, `get_info`, `create_session`, `list_sessions`, `delete_session` |
| `nodejs` | `execute_code`, `get_info`, `create_session`, `list_sessions`, `get_session`, `delete_session` |
| `code` | `execute_code`, `get_info` |
| `browser` | `get_info`, `screenshot`, `set_config`, `execute_action` |
| `browser_tabs` | `list`, `create` |
| `browser_cookies`, `browser_network` | `get_cookies`, `get_requests` |
| `display` | `record` |

Every response parses into the SDK's 1.x model. The TypeScript SDK exposes the same modules with camelCase names (`file.grepFiles`, `code.executeCode`, `nodejs.getInfo`); `sandbox`, `bash`, `shell`, `file`, `code`, `nodejs`, `browser.getInfo` and `browserTabs.list` were verified, and its desktop and Jupyter methods send the same requests as the Python ones above. A TypeScript call returns `{ ok, body }` on success and `{ ok, error }` on failure, with the payload at `body.data`.

### Calls that fail

Three calls fail on the request itself:

| Call | Why |
| --- | --- |
| `nodejs.update_session` | Sends `PATCH /v1/nodejs/sessions/{id}`, which answers `404` |
| `browser_tabs.activate` | Sends `PUT`; the route takes `POST` and answers `405` |
| `browser_tabs.close` | Typed as a tab index; the route keys on the CDP target id and answers `404 no tab with id 1` |

`close` has a workaround: pass the `id` a tab listing reports instead of the position. Python accepts it as written; TypeScript needs a cast; Go types the argument as `int` and cannot express it, so the route has to be called over HTTP.

### Removed routes

These modules call routes the daemon no longer serves; they answer `404`:

- `browser_page.*`, `browser_state.*`, `browser_captcha.*`, `browser.restart`, `browser.get_proxy_pac`
- `mcp.list_mcp_servers`, `mcp.list_mcp_tools`
- `skills.*`
- `sandbox.list_hooks`, `sandbox.register_hook`, `sandbox.remove_hook`, `sandbox.observe_*`
- `proxy.*`
- `util.convert_to_markdown`
- `auth.create_ticket`
