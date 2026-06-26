# Agent Call Sandbox vs In Sandbox

AIO Sandbox supports two common integration modes: the agent can call sandbox APIs from outside, or the agent can run inside the sandbox container. The main difference is where you keep orchestration logic, credentials, network access, and task execution.

## Mode Comparison

| | Agent Call Sandbox | Agent In Sandbox |
| --- | --- | --- |
| Agent location | Host machine, local service, remote service, notebook | Inside the sandbox container |
| Interaction model | REST API / SDK / MCP | Local commands / localhost REST API / `aio` CLI |
| Typical use cases | SaaS agents, remote development, multi-sandbox orchestration | Coding agents, CI/CD, isolated execution |
| Network requirement | The agent must reach the sandbox entry port | The agent can call `127.0.0.1:8080` directly |
| Resource limits | Agent process is outside sandbox limits | Agent and task share sandbox resources |
| Shared state | Shared through File / Shell / Browser APIs | Shared through the container filesystem and process environment |

## Agent Call Sandbox

In this mode the agent runs outside the sandbox and calls sandbox capabilities through REST APIs, the Python SDK, the TypeScript SDK, or MCP.

```text
┌──────────────────┐         ┌──────────────────┐
│ Agent (external) │  HTTP   │ AIO Sandbox      │
│ - LLM / planner  │ ──────> │ - Shell          │
│ - orchestration  │ <────── │ - File           │
│ - credentials    │ :8080   │ - Browser        │
└──────────────────┘         └──────────────────┘
```

Use this mode when:

- Your application already runs in a service, worker, notebook, or local process.
- You want to create, reuse, or tear down sandbox environments from outside.
- The agent should keep its own credentials and orchestration logic outside the isolated environment.
- One agent needs to manage multiple sandboxes for parallel development, comparison testing, or batch tasks.
- You want to connect an existing agent framework through MCP.

Typical flow:

1. Start AIO Sandbox with Docker.
2. Configure the client with `base_url="http://localhost:8080"`.
3. Use APIs such as `/v1/shell/exec`, `/v1/file/read`, `/v1/browser/*`, `/v1/code/execute`, or `/mcp`.

### Python SDK

```python
from agent_sandbox import Sandbox

sandbox = Sandbox(base_url="http://localhost:8080")

result = sandbox.shell.exec_command(command="pwd && ls -la")
print(result.data.output)

sandbox.file.write_file(
    file="/home/gem/workspace/task.txt",
    content="Build a small demo app",
)
```

### TypeScript SDK

```typescript
import { SandboxClient } from "@agent-infra/sandbox";

const sandbox = new SandboxClient({
  baseUrl: "http://localhost:8080",
});

const shell = await sandbox.shell.execCommand({
  command: "pwd && ls -la",
});

if (!shell.ok) {
  throw new Error("Shell command failed");
}

await sandbox.file.writeFile({
  file: "/home/gem/workspace/task.txt",
  content: "Build a small demo app",
});

const context = await sandbox.sandbox.getContext();
console.log(context.body);
```

### MCP Integration

AIO Sandbox exposes an `/mcp` endpoint. MCP-compatible agent clients can use this endpoint to discover and call sandbox tools.

```json
{
  "mcpServers": {
    "aio-sandbox": {
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

MCP is useful when you want to expose the sandbox as a standard tool provider: the agent handles reasoning and planning, while AIO Sandbox provides isolated shell, file, browser, and code execution tools.

### Multi-Sandbox Orchestration

One advantage of Call Sandbox is that the orchestrator can connect to multiple sandboxes at once. Each sandbox runs as a separate container with its own host port, which is useful for parallel experiments, regression checks, or task isolation.

```bash
docker run --rm -d --name sandbox-react -p 127.0.0.1:8080:8080 \
  ghcr.io/agent-infra/sandbox:latest

docker run --rm -d --name sandbox-vue -p 127.0.0.1:8081:8080 \
  ghcr.io/agent-infra/sandbox:latest
```

```python
from agent_sandbox import Sandbox

sandboxes = {
    "react": Sandbox(base_url="http://localhost:8080"),
    "vue": Sandbox(base_url="http://localhost:8081"),
}

for name, sandbox in sandboxes.items():
    sandbox.file.write_file(
        file="/home/gem/workspace/variant.txt",
        content=f"variant={name}\n",
    )
    result = sandbox.shell.exec_command(
        command="cat /home/gem/workspace/variant.txt",
    )
    print(name, result.data.output)
