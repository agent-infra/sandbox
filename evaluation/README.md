# AIO Sandbox Tool Evaluation

English | [简体中文](./README_zh.md)

> A comprehensive evaluation framework for MCP (Model Context Protocol) tools and AI agent capabilities based on aio-sandbox.

Inspired by [Anthropic's "Writing Tools for Agents"](https://www.anthropic.com/engineering/writing-tools-for-agents)

## Prerequisites

- Python >= 3.13
- [uv](https://github.com/astral-sh/uv) package manager

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd evaluation
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your credentials:
   ```env
   # Azure OpenAI Configuration
   OPENAI_BASE_URL=https://your-endpoint.openai.azure.com
   OPENAI_API_KEY=your-api-key
   AZURE_OPENAI_DEPLOYMENT=gpt-4
   AZURE_OPENAI_API_VERSION=2024-02-15-preview

   # MCP Server Configuration
   MCP_SERVER_URL=http://localhost:8080/mcp

   # Optional: Concurrency
   MAX_CONCURRENT_TASKS=5
   ```

## Usage

### Run All Evaluations

```bash
uv run main.py
```

### Run Specific Evaluation

```bash
uv run main.py --eval basic
uv run main.py --eval browser
uv run main.py --eval collaboration
uv run main.py --eval workflow
```

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
├── main.py                 # Main entry point and orchestration
├── agent_loop.py           # Agent loop implementation (Azure OpenAI, etc.)
├── dataset_parser.py       # XML dataset parser
├── .env.example            # Environment configuration template
├── pyproject.toml          # Project dependencies
├── dataset/                # Evaluation datasets
│   ├── evaluation_basic.xml
│   ├── evaluation_browser.xml
│   ├── evaluation_collaboration.xml
│   └── ...
└── result/                 # Evaluation reports (auto-generated)
    └── YYYYMMDD/           # Date-based output directory
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
   uv run main.py --eval mycategory
   ```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a Pull Request

## License

See [LICENSE](../LICENSE) in the repository root.

## References

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Anthropic: Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Azure OpenAI Documentation](https://learn.microsoft.com/azure/ai-services/openai/)