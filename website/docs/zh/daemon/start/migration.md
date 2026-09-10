# 从 1.x 迁移

`aiod` 替代 1.x Python 服务器。预构建镜像的公开端口和网关不变，多数客户端只需切换镜像标签。

v1 端点集的参考文档在 [v1 API 参考](/zh/daemon/start/v1-api)。v2 端点集在 [API 参考](/zh/daemon/api)。

## 用预构建镜像迁移

把 `ghcr.io/agent-infra/sandbox:latest`（1.x AIO 镜像）换成 `aio-daemon`；GUI 用户可使用 `aio-computer`。run 命令沿用 1.x 的参数，只多一个给 Chromium 的 `--shm-size 4g`；启动命令、网关端口和启动耗时见 [快速开始](/zh/daemon/start/quick-start#使用预构建镜像)。

然后按下面清单进行检查：

- **API key** —— `SANDBOX_API_KEY` 仍然可用，JWT 和 ticket 已移除。见 [鉴权](#鉴权)。
- **移除的路由** —— 调用代理映射、skills 增删改查或页面级浏览器自动化的客户端需要替换方案。见 [已移除的路由](#已移除的路由)。
- **SDK 覆盖面** —— v1 的 SDK 仍然覆盖大部分端点，剩下三个失败的调用发的是 daemon 不提供的方法、路由或 id。见 [1.x SDK 兼容性](#1x-sdk-兼容性)。
- **镜像中的默认值变更** —— Code Server 和 JupyterLab 默认关闭，默认不预热 kernel，shell 和代码后端固定为 `native`。见 [镜像](#镜像)。

## 路由对照：v1 到 v2

| Plane | v2 | v1（兼容） |
| --- | --- | --- |
| 命令 | `POST /v2/commands` | `/v1/bash/*` |
| 文件 | `/v2/fs/*`、`/v2/watch` | `/v1/file/*` |
| 终端 | `/v2/pty/sessions/*` | `/v1/shell/*` |
| 代码 | `/v2/code/*` | `/v1/code/*`、`/v1/jupyter/*`、`/v1/nodejs/*` |
| 浏览器 | `/v2/browser/*`（别名） | `/v1/browser/*` |
| 桌面 GUI | `/v2/computer/*` | `/v1/browser/actions`、`/v1/display/record` |
| MCP | `POST /mcp` | `POST /mcp` |
| 运维 | `/v2/sandbox`、`/health`、`/metrics` | `/v1/sandbox`、`/v1/capabilities` |

`/metrics` 需要 key。

下面按 plane 列出具体路由。能力页一次只展示一种调用风格，可以通过侧栏的 API Preference 开关切换。

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

v2 将每次执行建模为一个资源。`POST /v2/commands` 返回 `command_id`，可以通过 offset 增量读取输出，也可以在同一路由上以 NDJSON 流式读取。

会话是可选的，统一通过 `/v2/commands/sessions` 管理。v1 每次调用都使用 `session_id`，首次使用时隐式创建会话。

v2 还新增了 `shell`、`args` 和会话级 `env`。

v1 与大多数 v2 接口的返回结构：

- `success` —— 请求是否成功
- `message` —— 一行摘要
- `data` —— 负载内容；没有时是 `null`
- `hint` —— 可选的提示信息，否则是 `null`

校验失败和 1.x 一样返回 `422`，带 `errors: [{location, message, type}]`。文件类错误在 `data` 里带这些字段：

- `errno` —— 操作系统的错误号
- `errno_name` —— 它的符号名，比如 `ENOENT`
- `error_type` —— 失败的类型：`not_found`、`permission_denied` 等
- `exception_type` —— 1.x 的异常类名，比如 `FileNotFoundError`
- `message` —— 一行摘要
- `operation` —— 失败的文件操作
- `path` —— 涉及的路径
- `retryable` —— 重试是否可能成功

状态码约定：

- `400` —— 请求格式错误
- `401` —— 未携带 key 或 key 无效
- `403` —— 操作系统层拒绝了输入
- `404` —— 路由或对象不存在
- `422` —— 校验失败
- `429` —— 会话或监听器数量达到上限
- `501` —— 此 daemon 未实现：Windows 上调用仅 Linux 的路由，或未安装 `ipykernel` 时调用 `/v1/jupyter`
- `503` —— 能力暂时不可用


### Files

| 操作 | v2 | v1 |
| --- | --- | --- |
| 读取 | `GET /v2/fs/read` | `POST /v1/file/read` |
| 写入 | `POST /v2/fs/write` | `POST /v1/file/write` |
| 编辑 | `POST /v2/fs/edit` | `POST /v1/file/str_replace_editor`、`POST /v1/file/replace` |
| 元数据 | `GET /v2/fs/stat` | `POST /v1/file/stat` |
| 列目录 | `GET /v2/fs/list` | `POST /v1/file/list` |
| 按名字查找 | `GET /v2/fs/search` | `POST /v1/file/find`、`POST /v1/file/glob` |
| 搜索内容 | `POST /v2/fs/grep` | `POST /v1/file/grep`、`POST /v1/file/search` |
| 创建目录 | `POST /v2/fs/mkdir` | `POST /v1/file/mkdir` |
| 复制 | `POST /v2/fs/copy` | `POST /v1/file/copy` |
| 移动 | `POST /v2/fs/move` | `POST /v1/file/move` |
| 删除 | `POST /v2/fs/delete` | `POST /v1/file/delete` |
| 上传 | `POST /v2/fs/upload` | `POST /v1/file/upload` |
| 下载 | `GET /v2/fs/download` | `GET /v1/file/download` |
| 整目录 tar | `GET`/`PUT /v2/fs/tree` | — |
| 创建监听器 | `POST /v2/watch` | `POST /v1/file/watch` |
| 轮询监听器 | `GET /v2/watch/{id}/poll` | `POST /v1/file/watch/{id}/poll` |
| 流式监听器 | `GET /v2/watch/{id}/events` | `GET /v1/file/watch/{id}/events` |
| 停止监听器 | `DELETE /v2/watch/{id}` | `DELETE /v1/file/watch/{id}` |

v2 所有调用都使用 `path` 字段。读取文件和列目录使用 `GET`，`?user=` 用于指定文件归属身份。

v1 混用 `file` 和 `path` 两个参数，并且每次调用都可以带 `sudo`。

### Terminals

| 操作 | v2 | v1 |
| --- | --- | --- |
| 创建会话 | `POST /v2/pty/sessions` | `POST /v1/shell/sessions/create` |
| 列出会话 | `GET /v2/pty/sessions` | `GET /v1/shell/sessions` |
| 查看会话 | `GET /v2/pty/sessions/{id}` | — |
| 调整会话尺寸 | `PATCH /v2/pty/sessions/{id}` | — |
| 关闭会话 | `DELETE /v2/pty/sessions/{id}` | `DELETE /v1/shell/sessions/{session_id}` |
| 执行命令 | `POST /v2/pty/sessions/{id}/exec` | `POST /v1/shell/exec` |
| 输入 | `POST /v2/pty/sessions/{id}/input` | `POST /v1/shell/write` |
| 发信号 | `POST /v2/pty/sessions/{id}/signal` | `POST /v1/shell/kill` |
| 读屏幕 | `GET /v2/pty/sessions/{id}/screen` | `POST /v1/shell/view` |
| attach WebSocket | `GET /v2/pty/sessions/{id}/ws` | `GET /v1/shell/ws` |
| 匿名 shell | `GET /v2/pty/ws` | — |

v2 将终端建模为 `/v2/pty/sessions/{id}` 下的资源。exec、input、signal、screen 和 resize 都有独立路由，WebSocket attach 还可以持久化。

v1 则通过 `/v1/shell/exec {id}` 和 `/v1/shell/ws` 完成这些操作。

### Code

| 操作 | v2 | v1 |
| --- | --- | --- |
| 执行 | `POST /v2/code/execute` | `POST /v1/code/execute` |
| 运行时信息 | `GET /v2/code/info` | `GET /v1/code/info` |
| 有状态会话 | 带 `session_id` 的 `/v2/code/execute`、`GET /v2/code/sessions` | 带 `session_id` 的 `/v1/code/execute`、`/v1/jupyter/*`、`/v1/nodejs/*` |

v2 只有一个入口：`POST /v2/code/execute {language, code, session_id?}`，会话统一在 `/v2/code/sessions` 下。

v1 按语言拆成三个路由，每个路由都有自己的会话语义。

### Browser

| 操作 | v2 | v1 |
| --- | --- | --- |
| 浏览器 REST 工具 | `/v2/browser/*` | `/v1/browser/*` |

`/v2/browser/*` 是 `/v1/browser/*` 的别名：路由相同，body 相同。v2 不新增页面级路由，页面自动化交给 CDP 客户端，DevTools 转发交给代理层。

### Desktop

| 操作 | v2 | v1 |
| --- | --- | --- |
| 桌面动作 | `/v2/computer/*` | `/v1/browser/actions` |
| 录屏 | `/v2/computer/record` | `/v1/display/record` |

桌面能力只在 v2 提供，路径在 `/v2/computer/*` 下；`/v1/browser/actions` 和 `/v1/display/record` 作为 1.x 客户端的别名保留。

### Sandbox

| 操作 | v2 | v1 |
| --- | --- | --- |
| 沙箱信息 | `GET /v2/sandbox` | `GET /v1/sandbox` |
| 能力探测 | — | `GET /v1/capabilities` |
| Python 包 | `GET /v2/sandbox/packages?lang=python` | `GET /v1/sandbox/packages/python` |
| Node.js 包 | `GET /v2/sandbox/packages?lang=nodejs` | `GET /v1/sandbox/packages/nodejs` |

`GET /v2/sandbox` 用一个 JSON 对象返回身份、workspace 和能力。

`/v1/sandbox` 保留 1.x 的返回布局：`data` 是文本摘要，`detail`、`version` 和 `workspace` 位于顶层。

v2 中的 workspace 字段名为 `workspace_dir`。`/v1/sandbox` 还会返回 `home_dir`，并在顶层和 `detail.system` 下各保留一份，以兼容 1.x 模型。

## 已移除的路由

以下路由在 `aiod` 上已不存在，调用一律返回 `404`。它们分为两类：一类已整体删除，没有替代入口；另一类只是换了入口，功能仍然保留。

**整体删除，没有替代：**

- `/v1/skills/*`（增删改查）、`/v1/sandbox/hooks` 与 `SANDBOX_SHUTDOWN_HOOKS`
- `/v1/util/convert_to_markdown`
- `POST /v1/nodejs/execute` 的 `stdin` 字段；请求体里不认识的字段会被忽略
- `/v1/sandbox/observe/*`
- 独立的 Node REPL server（`DISABLE_NODEJS_REPL`、`NODEJS_REPL_PORT*`）
- `WORKSPACE` 重定位（没有 `--workspace` 参数）
- `/v1/browser/captcha/*`、`/v1/browser/state/*`、`/v1/browser/restart`、`/v1/browser/network/*` 的 `route`/`headers`/`scoped_headers`/`export_har` 子路由（`network/requests` 仍可用）与 `/v1/browser/proxy.pac`

**换了个入口，功能还在：**

- 运行时代理映射 API → 镜像上用静态 `PROXY_MAP`
- `/v1/mcp/servers`、`/v1/mcp/<server>/tools` 等管理路由 → `/mcp` hub（见 [下文 MCP](#mcp)）
- `/v1/browser/page/*` 页面自动化 → 用 CDP 驱动页面（`BROWSER_REMOTE_DEBUGGING_HOST`/`_PORT`，默认 `127.0.0.1:9222`）；daemon 不代理 DevTools，需部署方自行暴露（镜像上由 nginx 完成）
- `POST /tickets` 与 JWT 鉴权 → 改用 `AIO_API_KEY`（见 [下文鉴权](#鉴权)）

`/v1/browser/*` 的以下路由仍然提供：

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

## 鉴权

`AIO_API_KEY`（`--api-key`）是唯一的凭证，可选。设了 key，除公开路由外的请求都要带上；镜像上的 `SANDBOX_API_KEY` 设置的也是同一个 key。

三种携带方式等价，任选其一：

- `Authorization: Bearer <key>`
- `x-api-key: <key>`
- `?api_key=<key>` —— 已废弃，但 WebSocket / VNC 的 URL 带不了 header，只能靠它

以下路由不需要 key：

- `/`
- `/health`
- `/v1/ping`
- `/v1/openapi.json`
- `/v2/openapi.json`
- `/internal/auth`

设置 key 后，其余路由（包括 `/metrics`）都必须携带 key。镜像网关还接受 `X-AIO-API-Key`。

把 key 作为 bearer token 发送：

```bash
KEY=<key>

curl -H "Authorization: Bearer $KEY" "$BASE_URL/v2/sandbox"
```

1.x 的 ticket / JWT 机制整体移除：`POST /tickets`、`GET /auth`、`JWT_PUBLIC_KEY` 校验都不再存在。以前只配了 `JWT_PUBLIC_KEY` 的部署现在等于没开鉴权，启动时会告警——请显式设置 `AIO_API_KEY`。

WebSocket 或 VNC 场景没有 header 可用，key 只能放在 URL 里，例如 `ws://127.0.0.1:8091/v2/pty/sessions/SESSION_ID/ws?api_key=$KEY`。

## 身份：user 与 AIO_DEFAULT_USER

在命令、PTY 和代码执行上，`user`（按请求）或 `AIO_DEFAULT_USER`（启动时）是执行身份。进程以该账户运行。

在文件路由上它只是归属身份。daemon 仍以自己的权限读写，新建对象归属该账户。

仅 Linux 有效。Windows 上显式传 `user` 返回 `400`，`AIO_DEFAULT_USER` 生效的场合返回 `503`。

在镜像上，daemon 以 root 运行，`AIO_DEFAULT_USER=gem`；命令以 `gem` 执行。

工作目录不是隔离边界。文件路由能触达整台主机的文件系统。隔离是沙箱的职责，不是 daemon 的。

## MCP

`EXTRA_MCP_SERVERS`（或 `--mcp-servers`）注册 loopback、无状态的 streamable-HTTP MCP server。它们的工具和 10 个内置工具一起出现在 `POST /mcp` 上。

只接受 `http://127.0.0.1|localhost|[::1]` 的目标。以下会被跳过并给出告警：

- 远程 server
- `command`（stdio）server
- 需要 session 的 server

1.x 的管理机制已移除：

- `MCP_FILTER_SERVERS`
- `hidden`
- 逐条超时
- `/v1/mcp/*` 管理路由

改用 `/mcp` 上的 `tools/list` 列工具。AIO 镜像上，`mcp-server-browser` 随浏览器一起启动。

## 镜像

### AIO 镜像

`aio-daemon` 把 `aiod` 与 Chromium、VNC、Python 和 Node 工具链、nginx 网关打包在一起。

### Computer 镜像

`aio-computer` 在 AIO 镜像基础上加了 XFCE 桌面和 `computer-use` worker。

### 环境变量

镜像专属环境变量：

| 变量 | 默认值 | 含义 |
| --- | --- | --- |
| `SANDBOX_API_KEY` | 未设置 | `AIO_API_KEY` 的别名 |
| `BROWSER_START_MODE` | `async` | `async` 异步启动浏览器，不阻塞服务就绪；`auto` 等待浏览器启动完成；`manual`（Computer 镜像默认）启动时不启动浏览器，点击桌面上的 Browser 图标后才启动 |
| `DISABLE_CODE_SERVER` | `true` | Code Server IDE 默认关闭 |
| `DISABLE_JUPYTER` | `true` | `/jupyter` 的 Lab 界面关闭；`/v1/jupyter` API 仍可用 |
| `EXTRA_MCP_SERVERS` | 未设置 | 与 `--mcp-servers` 相同的 registry 格式 |
| `MCP_SERVER_BROWSER_PORT` | `8100` | `mcp-server-browser` 监听的端口 |
| `DISABLE_MCP_BROWSER` | 未设置 | `true` 时不启动 `mcp-server-browser` |
| `PROXY_SERVER` / `PROXY_MAP` | 未设置 | 静态代理映射（1.x 的运行时映射 API 已移除） |
| `WORKSPACE` | 账户 home | 必须保持为该账户的 home 目录 |

Computer 镜像额外带 `AIO_DESKTOP=xfce` 和 `ENABLE_DBUS=true`，后者会启动 AT-SPI 需要的 session D-Bus。Chromium 带 `--force-renderer-accessibility` 启动。

### 默认值变更

`JUPYTER_POOL_SIZE` 映射为 `AIO_KERNEL_PREWARM`：默认 `0`，不预热任何内核。镜像上 `AIO_SHELL_BACKEND=native`、`AIO_CODE_BACKEND=native` 是固定值，不做自动探测。

## 构建自定义镜像

两种起点覆盖大多数场景。在 `FROM enterprise-public-cn-beijing.cr.volces.com/vefaas-public/aio-daemon:1.0.0`（或 `aio-computer`）基础上加层，或者把 `aiod` 二进制复制进已有的任意镜像。见 [部署](/zh/daemon/ops/deployment)。

daemon 在请求发生时才从 `PATH` 里解析工具。在 Dockerfile 里装好对应的包就够了：

- 代码执行需要 Python 包和 `ipykernel`
- JavaScript 需要 `node`
- 搜索和终端需要 `rg` 和 `tmux`

`GET /v1/capabilities` 会报告镜像最终具备哪些能力。

镜像里的服务都由 supervisord 管理。新增长驻进程只需在 `/opt/gem/supervisord/` 下放置一个 `.conf` 文件；镜像的 `/etc/supervisord.conf` 会 include 该目录。

生命周期钩子由镜像入口脚本执行，每个都是一段 shell 命令字符串：

- `RUN_HOOK_INIT` —— 在任何东西启动之前执行
- `RUN_HOOK_PRE_SERVICES` —— 在服务启动之前执行
- `RUN_HOOK_POST_READY` —— 在 daemon 就绪之后执行

`RUN_HOOKS_STRICT=true` 让钩子失败变成致命错误（默认 `false`）。

daemon 刻意限制了一些能力，自定义镜像可以解除这些限制：

| Daemon 的限制 | 自定义镜像里的做法 |
| --- | --- |
| `/mcp` hub 只聚合 loopback、无状态的 MCP server。 | 把 MCP server 作为 supervisord 程序运行在镜像中，并列入 `EXTRA_MCP_SERVERS`。 |
| 没有运行时代理映射 API。 | 启动时设置 `PROXY_SERVER` / `PROXY_MAP`。 |
| 没有 skills 增删改查 API。 | 把 skill 目录放到磁盘上，`AIO_SKILLS_PATH` 指向它们；MCP 工具 `sandbox_load_skill` 会读取这些目录。 |
| Code Server 和 JupyterLab 默认关闭。 | 设置 `DISABLE_CODE_SERVER=false`（服务于 `/code-server/`）和 `DISABLE_JUPYTER=false`（服务于 `/jupyter`）。 |
| daemon 从不启动浏览器。 | 镜像负责启动 Chromium；`BROWSER_EXTRA_ARGS` 加启动参数，`HOMEPAGE` 设置起始页。 |
| 默认没有预热的 kernel。 | 设置 `AIO_KERNEL_PREWARM=1`。 |
| ref 套件（`snapshot`、ref 版 `click`/`fill`/`upload`）运行在内置的 CDP 后端上。 | 把 `AIO_AGENT_BROWSER_BIN` 指向一个 agent-browser CLI 即可改由它处理；AIO 镜像自带一个。 |
| daemon 从不启动桌面。 | 使用 `aio-computer`，或者在自己的镜像里提供 X11 display，同时运行 `computer-use` 和 `aiod`。 |

## 1.x SDK 兼容性

1.x 的 SDK 调用 v1 路由，不需要修改就能对接 `aiod`：Python `agent-sandbox` 0.0.31 和 TypeScript `@agent-infra/sandbox` 1.0.17 已在 `aiod` 0.9.x 上验证。Go SDK `github.com/agent-infra/sandbox-sdk-go` v0.0.5 已在 `aiod` 0.9.2 上验证：模块与 Python 一致，方法名按 Go 习惯书写（`file.GrepFiles`、`code.ExecuteCode`、`nodejs.GetInfo`），下表中每个方法的表现都与对应的 Python 方法相同，失败的也是同样那三个调用。SDK 只覆盖 v1；`/v2/*` 通过 HTTP 调用，见 [API 参考](/zh/daemon/api)，运行中的 daemon 也在 `/v2/openapi.json` 提供同一份文档。

### 已验证的方法

| 模块 | 方法 |
| --- | --- |
| `sandbox` | `get_context`、`get_python_packages`、`get_nodejs_packages` |
| `shell` | `exec_command` 及各个 session 方法 |
| `bash` | `exec`、`output`、`write`、`kill`、`create_session`、`sessions`、`close_session` |
| `file` | 除 `watch_events` 外的全部方法：它返回 Server-Sent Events，生成的客户端会按 JSON 解析而失败（Go 上已验证），这条路由直接用 HTTP 读 |
| `jupyter` | `execute_code`、`get_info`、`create_session`、`list_sessions`、`delete_session` |
| `nodejs` | `execute_code`、`get_info`、`create_session`、`list_sessions`、`get_session`、`delete_session` |
| `code` | `execute_code`、`get_info` |
| `browser` | `get_info`、`screenshot`、`set_config`、`execute_action` |
| `browser_tabs` | `list`、`create` |
| `browser_cookies`、`browser_network` | `get_cookies`、`get_requests` |
| `display` | `record` |

以上响应都能被 SDK 的 1.x 模型解析。TypeScript SDK 提供同样的模块，方法名为驼峰（`file.grepFiles`、`code.executeCode`、`nodejs.getInfo`）；`sandbox`、`bash`、`shell`、`file`、`code`、`nodejs`、`browser.getInfo` 和 `browserTabs.list` 已验证，桌面和 Jupyter 方法发出的请求与上面的 Python 方法相同。TypeScript 调用成功返回 `{ ok, body }`，失败返回 `{ ok, error }`，结果在 `body.data`。

### 会失败的调用

以下三个调用在请求阶段就会失败：

| 调用 | 原因 |
| --- | --- |
| `nodejs.update_session` | 发送 `PATCH /v1/nodejs/sessions/{id}`，daemon 返回 `404` |
| `browser_tabs.activate` | 发送 `PUT`，而路由只接受 `POST`，返回 `405` |
| `browser_tabs.close` | 参数是标签页下标，而路由按 CDP target id 定位，返回 `404 no tab with id 1` |

`close` 有绕法：传标签页列表里的 `id` 而不是位置。Python 直接可用，TypeScript 需要一次类型断言；Go 的参数类型是 `int`，表达不了，只能直接用 HTTP 调这个路由。

### 已移除的路由

以下模块调用的路由 daemon 已不再提供，返回 `404`：

- `browser_page.*`、`browser_state.*`、`browser_captcha.*`、`browser.restart`、`browser.get_proxy_pac`
- `mcp.list_mcp_servers`、`mcp.list_mcp_tools`
- `skills.*`
- `sandbox.list_hooks`、`sandbox.register_hook`、`sandbox.remove_hook`、`sandbox.observe_*`
- `proxy.*`
- `util.convert_to_markdown`
- `auth.create_ticket`
