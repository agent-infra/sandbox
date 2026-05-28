# AIO Hooks

AIO Hooks let you run startup commands at defined points in the container lifecycle. They are useful for installing lightweight dependencies, preparing files, or starting companion processes.

## Startup Order

```text
container starts
  -> RUN_HOOK_INIT
  -> runtime user and workspace are prepared
  -> RUN_HOOK_PRE_SERVICES
  -> managed services start
  -> readiness checks pass
  -> RUN_HOOK_POST_READY
```

## Hooks

| Hook | Use for |
| --- | --- |
| `RUN_HOOK_INIT` | Earliest initialization that must run before services are prepared |
| `RUN_HOOK_PRE_SERVICES` | Installing tools or writing config before supervised services start |
| `RUN_HOOK_POST_READY` | Warm-up tasks that need the API, browser, or code-server to be available |

## Example

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 8080:8080 \
  -e RUN_HOOK_PRE_SERVICES="python -m pip install requests" \
  ghcr.io/agent-infra/sandbox:latest
```

For heavier customization, prefer a custom Docker image so startup remains fast and reproducible.

## Runtime Shutdown Hooks

You can also register shutdown hooks while the sandbox is running. These hooks are useful for flushing state or writing a marker before the sandbox exits. The runtime API currently supports the `shutdown` event.

```bash
curl -X POST "http://localhost:8080/v1/sandbox/hooks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "write-shutdown-marker",
    "event": "shutdown",
    "command": "printf stopped > /home/gem/workspace/shutdown.txt",
    "timeout": 10,
    "priority": 100
  }'
```

List registered hooks:

```bash
curl "http://localhost:8080/v1/sandbox/hooks?event=shutdown"
```

Remove an API-registered hook:

```bash
curl -X DELETE "http://localhost:8080/v1/sandbox/hooks/write-shutdown-marker"
```

## Guidelines

- Keep hook commands idempotent.
- Keep secrets out of hook values and image layers.
- Use custom images for large dependencies.
- Use [Workspace](/guide/advanced/workspace) for mounted project files.
