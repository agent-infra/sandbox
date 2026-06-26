# Code Server Configuration

AIO Sandbox includes code-server so you can open a browser-based VS Code environment inside the sandbox.

## Access

```text
http://localhost:8080/code-server/
```

The editor shares the same filesystem as shell, browser downloads, Jupyter, and file APIs.

## Environment Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `CODE_SERVER_PORT` | `8200` | Internal code-server port |
| `DISABLE_CODE_SERVER` | `false` | Disable code-server when set to a truthy value |
| `WORKSPACE` | `/home/gem` | Default folder opened by code-server |

## Install Extensions At Startup

Use a lifecycle hook for light customization:

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 127.0.0.1:8080:8080 \
  -e RUN_HOOK_PRE_SERVICES="code-server --install-extension ms-python.python" \
  ghcr.io/agent-infra/sandbox:latest
```

For repeatable team environments, build a custom image with extensions preinstalled.

## Tips

- Mount project code into `WORKSPACE`.
- Use [Preview Proxy](/guide/advanced/proxy-network) to view apps started from the editor terminal.
- Disable code-server in API-only deployments to reduce resource usage.

