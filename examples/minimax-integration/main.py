"""MiniMax integration with agent-sandbox for code execution.

Uses MiniMax's OpenAI-compatible API (https://api.minimax.io/v1) to drive
function-calling workflows that execute code inside the sandbox.
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from agent_sandbox import Sandbox

load_dotenv()

# ── MiniMax client (OpenAI-compatible) ──────────────────────────────────
client = OpenAI(
    api_key=os.getenv("MINIMAX_API_KEY"),
    base_url="https://api.minimax.io/v1",
)

MODEL = os.getenv("MINIMAX_MODEL", "MiniMax-M2.7")

# ── Sandbox ─────────────────────────────────────────────────────────────
sandbox_url = os.getenv("SANDBOX_BASE_URL", "http://localhost:8080")
sandbox = Sandbox(base_url=sandbox_url)


def run_code(code: str, lang: str = "python"):
    """Execute code in the sandbox and return the result."""
    if lang == "python":
        return sandbox.jupyter.execute_code(code=code).data
    return sandbox.nodejs.execute_code(code=code).data


# ── Tool definition ─────────────────────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_code",
            "description": "Execute code in a sandboxed environment",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The code to execute",
                    },
                    "lang": {
                        "type": "string",
                        "enum": ["python", "javascript"],
                        "description": "Programming language (default: python)",
                    },
                },
                "required": ["code"],
            },
        },
    }
]


def main():
    task = os.getenv("TASK", "Calculate the first 10 Fibonacci numbers")
    print(f"Task: {task}")
    print(f"Model: {MODEL}")

    # MiniMax requires temperature > 0
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": task}],
        tools=TOOLS,
        temperature=0.01,
    )

    message = response.choices[0].message

    if message.tool_calls:
        tool_call = message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        print(f"\nGenerated code ({args.get('lang', 'python')}):")
        print(args["code"])
        print("\nExecution result:")
        result = run_code(**args)
        print(result.outputs[0].text if result.outputs else "(no output)")
    else:
        print(f"\nResponse: {message.content}")


if __name__ == "__main__":
    main()
