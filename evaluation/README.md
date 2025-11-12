# AIO Sandbox Tool Evaluation

English | [简体中文](./README_zh.md)

> A comprehensive evaluation framework for MCP (Model Context Protocol) tools and AI agent capabilities based on aio-sandbox.

Inspired by [Anthropic's "Writing Tools for Agents"](https://www.anthropic.com/engineering/writing-tools-for-agents)

## Prerequisites

- Python >= 3.12
- [uv](https://github.com/astral-sh/uv) package manager

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd evaluation
   ```

2. **Install dependencies**:
   ```bash
   # only openai
   uv sync 
   # include langchain-opanai agent runtime
   uv sync --extra langchain-openai 
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your credentials:
   ```env
   # OpenAI Configuration
   OPENAI_BASE_URL=https://api.openai.com/v1
   OPENAI_API_KEY=your-api-key
   OPENAI_MODEL_ID=gpt-4

   # AIO Sandbox MCP Server Configuration
   MCP_SERVER_URL=http://localhost:8080/mcp
   ```

## Usage

### Running Evaluations

```bash
# Run all evaluations
uv run aio-eval

# Run specific evaluation
uv run aio-eval --eval basic
uv run aio-eval --eval browser --model gpt-4o

# Use different agent runtime
uv run aio-eval --agent langchain --eval basic

# List available evaluations
uv run aio-eval --list

# Get help
uv run aio-eval --help
```

You can also run the main script directly:
```bash
uv run main.py --eval basic
python main.py --eval basic
```

See [CLI_USAGE.md](./CLI_USAGE.md) for detailed CLI documentation.

### Available Categories

| Category | Description |
|----------|-------------|
| `ping` | Basic connectivity test |
| `basic` | Single tool capabilities (file ops, code execution, shell) |
| `browser` | Browser automation basics (navigation, DOM, forms) |
| `browser_advanced` | Advanced browser interactions (click, hover, keyboard) |
| `code_advanced` | Advanced code execution (async, error handling, data structures) |
| `collaboration` | Multi-tool workflows (file+code, browser+file) |
| `editor` | Text editor operations (view, create, replace, insert, undo) |
| `packages` | Package management (Python, Node.js) |
| `util` | Utilities (Markdown conversion) |
| `error` | Error handling tests |
| `workflow` | Real-world scenarios (code review, data pipeline, web scraping) |
| `nextjs` | Next.js project startup |

## Project Structure

```
evaluation/
├── main.py                 # ✨ CLI entry point
├── pyproject.toml
├── aio_sandbox_eval/       # Evaluation framework
│   ├── cli/
│   │   └── utils.py        # CLI helper functions
│   ├── core/               # Core logic
│   └── services/           # Service layer
└── agent_runtime/          # Custom agent implementations (auto-discovered)
├── dataset/                # Evaluation datasets
│   ├── evaluation_basic.xml
│   ├── evaluation_browser.xml
│   ├── evaluation_collaboration.xml
│   └── ...
└── result/                 # Evaluation reports (auto-generated)
    └── YYYYMMDD/           # Date-based output directory
        └── {agent}-{model}-{temp}/
            └── evaluation_*.md
```

## Extending the Framework

### Add New Evaluation Category

1. Create XML file in `dataset/`:
   ```
   dataset/evaluation_mycategory.xml
   ```

2. Run:
   ```bash
   uv run aio-eval --eval mycategory
   ```

### Create Custom Agent Implementation

The framework supports custom agent implementations via a registry pattern. You can extend the evaluation framework with your own agent without modifying core code.

**Quick Start:**

```python
from aio_sandbox_eval.agent_runtime import BaseAgentLoop, AgentRegistry, AgentMessage

@AgentRegistry.register("my_custom_agent")
class MyCustomAgent(BaseAgentLoop):
    def __init__(self, mcp_session, model_name="gpt-4", **kwargs):
        super().__init__()
        self.mcp_session = mcp_session
        self.model_name = model_name
        # Your custom initialization

    async def run(self, prompt: str, tools: List[Dict[str, Any]]) -> List[AgentMessage]:
        # Your agent logic
        pass

    async def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        # Execute tools via MCP
        result = await self.mcp_session.call_tool(tool_name, arguments=arguments)
        return result.model_dump() if hasattr(result, "model_dump") else result
```

**Use Your Custom Agent:**

```bash
# Via CLI with --agent parameter
uv run aio-eval --agent my_custom_agent --eval basic

# Or use environment variable
export AGENT_TYPE=my_custom_agent
uv run aio-eval --eval basic
```


## License

See [LICENSE](../LICENSE) in the repository root.

## References

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Anthropic: Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [OpenAI API Documentation](https://platform.openai.com/docs/)