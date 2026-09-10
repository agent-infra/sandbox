# Windows

aiod 在 Windows 上是同一个二进制、同一套 API。鉴权、统一返回结构、OpenAPI 发现方式都一样。下面只列差异，全部内容都在 Windows Server 2022 + Windows PowerShell 5.1 上验证过。

## 与 Linux 的差异

| 差异点 | Linux | Windows |
| --- | --- | --- |
| `/v2/commands` 用的 shell | `bash`、`sh` | 默认 `powershell`，还有 `cmd`、`bash` |
| 终端会话（PTY） | 原生 PTY 或 tmux | ConPTY 上跑 PowerShell |
| 终端会话上的 `exec` | 任何 shell 都能用 | `501`，改用 `/v2/commands` |
| `user` 参数 | 切换执行身份 | 未实现 |
| 进程模型 | 单个进程，自带 supervisor | `aiod.exe`：普通进程或 Session 0 服务 |
| 文件元数据里的 `permissions` | 八进制 mode（`644`） | `readwrite` 或 `readonly` |
| 文件属性 | POSIX 权限 | Hidden/System → `is_hidden: true` |
| 运行时状态 | `/run` 或 `$XDG_RUNTIME_DIR` | `%TEMP%\aiod-0\<hash>`，没有持久状态 |

每个 PTY 会话都运行在自己的 Job Object 中。显式传 `user` 返回 `400`；配置了 `AIO_DEFAULT_USER` 返回 `503`。

Windows 上同样支持包查询：pip 使用解析到的 Python，npm 使用对应的 `.cmd` shim。

以服务方式运行时，Node.js 包清单也可正常获取。服务账户没有 `APPDATA` 和 per-user 全局 prefix，因此 npm 会使用 Node 安装目录本身；机器级全局包就在该目录下。

运行时目录按用户隔离；`--runtime-dir`（或 `AIO_RUNTIME_DIR`）可以改位置。作为服务运行时，`%TEMP%` 是 `C:\Windows\Temp`。

## 命令

### Shell

| `shell` | Windows |
| --- | --- |
| `auto`、`powershell` | `pwsh`，缺失时退回 `powershell` |
| `cmd` | `%ComSpec%`；UTF-8 输出，不回显提示符 |
| `bash` | Git Bash（解析顺序见下文） |
| `sh` | `503`，Windows 没有 POSIX `sh` |
| `none` | 命令必须能解析成可执行文件 |

整个 `bash` 解析过程不涉及 WSL，查找顺序如下：`AIO_BASH_BIN`、`PATH` 中不是 `System32\bash.exe` 的 `bash`，以及 `%ProgramFiles%` 或 `%ProgramFiles(x86)%` 下的 Git 安装。

`none` 不经过 shell，因此无法启动 `echo` 这类内建命令。

超过 8191 字节的 PowerShell 脚本和所有 `cmd` 脚本会先写入运行时目录，再执行。文件会保留在那里，便于检查失败脚本。

### 退出码

退出码由最后一条语句决定：`$?` 为真时为 0；`$?` 为假时，使用最后一个原生程序的非零退出码，没有退出码时为 1。

脚本前面的原生程序失败不会影响后面的成功结果。例如，`cmd /c exit 3; Write-Output ok` 的退出码为 0，与 `bash -c` 一致。`exit N` 和 `Set-StrictMode` 的行为与脚本文件相同。

退出码是进程的原始值，不对 256 取模：`exit 300` 报 300，`exit -1` 报 -1。

daemon 会在脚本末尾追加退出 trailer。脚本以悬空的 `|` 结尾时，管道会延续到 trailer，PowerShell 就把语法错误报在 trailer 那一行。退出码仍是 1。

### 终止与超时

| 信号 | Windows 映射 | 保证 |
| --- | --- | --- |
| `SIGKILL`、`hard_timeout` | Job Object 终止 | 整棵进程树被收掉，包括孙进程 |
| `SIGTERM`（默认）、`SIGINT` | 协作式 `taskkill /T` | 无（尽力而为） |

被终止或超时的命令报 `exit_code: -1`；`hard_timeout` 之后 `status` 是 `"timed_out"`。协作信号是尽力而为：无论进程是否响应，路由都返回 `200`；需要命令一定停下时，再补一发 `SIGKILL`。

### 输出、环境变量、stdin、cwd

- **行尾**：stdout 和 stderr 原样保留子进程写的内容：PowerShell 和 cmd 写 CRLF，Git Bash 写 LF。所有 shell 的输出都是 UTF-8；offset 按字节计。
- **空的 `env` 值**：`env: {"KEY": ""}` 等于删除该变量。PowerShell 把赋空串的变量移除，Windows 进程的环境块也存不下空值。带引号或换行的值正常保留。
- **stdin**：PowerShell 以 `-NonInteractive` 启动，`Read-Host`、`Get-Credential` 等提示会立即失败。写到 `/v2/commands/{id}/stdin` 的数据能被 `[Console]::In.ReadLine()` 和原生程序读到。
- **相对 `cwd`**：相对于 daemon 进程自己的工作目录，与 Linux 一致。作为服务运行时那是系统目录，所以相对 `cwd` 通常得到 `400 Working directory does not exist`。正斜杠可用。

## 文件

### 路径

路径按原样使用，不做归一化。相对路径相对于 daemon 的工作目录，`..` 有效；`C:/dir` 和 `c:\dir` 都可以使用，并会按发送时的写法回显。

不带盘符的 `\name` 表示当前盘的根目录。因此，上传时将 `path` 写成 `\aiod.exe` 会写入 `C:\aiod.exe`。建议使用完整路径。

