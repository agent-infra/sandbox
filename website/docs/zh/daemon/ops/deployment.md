# 部署与运维

`aiod` 默认在前台运行，可以交给进程管理器无人值守。作为独立二进制文件，它提供 `/health` 和 `/v1/capabilities` 健康检查。

本页按部署流程介绍：安装二进制、配置 supervisor 和 API key、接入健康检查，以及日志、环境变量和常见排障方法。

## 安装二进制文件

安装脚本会下载本机对应的构建，按发布目录里的 `SHA256SUMS` 核对后安装。部署时固定版本，并把二进制放到 supervisor 期望的位置：

```bash
curl -fsSL https://aio-static.tos-cn-beijing.volces.com/install.sh \
  | AIOD_VERSION=0.9.2 AIOD_INSTALL_DIR=/usr/local/bin sh

aiod version
# aio-daemon 0.9.2+<commit>
```

运行桌面 worker 的主机加上 `AIOD_WITH_COMPUTER_USE=1`。每个发布目录（`/v<version>/<platform>/`）也直接提供原始二进制和 `SHA256SUMS`，供自行拉取的镜像构建使用。

选择与目标平台匹配的目录：`linux-x86_64`、`linux-arm64`、`linux-riscv64` 或 `windows-x86_64`（`aiod.exe`）。`latest/<platform>/aiod` 始终指向最新稳定版。

要固定版本，请使用 `v<version>/<platform>/aiod`。发布说明与各文件校验值见 [发布记录](/zh/daemon/start/releases)。

## 使用 supervisor 管理

`aiod start` 在前台运行，没有后台化参数：重启、日志和环境都由 supervisor 负责。用宿主机已有的进程管理器即可。下面的示例统一把服务配置为 `8091` 端口。

**systemd：**

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

**supervisord：** 预构建镜像就是这样和 nginx、Chromium 一起运行 aiod 的：

```ini
[program:aiod]
command=/usr/local/bin/aiod start
environment=AIO_PORT="8091",AIO_API_KEY="my-secret-key"
autorestart=true
stdout_logfile=/var/log/aiod.log
redirect_stderr=true
```

**镜像 `CMD`：** 将二进制文件复制到镜像中，并设为启动命令：

```dockerfile
FROM your-base-image
COPY aiod /usr/local/bin/aiod
RUN chmod +x /usr/local/bin/aiod
ENV AIO_PORT=8091
EXPOSE 8091
CMD ["aiod", "start"]
```

**Docker Compose：** 在同一个容器中运行，并使用 `/health` 做健康检查：

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

**Windows：** `aiod.exe` 可以作为普通进程运行，也可以注册为 SCM 服务（Session 0）。见 [Windows](/zh/daemon/basic/windows)。

即使宿主机没有 bash、解释器、浏览器或可访问的桌面，daemon 仍会启动。

缺失的能力只会让对应路由返回 `503`，不会阻止 daemon 启动。

## 配置 API key

配置 API key，让所有非公开路由都要求鉴权：

```bash
aiod start --api-key my-secret-key
# or: AIO_API_KEY=my-secret-key aiod start
```

普通 HTTP 请求通过 `Authorization: Bearer <key>` 或 `x-api-key: <key>` 发送 key。

对于无法设置请求头的 WebSocket、下载等请求，通过 `?api_key=` 传入 key。

无论是否设置 key，以下路由都保持开放：

- `/`
- `/health`
- `/v1/ping`
- `/v1/openapi.json`
- `/v2/openapi.json`
- `/internal/auth`

未设置 key 时，所有路由都开放。此时应绑定到私有网卡，或不要将端口暴露到公共网络。

## 健康检查与能力就绪状态

| 检查 | 路径 | 检查结果 |
| --- | --- | --- |
| 存活 | `GET /health` | 进程是否在运行（公开，无需 key） |
| 能力就绪 | `GET /v1/capabilities` | 当前可用的域 |

