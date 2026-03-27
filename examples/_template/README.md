# Your Example Name

Brief description of what this example demonstrates.

## Quick Start

1. Start the sandbox

```bash
# 可选：配置 API Key 鉴权（保护所有服务：API、JupyterLab、VNC）
# - 支持三种方式：X-AIO-API-Key header、Authorization: Bearer header、?api_key= query parameter
# - 未配置 SANDBOX_API_KEY 时服务保持向后兼容（无需鉴权即可访问）
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
