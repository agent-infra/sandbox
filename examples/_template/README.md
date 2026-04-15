# Your Example Name

Brief description of what this example demonstrates.

## Quick Start

1. Start the sandbox

```bash
# Optional: Enable API Key authentication (protects all services: API, JupyterLab, VNC)
# - Supports three methods: X-AIO-API-Key header, Authorization: Bearer header, ?api_key= query parameter
# - Without SANDBOX_API_KEY, services remain open (backward compatible)
docker run --security-opt seccomp=unconfined --rm -it \
  -e SANDBOX_API_KEY=your-secret-key \
  -p 127.0.0.1:8080:8080 ghcr.io/agent-infra/sandbox:latest
```

2. Configure the environment

```bash
# 1. Copy .env.example to .env
cp .env.example .env

# 2. Run the example
uv run main.py
```

## What This Does

Explain what happens when you run this example.

## Customize

Modify `main.py` to add your own logic.