`/v1/capabilities` 缓存 5 秒，在后台刷新。加 `?refresh=true` 可强制一次新探测。它报告的域包括 `files`、`exec`、`code_interpreter`、`browser`、`computer`。

如果 `/health` 失败，重启 daemon。

是否接收流量应根据 `/v1/capabilities` 判断，不要只检查 `/health`。

进程存活并不代表所有能力都可用，以下情况仍可能导致某项能力降级或缺失：

- 宿主没有 bash
- 没有解释器
- 没有可达的 Chromium
- 没有桌面

两者都可以直接检查：

```bash
curl -fsS "$BASE_URL/health"
curl -fsS "$BASE_URL/v1/capabilities?refresh=true" -H "Authorization: Bearer $AIO_API_KEY"
```

## 日志

aiod 向 stdout 写结构化 JSON，每个请求一行。每行标记为 `HTTP_REQUEST`，带 method、path、status、`duration_ms`、`logid`、`client_ip`。

使用容器日志驱动或 supervisor 收集 stdout 即可。没有单独的日志文件需要 tail。
`AIO_RUST_LOG_LEVEL`（默认 `info`）控制日志详细程度。

## 环境变量

| 变量 | 默认值 | 含义 |
| --- | --- | --- |
| `AIO_HOST` | `0.0.0.0` | 绑定地址 |
| `AIO_PORT` | `18091` | 绑定端口 |
| `AIO_API_KEY` | 未设置 | 让受保护路由要求 key |
| `AIO_RUNTIME_DIR` | 自动 | pid、socket、临时状态 |
| `AIO_DEFAULT_USER` | daemon 账户 | 命令、解释器、文件属主使用的账户（仅 Linux） |
| `AIO_API_SURFACE` | `full` | `full`（v1 + v2）或仅 `v2` |
| `AIO_RUST_LOG_LEVEL` | `info` | 日志过滤级别 |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | 未设置 | 设置后开启 OTLP trace 导出 |

每个参数都有对应的环境变量（例如 `--host`/`AIO_HOST`、`--port`/`AIO_PORT`）。同时设置时，命令行参数优先。

## 排障

- **`/v1/nodejs`、`/v1/code`、`/v2/code` 返回 `503`**：宿主机没有匹配的解释器。安装 `python3` 或 `node`；`capabilities.code_interpreter.missing` 会指出缺少什么。
- **`/v1/jupyter` 返回 `501`**：没有可导入的 `ipykernel`，也没有设置 `AIO_JUPYTER_ENDPOINT`。安装 `ipykernel`，或将 `AIO_JUPYTER_ENDPOINT` 指向 Jupyter server。
- **`/v1/browser/*` 返回 `503`**：`BROWSER_REMOTE_DEBUGGING_HOST:PORT`（默认 `127.0.0.1:9222`）上没有 Chromium。使用 `--remote-debugging-port=9222` 启动 Chromium。
- **`/v2/computer/*` 返回 `503`**：`computer-use` worker 不可达。启动 worker，并检查 `AIO_COMPUTER_USE_URL`（默认 `http://127.0.0.1:18100`）。
- **所有 `/v1/*` 或 `/v2/*` 调用返回 `401`**：已设置 `AIO_API_KEY`。带上 `Authorization: Bearer <key>` 或 `x-api-key: <key>`；WebSocket 和下载请求使用 `?api_key=`。
- **连接 `/v1/shell/ws` 后立刻返回 `400`**：设置了 `durable=true` 或 `restore=true`，但没有 `session_id`。先调用 `POST /v1/shell/sessions/create`，再使用 `?session_id=<id>` 连接。

运行中的 daemon 会通过 OpenAPI spec 提供每个路由的完整请求和响应定义：`/v1/openapi.json`、`/v2/openapi.json`。

v2 参考文档见 [API 参考](/zh/daemon/api)，Kubernetes 专属指引见 [Kubernetes](/zh/daemon/ops/kubernetes)。
