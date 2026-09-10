# Windows

aiod on Windows is the same binary and the same API. Auth, the response envelope, and OpenAPI discovery work the same way. This page covers the differences. Everything below was verified on Windows Server 2022 with Windows PowerShell 5.1.

## Differences from Linux

| Area | Linux | Windows |
| --- | --- | --- |
| Shell for commands (`/v2/commands`) | `bash`, `sh` | `powershell` (default), `cmd`, `bash` |
| Terminal sessions (PTY) | Native PTY or tmux | ConPTY on PowerShell |
| `exec` on a terminal session | Works on any shell | `501`; use `/v2/commands` |
| `user` request field | Switches execution identity | Not implemented |
| Process model | One process, own supervisor | `aiod.exe` as a process or Session 0 service |
| `permissions` in file metadata | Octal mode (`644`) | `readwrite` or `readonly` |
| File attributes | POSIX permissions | Hidden/System → `is_hidden: true` |
| Runtime state | `/run` or `$XDG_RUNTIME_DIR` | `%TEMP%\aiod-0\<hash>`, nothing durable |

Each PTY session runs inside a Job Object. An explicit `user` answers `400`; a configured `AIO_DEFAULT_USER` answers `503`.

Package queries work on Windows too: pip via the resolved Python, npm via its `.cmd` shim. The Node.js listing works under a service as well — a service account has no `APPDATA` and so no per-user global prefix, so npm is pointed at the Node install's own directory, where a machine-wide install keeps its global packages.

The runtime directory is per user; `--runtime-dir` (or `AIO_RUNTIME_DIR`) moves it. For a service, `%TEMP%` is `C:\Windows\Temp`.

## Commands

### Shells

| `shell` | Windows |
| --- | --- |
| `auto`, `powershell` | `pwsh`, falling back to `powershell` |
| `cmd` | `%ComSpec%`; UTF-8 output, no prompt echo |
| `bash` | Git Bash (resolution order below) |
| `sh` | `503`; there is no POSIX `sh` |
| `none` | The command must resolve as an executable |

`bash` resolution never involves WSL: it checks `AIO_BASH_BIN`, then a `bash` on `PATH` that is not `System32\bash.exe`, then a Git install under `%ProgramFiles%` or `%ProgramFiles(x86)%`. With `none` there is no shell, so a builtin such as `echo` fails to spawn. A PowerShell script longer than 8191 bytes, and every `cmd` script, is written under the runtime directory and run from there; the file is left behind, so a failed script stays inspectable.

### Exit codes

The last statement decides. `$?` true → 0. `$?` false → the last native program's exit code when it is nonzero, else 1. A native failure earlier in the script does not leak into a successful ending: `cmd /c exit 3; Write-Output ok` exits 0, as `bash -c` would. `exit N` and `Set-StrictMode` behave as in a script file.

Exit codes are the raw process value, not reduced modulo 256: `exit 300` reports 300 and `exit -1` reports -1.

The daemon appends its exit trailer to the script. A script that ends in a dangling `|` continues its pipeline into the trailer, so PowerShell reports the syntax error at the trailer's line. The exit code is still 1.

### Kill and timeout

| Signal | Windows mapping | Guarantee |
| --- | --- | --- |
| `SIGKILL`, `hard_timeout` | Job Object termination | The whole tree is gone, grandchildren included |
| `SIGTERM` (default), `SIGINT` | Cooperative `taskkill /T` | None (best effort) |

A killed or timed-out command reports `exit_code: -1`, with `status: "timed_out"` after `hard_timeout`. Cooperative signals are best effort: the route answers `200` whether the process acts on them or not. Follow one with `SIGKILL` when the command has to stop.

### Output, environment, stdin, cwd

- **Line endings** — stdout and stderr keep what the child wrote: PowerShell and cmd write CRLF, Git Bash writes LF. Output is UTF-8 on every shell; offsets count bytes.
- **Empty `env` value** — `env: {"KEY": ""}` unsets the variable. PowerShell removes a variable assigned the empty string, and a Windows environment block cannot hold an empty value. Values with quotes or newlines survive.
- **stdin** — PowerShell runs with `-NonInteractive`, so `Read-Host`, `Get-Credential`, and other prompts fail at once. Data written to `/v2/commands/{id}/stdin` reaches `[Console]::In.ReadLine()` and native programs.
- **Relative `cwd`** — Resolves against the daemon process's working directory, as on Linux. Under a service that directory is a system location, so a relative `cwd` normally answers `400 Working directory does not exist`. Forward slashes are accepted.

## Files

### Paths

Paths are used as given, without normalisation: a relative path resolves against the daemon's working directory, `..` is honoured, and `C:/dir` and `c:\dir` both work and are echoed back as sent. A driveless `\name` means the current drive's root, so an upload `path` of `\aiod.exe` lands at `C:\aiod.exe`. Send full paths.

### Permissions and hidden files

