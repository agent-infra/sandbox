# MiniMax Integration Example

This example demonstrates how to use [MiniMax](https://www.minimaxi.com/) models with agent-sandbox for safe code execution, leveraging MiniMax's OpenAI-compatible API.

## Prerequisites

- A running sandbox instance at `http://localhost:8080`
- Python 3.11+
- MiniMax API key ([get one here](https://platform.minimaxi.com/))

## Running the Example

```bash
# Set your MiniMax API key
export MINIMAX_API_KEY="your_api_key"

# Run the example
uv run main.py
```

You can customise the model and the task via environment variables:

```bash
MINIMAX_MODEL=MiniMax-M2.7-highspeed TASK="sort a list of 100 random numbers" uv run main.py
```

## What This Example Does

1. Connects to MiniMax via the OpenAI-compatible endpoint (`https://api.minimax.io/v1`)
2. Sends a natural-language task to a MiniMax model (default: **MiniMax-M2.7**, 204K context)
3. The model generates code and calls the `run_code` tool
4. The code is executed inside the sandbox and results are returned

## Available MiniMax Models

| Model | Context | Notes |
|---|---|---|
| `MiniMax-M2.7` | 204K | Latest, recommended |
| `MiniMax-M2.7-highspeed` | 204K | Faster, lower latency |
| `MiniMax-M2.5` | 204K | Previous generation |
| `MiniMax-M2.5-highspeed` | 204K | Previous generation, faster |

## Key Features

- **OpenAI-compatible** — uses the standard `openai` Python SDK, just with a different `base_url`
- **Safe Code Execution** — all code runs in an isolated sandbox environment
- **Multi-language Support** — supports both Python (Jupyter) and Node.js execution
- **Function Calling** — leverages MiniMax's tool-use capabilities
