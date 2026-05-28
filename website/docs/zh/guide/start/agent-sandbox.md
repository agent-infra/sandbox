# Agent Call Sandbox vs In Sandbox

AIO Sandbox 支持两种常见集成模式：Agent 在沙盒外调用沙盒 API，或 Agent 直接运行在沙盒内部。核心区别是控制逻辑、凭据、网络访问和任务执行环境放在哪里。

## 模式对比

| | Agent Call Sandbox | Agent In Sandbox |
| --- | --- | --- |
| Agent 位置 | 宿主机、本地服务、远端服务、Notebook | 沙盒容器内部 |
| 交互方式 | REST API / SDK / MCP | 本地命令 / localhost REST API / `aio` CLI |
| 典型场景 | SaaS Agent、远程开发、多沙盒编排 | Coding Agent、CI/CD、隔离执行 |
| 网络要求 | Agent 需要访问沙盒入口端口 | Agent 可直连 `127.0.0.1:8080` |
| 资源限制 | Agent 不受沙盒资源限制 | Agent 与任务共享沙盒资源 |
| 状态共享 | 通过 File / Shell / Browser API 共享 | 直接共享容器文件系统和进程环境 |

## Agent Call Sandbox

这种模式下，Agent 运行在沙盒外部，通过 REST API、Python SDK、TypeScript SDK 或 MCP 调用沙盒能力。

```text
┌──────────────────┐         ┌──────────────────┐
│ Agent (external) │  HTTP   │ AIO Sandbox      │
│ - LLM / planner  │ ──────> │ - Shell          │
│ - orchestration  │ <────── │ - File           │
│ - credentials    │ :8080   │ - Browser        │
└──────────────────┘         └──────────────────┘
```

适合以下场景：

- Agent 已经运行在服务、Worker、Notebook 或本地进程中。
- 需要在外部创建、复用或销毁沙盒环境。
- 希望编排逻辑和凭据留在隔离环境外部。
- 需要一个 Agent 同时管理多个沙盒，用于并行开发、对比测试或批量任务。
- 希望通过 MCP 接入现有 Agent 框架。

典型流程：

1. 使用 Docker 启动 AIO Sandbox。
2. 将客户端配置为 `base_url="http://localhost:8080"`。
3. 调用 `/v1/shell/exec`、`/v1/file/read`、`/v1/browser/*`、`/v1/code/execute` 或 `/mcp` 等接口。

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

### MCP 接入

AIO Sandbox 暴露 `/mcp` 端点。MCP-compatible Agent 客户端可以通过这个端点发现和调用沙盒工具。

```json
{
  "mcpServers": {
    "aio-sandbox": {
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

MCP 适合把沙盒作为一个标准工具提供给 Agent：Agent 负责推理和任务拆分，AIO Sandbox 负责 Shell、文件、浏览器、代码执行等隔离能力。

### 多沙箱编排

Call Sandbox 的一个优势是编排层可以同时连接多个沙盒。每个沙盒使用独立容器和端口，适合做并行方案探索、批量回归或多任务隔离。

```bash
docker run --rm -d --name sandbox-react -p 8080:8080 \
  ghcr.io/agent-infra/sandbox:latest

docker run --rm -d --name sandbox-vue -p 8081:8080 \
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

如果需要对比网页效果，可以在每个沙盒内启动应用，再分别调用浏览器或服务预览能力获取截图、日志和产物。

## Agent In Sandbox

这种模式下，Agent 进程运行在沙盒容器内部，可以直接调用本地命令和本地 REST 端点。

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

适合以下场景：

- Agent、工具、源码和产物需要共享同一个文件系统。
- 正在构建 Coding Agent 或类似 CI 的隔离执行流程。
- 希望在终端中直接使用内置的 `aio` CLI。
- Agent 自身也需要被容器隔离，避免影响宿主机环境。

### 启动方式

**方式一：Docker 启动时运行 Agent 脚本。**
适合把 Agent 脚本随容器一次性拉起的场景。下面示例把本地 `agent.py` 挂载到容器内，然后在沙盒服务启动后执行它。

```bash
docker run --rm -it -p 8080:8080 \
  -v "$PWD/agent.py:/home/gem/agent.py" \
  ghcr.io/agent-infra/sandbox:latest \
  bash -lc "/entrypoint.sh & sleep 5 && python /home/gem/agent.py"
```

**方式二：通过 Shell API 启动 Agent。**
适合先启动一个标准沙盒，再由外部控制面把 Agent 安装并启动在沙盒内。

```bash
curl -X POST http://localhost:8080/v1/shell/exec \
  -H "Content-Type: application/json" \
  -d '{"command": "pip install my-agent && my-agent start"}'
```

**方式三：在容器内直接启动（推荐）。**
适合在容器内、Web Terminal 或已经进入沙盒 Shell 的自动化脚本中启动 Agent。Agent 进程直接运行在沙盒内，可以访问同一个文件系统和 `127.0.0.1:8080`。

```bash
python -m pip install my-agent
my-agent start
```

### 本地命令 + localhost API

Agent 在沙盒内可以优先使用本地命令处理文件和进程，再通过 localhost API 使用浏览器、代码执行、文件监听等服务能力。

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

### AIO CLI（容器内工具调用）

容器内 Agent 不一定需要为所有能力引入 SDK。对于浏览器、GUI、MCP 和 Skills 等工具调用，可以直接使用 `aio` CLI；对于 Shell 与文件读写，优先使用本地命令或 localhost REST API。

```bash
# 浏览器操作
aio browser navigate http://127.0.0.1:3000
aio browser screenshot -o /tmp/page.png

# MCP 与 Skills
aio mcp list
aio skills list

# 沙盒信息
aio sandbox info
```

更多 CLI 用法见 [AIO CLI](/guide/basic/aio-cli.md)。如果需要把 Agent 能力沉淀成可复用操作，可以结合 [Skills](/guide/basic/skills.md) 编写面向任务的命令说明。

## 如何选择

```text
你的 Agent 需要...

├── 访问外部服务、数据库或控制面
│   └── Agent Call Sandbox
│
├── 同时操作多个沙盒
│   └── Agent Call Sandbox
│
├── 通过 MCP 接入现有 Agent 客户端
│   └── Agent Call Sandbox + MCP
│
├── Agent 自身也需要隔离
│   └── Agent In Sandbox
│
├── 在容器内直接编码、构建、测试
│   └── Agent In Sandbox
│
└── 外部服务负责调度，沙盒内子 Agent 执行任务
    └── Hybrid
```

两种模式可以组合使用：外部 Agent 负责创建、调度和回收沙盒，任务真正开始后再通过 Shell API 或容器内命令在沙盒内部启动子 Agent。这样既保留外部编排能力，也让具体执行过程落在隔离环境里。
