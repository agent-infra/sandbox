# Agent Sandbox Examples

This directory contains examples demonstrating various use cases and integrations with agent-sandbox.

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
cd basic-file-operations
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
export VOLCENGINE_ACCESS_KEY="your_key"
export VOLCENGINE_SECRET_KEY="your_secret"
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
export OPENAI_API_KEY="your_key"
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
# Update API key in main.py
uv run main.py
```

## Prerequisites

All examples require:
- Python 3.11+
- A running sandbox instance (most examples use `http://localhost:8080`)
- uv package manager

## Quick Setup

**📖 For detailed setup instructions, see [SETUP.md](SETUP.md)**

### Basic Steps

1. **Check all examples are properly configured:**
```bash
./check_examples.sh
```

2. **Configure environment variables (if needed):**
```bash
cd <example-name>
cp .env.example .env
# Edit .env with your actual credentials
```

3. **Run the example:**
```bash
uv run main.py
```

## Project Structure

Each example is an independent uv project with:
- `pyproject.toml` - Project configuration and dependencies
- `main.py` - Example code
- `README.md` - Specific documentation
- `.env.example` - Environment variable template (if needed)

## Environment Variables

Examples that require environment variables:
- **volcengine-provider**: Requires `VOLCENGINE_ACCESS_KEY`, `VOLCENGINE_SECRET_KEY`
- **browser-use-integration**: Requires `OPENAI_API_KEY`
- **openai-integration**: Requires `OPENAI_API_KEY`
- **All examples**: Optional `SANDBOX_BASE_URL` (default: http://localhost:8080)

See [SETUP.md](SETUP.md) for complete configuration details.

## Contributing

When adding new examples, please follow the established pattern:
1. Create a new directory with a descriptive name
2. Initialize as a uv project with `uv init`
3. Add `agent-sandbox` workspace dependency
4. Include comprehensive README.md
5. Update this main README.md
