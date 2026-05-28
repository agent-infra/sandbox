# FAQ

This FAQ is written for the open-source Docker and SDK workflow.

## Docker

### Port 8080 Is Already In Use

Map the container to a different host port:

```bash
docker run --security-opt seccomp=unconfined --rm -it -p 3000:8080 ghcr.io/agent-infra/sandbox:latest
```

Then use `http://localhost:3000` as the sandbox base URL.

### The Browser Does Not Start

Make sure the container has enough memory and that it is started with the recommended seccomp option:

```bash
docker run --security-opt seccomp=unconfined --rm -it -p 8080:8080 ghcr.io/agent-infra/sandbox:latest
```

If you run in a restricted container runtime, also check whether Chromium sandboxing or shared-memory limits need additional runtime flags.

## SDK And API

### The SDK Cannot Connect

Check that the base URL points to the host port you mapped:

```python
from agent_sandbox import Sandbox

client = Sandbox(base_url="http://localhost:8080")
print(client.sandbox.get_context())
```

### How Should Errors Be Handled?

Handle errors in layers:

- Non-2xx HTTP responses indicate transport, validation, auth, or server errors.
- A JSON response with `success: false` indicates a tool-level failure.
- Execution APIs can also report domain fields such as `status`, `exit_code`, or stderr output.

See [Error Handling](/guide/basic/error-handling) for the recommended pattern.

## Browser

### Screenshots Work But Browser Automation Fails

Check whether the page is fully loaded, whether the target element is visible, and whether the automation method matches your task. Use CDP or page APIs for DOM-level automation, and GUI actions for visual desktop-level interaction.

### Where Do Downloads Go?

Chromium downloads normally land in the user downloads directory, such as `/home/gem/Downloads`. Use the file API to inspect or retrieve downloaded files.

## MCP

### Do I Need A Separate MCP Server?

No. AIO Sandbox exposes an aggregated MCP endpoint at `/mcp`. You can connect an MCP-compatible client directly to that endpoint.

### Why Are Some Low-Level Browser Tools Hidden?

The MCP endpoint focuses on commonly used tools by default. Prefer the documented browser APIs or high-level MCP tools unless you need low-level CDP behavior.

## Customization

### How Do I Preinstall Dependencies?

Build a custom image from the public AIO Sandbox image and install your packages in the Dockerfile. For runtime-only setup, use lifecycle hooks described in [AIO Hooks](/guide/advanced/lifecycle).

### How Do I Set A Default Workspace?

Set `WORKSPACE` when starting the container. See [Workspace](/guide/advanced/workspace).