`permissions` is `readwrite` or `readonly`, from the file's read-only attribute. A directory is always `readwrite`: Windows sets the attribute on customised folders such as Desktop without it meaning anything for access.

`list` sets `is_hidden` from the Hidden attribute and from dot-prefixed names. `search`, `glob`, and `grep` skip dot-prefixed names only, so attribute-hidden files appear in their results. A `\` in a glob is a path separator on Windows.

### Error statuses

Windows error codes do not map onto the Unix errno table, so the same mistake can answer differently:

| Case | Windows | Linux |
| --- | --- | --- |
| Path does not exist | `404` | `404` |
| Target already exists | `409` | `409` |
| Read through a file as if it were a directory | `404` | `400` |
| Write onto a directory | `403` | `400` |

### CRLF in read and edit

A full `read` returns the bytes verbatim. A line-range `read` keeps each line's CRLF and drops only the last line's terminator. `str_replace` matches bytes, so `old_str` must contain `\r\n` where the file does; a `\n` anchor answers `400 old_str not found in file`. `insert` writes new lines with the file's own ending.

### Watch files

A recursive watch is one native watch on the root, so directories under it can be renamed and deleted while watched. Events carry `relative_path` with `\` separators, `inode` is `null`, and a rename arrives as one `rename` for the old name and one for the new name.

## Terminal

`/v2/pty` and `/v1/shell` run PowerShell over ConPTY. `create`, `input`, `screen`, resize, the WebSocket attach, and close all work; `screen` returns the raw VT stream. `exec` answers `501` because its protocol needs a POSIX shell; use `/v2/commands`. `/v1/capabilities` reports `exec.pty: false` for that reason. `signal` closes the session, on every platform.

## Browser

The daemon only probes CDP; it never launches a browser. Start Chrome or Edge with `--remote-debugging-port=9222`; aiod picks it up the same way it does on Linux.

Forwarding `/cdp/*` to a public path is the deployment's job. The reverse proxy in front of the host does this, not the daemon.

`GET /v1/capabilities` probes for real on Windows too: `browser.process` via `tasklist`, CDP via `GET /json/version`.

## Desktop (computer-use)

Input aimed at the secure desktop is refused with `403`, and `data` names the reason. This includes a UAC prompt and the lock screen:

```json
{
  "status": "denied",
  "reason": "secure-desktop-or-uipi"
}
```

This is the rule that forces computer-use into its own process. A Session 0 service has no desktop, so a worker started there would refuse every action; computer-use has to run in the interactive logon session. aiod itself needs no desktop and can run as a service. The capabilities section of `GET /v2/sandbox` reports what the current session actually probed.

## Register aiod as a service

You can register aiod as a Windows service, configure automatic restarts, and open its port in the firewall. Run these commands as an administrator:

```powershell
$exe = "C:\Program Files\aiod\aiod.exe"
sc.exe create aiod binPath= "`"$exe`" service-run --host 0.0.0.0 --port 18091" start= auto obj= LocalSystem
sc.exe failure aiod reset= 86400 actions= restart/5000/restart/5000/restart/30000
New-NetFirewallRule -DisplayName "aiod 18091" -Direction Inbound -Protocol TCP -LocalPort 18091 -Action Allow
sc.exe start aiod
Invoke-RestMethod http://127.0.0.1:18091/health
```

`--port` sets the listening port. `sc.exe failure` configures automatic restarts: up to three restarts after a crash, then a 30 s gap; the counter resets daily.

A service has no console window. Logs go to `%ProgramData%\aiod\logs\aiod.log` by default; override the path with `AIO_SERVICE_LOG_FILE`.

### Defender

Exclude the installation directory and the runtime directory from real-time protection, and keep protection on for everything else. A workload command line can match Defender's machine-learning models; the remediation then terminates every process running the binary and quarantines the file, so every daemon on the host disappears at once. `Get-MpThreatDetection` shows the detection.

## Running computer-use

computer-use has to start inside the interactive logon session, so a logon-triggered, interactive scheduled task is the usual home for it. The repository's `scripts/windows/install-computer-use.ps1` registers one and waits for the worker's `/healthz`; re-running it with a new `-ExeSource` swaps the binary.

The ffmpeg directory is resolved from the machine `PATH`. It is injected into the task environment explicitly. A logon session's environment is snapshotted at logon; a later `PATH` edit is invisible to the task.

Screenshot and recording both need ffmpeg (gdigrab). If `where ffmpeg` finds nothing although `PATH` lists the directory, check the ACL. The task account needs read and execute on the ffmpeg directory.

## Verify

Run these in PowerShell against the port aiod listens on; `curl.exe` avoids the PowerShell `curl` alias:

```powershell
$BASE_URL = "http://127.0.0.1:18091"
curl.exe "$BASE_URL/health"
curl.exe "$BASE_URL/v2/sandbox"
curl.exe -X POST "$BASE_URL/v2/commands" -H "Content-Type: application/json" -d '{"command":"Get-Date"}'
```
