import asyncio
import os
import sys

from agent_sandbox import Sandbox
from deepagents import create_deep_agent
from langchain.chat_models.base import init_chat_model

from sandbox_backend import AIOSandboxBackend

# Ensure localhost bypasses proxy
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

SYSTEM_PROMPT = """You are a coding assistant with sandbox access.
Your working directory is /home/gem. Write files there.
Write and execute code to answer questions."""


async def main():
    sandbox_url = os.getenv("SANDBOX_URL", "http://localhost:8080")
    client = Sandbox(base_url=sandbox_url)
    backend = AIOSandboxBackend(client)

    model = init_chat_model(
        model=f"openai:{os.getenv('OPENAI_MODEL_ID')}",
        base_url=os.getenv("OPENAI_BASEURL"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    agent = create_deep_agent(
        system_prompt=SYSTEM_PROMPT,
        model=model,
        backend=backend,
    )

    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Write a Python script that calculates the first 20 Fibonacci numbers, then run it."

    try:
        async for chunk in agent.astream(
            {"messages": [{"role": "user", "content": prompt}]},
            stream_mode="values"
        ):
            if "messages" in chunk:
                chunk["messages"][-1].pretty_print()
    finally:
        backend.close()


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(main())