### 权限与隐藏文件

`permissions` 是 `readwrite` 或 `readonly`，来自文件的只读属性。目录永远是 `readwrite`：Windows 会给 Desktop 这类定制过的文件夹打上该属性，但它对访问没有意义。

`list` 的 `is_hidden` 来自 Hidden 属性和点开头的名字。`search`、`glob`、`grep` 只跳过点开头的名字，带隐藏属性的文件会出现在结果里。glob 里的 `\` 在 Windows 上是路径分隔符。

### 错误状态码

Windows 错误码映射不到 Unix 的 errno 表，同一个错误的状态码可能不同：

| 情况 | Windows | Linux |
| --- | --- | --- |
| 路径不存在 | `404` | `404` |
| 目标已存在 | `409` | `409` |
| 把文件当目录读 | `404` | `400` |
| 往目录上写 | `403` | `400` |

### `read` 和 `edit` 里的 CRLF

整文件 `read` 原样返回字节。按行读取时，会保留每行的 CRLF，只去掉最后一行的终止符。

`str_replace` 按字节匹配。文件使用 CRLF 时，`old_str` 也必须写成 `\r\n`；使用 `\n` 作为锚点会返回 `400 old_str not found in file`。`insert` 会使用文件原有的行尾写入新行。

### 文件变化监听

递归 watch 是根目录上的一个原生 watch，所以被 watch 的子目录可以改名和删除。事件的 `relative_path` 用 `\` 分隔，`inode` 是 `null`，改名到达时是旧名字和新名字各一条 `rename`。

## 终端

`/v2/pty` 和 `/v1/shell` 在 ConPTY 上运行 PowerShell。

`create`、`input`、`screen`、resize、WebSocket attach 和 close 都可用；`screen` 返回原始 VT 流。

`exec` 返回 `501`，因为该协议需要 POSIX shell，请改用 `/v2/commands`。因此，`/v1/capabilities` 会报告 `exec.pty: false`。

`signal` 在所有平台上都用于关闭会话。

## 浏览器

daemon 只探测 CDP，从不启动浏览器。用 `--remote-debugging-port=9222` 启动 Chrome 或 Edge，aiod 探测它的方式和 Linux 上一样。

把 `/cdp/*` 转发成公网可访问的路径是部署方的事。这是宿主机前面反向代理的职责，不是 daemon 做的。

`GET /v1/capabilities` 在 Windows 上也是真探测：`browser.process` 走 `tasklist`，CDP 走 `GET /json/version`。

## 桌面 GUI（computer-use）

发往 secure desktop 的输入会被拒绝，返回 `403`，`data` 里给出原因。常见场景是 UAC 弹窗、锁屏：

```json
{
  "status": "denied",
  "reason": "secure-desktop-or-uipi"
}
```

因此，computer-use 必须作为独立进程运行。Session 0 中的服务没有桌面，其中的 worker 会拒绝所有动作；computer-use 只能运行在交互登录会话中。

aiod 本身不需要桌面，可以作为服务运行。`GET /v2/sandbox` 的 capabilities 部分会返回当前会话的实际探测结果。

## 注册为 Windows 服务

可以将 aiod 注册为 Windows 服务，并配置崩溃自动重启和防火墙规则。请以管理员身份运行以下命令：

```powershell
$exe = "C:\Program Files\aiod\aiod.exe"
sc.exe create aiod binPath= "`"$exe`" service-run --host 0.0.0.0 --port 18091" start= auto obj= LocalSystem
sc.exe failure aiod reset= 86400 actions= restart/5000/restart/5000/restart/30000
New-NetFirewallRule -DisplayName "aiod 18091" -Direction Inbound -Protocol TCP -LocalPort 18091 -Action Allow
sc.exe start aiod
Invoke-RestMethod http://127.0.0.1:18091/health
```

`--port` 设置监听端口。`sc.exe failure` 配置崩溃后的自动重启：最多重启三次，之后间隔 30 秒，计数每天重置。

服务不会显示控制台窗口。日志默认写入 `%ProgramData%\aiod\logs\aiod.log`，可用 `AIO_SERVICE_LOG_FILE` 修改路径。

### Defender

可以将安装目录和运行时目录加入实时防护的排除项，但应保持其他防护开启。

workload 的命令行可能命中 Defender 的机器学习模型。处置动作会终止运行该二进制的进程并隔离文件，主机上的 daemon 也会随之停止。可以通过 `Get-MpThreatDetection` 查看检测结果。

## 运行 computer-use

computer-use 必须在交互登录会话中启动，通常应放在由登录触发的交互式计划任务中。

仓库里的 `scripts/windows/install-computer-use.ps1` 会注册该任务，并等待 worker 的 `/healthz`。更换 `-ExeSource` 后重新运行脚本，即可切换二进制。

ffmpeg 目录是从机器 `PATH` 解析出来的，显式注入任务环境。登录会话的环境变量是登录那一刻的快照，之后改的 `PATH` 任务看不到。

截图和录屏都要用到 ffmpeg（gdigrab）。如果 `PATH` 里明明有目录，`where ffmpeg` 却找不到，先查 ACL。任务账户需要对 ffmpeg 目录的读和执行权限。

## 验证

在 PowerShell 里对着 aiod 监听的端口执行，用 `curl.exe` 绕开 PowerShell 自带的 `curl` 别名：

```powershell
$BASE_URL = "http://127.0.0.1:18091"
curl.exe "$BASE_URL/health"
curl.exe "$BASE_URL/v2/sandbox"
curl.exe -X POST "$BASE_URL/v2/commands" -H "Content-Type: application/json" -d '{"command":"Get-Date"}'
```
