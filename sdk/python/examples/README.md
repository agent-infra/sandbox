# Agent Sandbox Examples

This directory contains examples demonstrating various use cases and integrations with agent-sandbox.

## Table of Contents

- [basic-file-operations](#basic-file-operations) - Core file operations (upload, read, list, download)
- [volcengine-provider](#volcengine-provider) - Volcengine cloud provider integration
- [site-to-markdown](#site-to-markdown) - Website to markdown conversion with browser automation
- [browser-use-integration](#browser-use-integration) - AI-driven browser automation
- [openai-integration](#openai-integration) - OpenAI function calling with code execution
- [langgraph-deepagents](#langgraph-deepagents) - LangGraph deep agent with MCP tools integration

## Available Examples

### [basic-file-operations](basic-file-operations/)
Demonstrates core file operations including uploading, reading, listing, and downloading files from the sandbox.

**Key Features:**
- File upload to sandbox
- File listing
- File reading
- File download

**Run:**
```bash
cd basic-file-operation
uv venv
uv pip install -e .
uv run main.py
```

---

### [volcengine-provider](volcengine-provider/)
Shows how to use the Volcengine cloud provider to create and manage sandbox instances using VEFAAS API.

**Key Features:**
- Application creation
- Sandbox lifecycle management
- Cloud deployment

**Run:**
```bash
cd volcengine-provider
cp .env.example .env # Edit .env with your API details
uv venv
uv pip install -e .
uv run main.py
```

---

### [site-to-markdown](site-to-markdown/)
Combines browser automation, Jupyter code execution, and file operations to convert websites to markdown.

**Key Features:**
- Browser automation with Playwright
- HTML to markdown conversion
- Screenshot capture
- Multi-feature integration

**Run:**
```bash
cd site-to-markdown
uv run playwright install
uv venv
uv pip install -e .
uv run main.py
```

---

### [browser-use-integration](browser-use-integration/)
Integrates the browser-use library with agent-sandbox for AI-driven browser automation.

**Key Features:**
- Integration with browser-use
- AI agent browser control
- CDP connection

**Run:**
```bash
cd browser-use-integration
cp .env.example .env # Edit .env with your API details
uv venv
uv pip install -e .
uv run main.py
```

---

### [openai-integration](openai-integration/)
Demonstrates OpenAI function calling with sandbox code execution.

**Key Features:**
- OpenAI function calling
- Safe code execution
- Python and Node.js support

**Run:**
```bash
cd openai-integration
cp .env.example .env # Edit .env with your API details
uv venv
uv pip install -e .
uv run main.py
```

---

### [langgraph-deepagents](langgraph-deepagents/)
A LangGraph-based deep agent implementation using the AIO sandbox with MCP integration for enhanced research capabilities.

**Key Features:**
- Deep research agent with advanced reasoning
- MCP (Model Context Protocol) integration
- OpenAI-compatible API support
- Streaming support for real-time responses

**Run:**
```bash
cd langgraph-deepagents
cp .env.example .env # Edit .env with your API details
uv venv
uv pip install -e .
uv run main.py
```

## Prerequisites

All examples require:
- Python 3.12+
- A running sandbox instance (most examples use `http://localhost:8080`)
- uv package manager

## Contributing

When adding new examples, please follow the established pattern:
1. Create a new directory with a descriptive name
2. Initialize as a uv project with `uv init`
3. Add `agent-sandbox` workspace dependency
4. Include comprehensive README.md
5. Update this main README.md
