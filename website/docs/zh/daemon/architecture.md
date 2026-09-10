# 架构

`aiod` 是 AIO Sandbox 的核心 daemon 进程，提供沙箱工具 API 和 MCP 端点。

shell、解释器、浏览器和桌面均由独立进程提供。aiod 只在运行时探测这些进程，不负责启动它们。

## daemon 进程

它通过 HTTP 和 WebSocket 提供 commands、files、terminals（PTY）、代码执行和浏览器控制，并承载 `POST /mcp`。

![](/architecture/aiod-overview.svg)

浏览器是监听 `BROWSER_REMOTE_DEBUGGING_HOST:PORT`（默认 `127.0.0.1:9222`）并响应 CDP 的 Chromium 进程，可以由任意进程启动。

桌面由 `AIO_COMPUTER_USE_URL`（默认 `http://127.0.0.1:18100`）上的 `computer-use` worker 提供。

aiod 只把 `/v2/computer/*` 转发给它，不直接访问显示设备。worker 必须作为独立进程运行，因为它需要桌面会话。

Windows 上的区别尤其明显：aiod 可以作为 Session 0 服务运行，但 computer-use 必须运行在交互式登录会话中（见 [Windows](/zh/daemon/basic/windows)）。

## 依赖与能力

aiod 始终可以启动。启动时及每次能力检查时，它都会探测依赖是否可达，并将结果写入 capabilities：

![](/architecture/aiod-capabilities.svg)

| 依赖 | 探测方式 | 启用的路由 |
| --- | --- | --- |
| Shell | `PATH` 上的 `bash`；Windows 上是 PowerShell | `/v2/commands`、`/v2/pty` 及对应的 v1 路由 |
| 解释器 | `PATH` 上的 `python3`、`node`，或 `AIO_JUPYTER_ENDPOINT` | `/v2/code`、`/v1/code`、`/v1/jupyter`、`/v1/nodejs` |
| 浏览器 | 调试端口上的 CDP `GET /json/version` | `/v2/browser`、`/v1/browser` |
| 桌面 GUI | `AIO_COMPUTER_USE_URL` 上的 `computer-use` worker | `/v2/computer` |

依赖缺失时，只有依赖该能力的路由返回 `503`。

其他功能不受影响，daemon 仍会绑定端口。

`GET /v1/capabilities` 返回当前能力状态。结果会缓存 5 秒，并在后台刷新；加上 `?refresh=true` 可以强制重新探测。

`aiod doctor --json` 在命令行执行同样的探测。返回结构见 [沙箱信息与能力](/zh/daemon/basic/sandbox)。

## 状态保存在内存中

Command 会话、PTY 会话、代码会话、保留的输出、文件 watcher 和编辑器撤销历史都保存在进程内存中，不会写入磁盘。

重启或升级后，这些状态都会丢失，客户端需要重新开始。已经写入磁盘的文件不受影响。

## 权限模型

调用涉及两类身份，但这两类身份都不提供沙箱隔离：

| 身份 | 决定什么 |
| --- | --- |
| daemon 账户（Linux 上是 `AIO_DEFAULT_USER`） | 每一次文件和命令调用的权限 |
| 请求里的 `user`，用于 commands、terminals、code | 进程以哪个账户运行 |
| 请求里的 `user`，用于 files | 新建对象归谁所有 |

![](/architecture/aiod-permission-model.svg)

调用可以访问 daemon 账户在宿主机上有权限访问的任意位置。aiod 不提供按请求隔离的 jail、chroot 或路径白名单；如果需要限制目录或租户范围，应由沙箱负责。

Windows 尚未实现 `user`，显式传入时返回 `400`。

API 的访问只有一道门：`AIO_API_KEY`，在每个非公开路由上检查（见 [鉴权](/zh/daemon/basic/authentication)）。

## 运行 daemon

接入镜像只需要拷贝一个文件：

```dockerfile
FROM your/base-image
COPY aiod /usr/local/bin/aiod
CMD ["aiod", "start"]
```

`aiod start` 没有必填参数，默认绑定 `0.0.0.0:18091`，并使用 daemon 账户的 home 目录作为工作目录。运行时目录由 aiod 自行解析。

可以直接把它作为容器的启动命令，也可以交给已有的 supervisor 管理，例如 systemd、s6 或自定义 init。

一条更完整的启动命令，对应带非特权账户和 API key 的镜像：

```bash
# Every flag has an environment variable of the same meaning:
# AIO_HOST, AIO_PORT, AIO_API_KEY, AIO_DEFAULT_USER, AIO_API_SURFACE, AIO_RUNTIME_DIR.
aiod start \
  --host 0.0.0.0 \
  --port 18091 \
  --api-key "$API_KEY" \
  --default-user gem \
  --api-surface full \
  --runtime-dir /run/aiod
```

`--default-user` 设置请求的默认执行账户，但请求可以指定其他账户。`--api-surface v2` 只提供 `/v2/*` 和 `/mcp`。

`aiod -h` 列出子命令：`start`、`doctor`、`version` 和 `print-openapi`。`aiod start --help` 列出每个参数、对应的环境变量和默认值。

`aiod doctor` 不会启动 daemon，只探测主机上的 `bash`、`rg`、`tmux`、浏览器进程和 CDP 端口，并逐项输出结果。

编排时要看两个检查：

```bash
curl "$BASE_URL/health"          # liveness: the process is up (no key needed)
curl "$BASE_URL/v1/capabilities" # readiness per capability: browser, code, desktop right now
```

重启策略看 `/health`；浏览器、代码和桌面流量则根据 `/v1/capabilities` 中对应的能力状态路由。

在 Kubernetes 上，通常由一个容器运行 aiod；需要桌面时再加入 computer-use。

如果 pod 内还运行 Chromium，需要允许其 seccomp profile，并为 `/dev/shm` 分配足够空间。没有更严格配置时，可以使用 `unconfined`；4 GiB 是安全默认值。

这些是 Chromium 的要求，不是 aiod 额外增加的要求。

`aiod version` 打印 `aio-daemon <version>+<commit>`。`aiod print-openapi` 将完整 spec 输出到 stdout。

daemon 提供 `/openapi.json`、`/v1/openapi.json` 和 `/v2/openapi.json`，但不提供文档 UI。v2 参考文档见 [API 参考](/zh/daemon/api)。

## 支持的平台

aiod 以静态二进制形式发布，覆盖 Linux（x86_64、arm64、riscv64）和 Windows（x86_64）。运行它不需要共享库，也不需要预装运行时。