```

```typescript
import { SandboxClient } from "@agent-infra/sandbox";

const sandboxes = [
  new SandboxClient({ baseUrl: "http://localhost:8080" }),
  new SandboxClient({ baseUrl: "http://localhost:8081" }),
];

await Promise.all(
  sandboxes.map((sandbox, index) =>
    sandbox.shell.execCommand({
      command: `echo sandbox-${index} > /home/gem/workspace/id.txt`,
    }),
  ),
);
```

If you need to compare web UI results, start one app in each sandbox and then collect screenshots, logs, and artifacts through the browser and preview APIs.

## Agent In Sandbox

In this mode the agent process runs inside the sandbox container. It can call local commands and local REST endpoints directly.

```text
┌─────────────────────────────────────┐
│ AIO Sandbox Container               │
│ ┌─────────────────────────────────┐ │
│ │ Agent process                   │ │
│ │ - local commands                │ │
│ │ - local files                   │ │
│ │ - http://127.0.0.1:8080         │ │
│ └─────────────────────────────────┘ │
│ Shell / File / Browser / Code        │
└─────────────────────────────────────┘
```

Use this mode when:

- You want the agent, tools, source code, and generated files to share the same filesystem.
- You are building a coding agent or CI-style workflow that should run inside the isolated environment.
- You want to use the built-in `aio` CLI from a terminal session.
- The agent process itself should be isolated from the host environment.

### Startup Options

**Option 1: run an agent script when Docker starts.**
Use this when you want the agent script to start with the container. The example mounts a local `agent.py` into the container and runs it after the sandbox service starts.

```bash
docker run --rm -it -p 127.0.0.1:8080:8080 \
  -v "$PWD/agent.py:/home/gem/agent.py" \
  ghcr.io/agent-infra/sandbox:latest \
  bash -lc "/entrypoint.sh & sleep 5 && python /home/gem/agent.py"
```

**Option 2: start the agent through the Shell API.**
Use this when you want to start a standard sandbox first, then install and run the agent inside it from an external control plane.

```bash
curl -X POST http://localhost:8080/v1/shell/exec \
  -H "Content-Type: application/json" \
  -d '{"command": "pip install my-agent && my-agent start"}'
```

**Option 3: start directly inside the container (recommended).**
Use this from inside the container, Web Terminal, or an automation script that already runs in the sandbox shell. The agent process runs inside the sandbox and can access the same filesystem and `127.0.0.1:8080`.

```bash
python -m pip install my-agent
my-agent start
```

### Local Commands Plus Localhost API

An in-sandbox agent can use local commands for files and processes, then call localhost APIs for browser automation, code execution, file watching, and other sandbox services.

```python
import subprocess

import requests

result = subprocess.run(
    ["python", "--version"],
    capture_output=True,
    text=True,
    check=True,
)
print(result.stdout)

response = requests.post(
    "http://127.0.0.1:8080/v1/file/write",
    json={
        "file": "/home/gem/workspace/agent-note.txt",
        "content": "created from an in-sandbox agent\n",
    },
    timeout=10,
)
response.raise_for_status()
```

### AIO CLI (Tool Calls Inside the Container)

An in-sandbox agent does not always need an SDK for every capability. Use `aio` CLI for browser, GUI, MCP, and Skills tool calls. For shell commands and file reads or writes, prefer local commands or the localhost REST API.

```bash
# Browser automation
aio browser navigate http://127.0.0.1:3000
aio browser screenshot -o /tmp/page.png

# MCP and Skills
aio mcp list
aio skills list

# Sandbox information
aio sandbox info
```

See [AIO CLI](/guide/basic/aio-cli.md) for more CLI commands. If you want to package repeated agent operations, combine it with [Skills](/guide/basic/skills.md).

## How To Choose

```text
Your agent needs to...

├── Access external services, databases, or control planes
│   └── Agent Call Sandbox
│
├── Operate multiple sandboxes at once
│   └── Agent Call Sandbox
│
├── Connect through an existing MCP-compatible client
│   └── Agent Call Sandbox + MCP
│
├── Isolate the agent process itself
│   └── Agent In Sandbox
│
├── Code, build, and test directly inside the container
│   └── Agent In Sandbox
│
└── Keep scheduling outside while a child agent runs inside
    └── Hybrid
```

The two modes can also be combined: an external agent creates, schedules, and cleans up sandboxes, then starts a child agent inside the sandbox through the Shell API or an in-container command. This keeps orchestration outside while task execution stays inside the isolated environment.
