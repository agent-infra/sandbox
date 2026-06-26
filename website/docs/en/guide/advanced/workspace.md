# Workspace

`WORKSPACE` controls the default working directory used by AIO Sandbox services.

## Basic Usage

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 127.0.0.1:8080:8080 \
  -e WORKSPACE=/workspace \
  -v "$PWD:/workspace" \
  ghcr.io/agent-infra/sandbox:latest
```

On startup, the container creates the workspace directory when needed and prepares permissions for the runtime user.

## Service Behavior

| Service | Default directory | Per-request override |
| --- | --- | --- |
| Shell | `$WORKSPACE` | `exec_dir` |
| Bash | `$WORKSPACE` | `exec_dir` |
| Jupyter | `$WORKSPACE` | request options |
| Node.js | `$WORKSPACE` | request options |
| code-server | `$WORKSPACE` | open folder |

## Recommendations

- Mount project code into the workspace for coding-agent tasks.
- Store generated artifacts under the workspace so browser, shell, file, and code APIs can share them.
- Avoid writing long-lived project files under temporary directories unless you plan to download them immediately.

