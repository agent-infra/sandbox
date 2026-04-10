# AG2 Integration Example

This example demonstrates how to run an AG2 multi-agent workflow against Agent Sandbox.

## Prerequisites

- A running sandbox instance at `http://localhost:8080`
- Python 3.12+
- OpenAI API key

## Quick Start

```bash
# Start sandbox
docker run --security-opt seccomp=unconfined --rm -it -p 8080:8080 ghcr.io/agent-infra/sandbox:latest

# Configure env
cp .env.example .env

# Install dependencies and run
uv sync
uv run main.py
```

## What This Example Does

1. Creates persistent Jupyter and shell sessions in the sandbox
2. Registers sandbox-backed AG2 tools for Python, shell, and file operations
3. Runs a Coder + Reviewer group chat against the Iris dataset
4. Verifies generated artifacts in `/home/gem`
5. Cleans up sandbox sessions before exit

## Optional Smoke Test

`smoke_test.ipynb` is a step-by-step notebook for validating the SDK calls used by `main.py` before running the full multi-agent flow.
