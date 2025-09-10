from openai import OpenAI
from agent_sandbox import Sandbox
import json

client = OpenAI(
    api_key="your_api_key",
)
sandbox = Sandbox(base_url="http://localhost:8080")


# define a tool to run code in the sandbox
def run_code(code, lang="python"):
    if lang == "python":
        return sandbox.jupyter.execute_jupyter_code(code=code).data
    return sandbox.nodejs.execute_nodejs_code(code=code).data


# 使用 OpenAI
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "calculate 1+1"}],
    tools=[
        {
            "type": "function",
            "function": {
                "name": "run_code",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "lang": {"type": "string"},
                    },
                },
            },
        }
    ],
)


if response.choices[0].message.tool_calls:
    args = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
    print("args", args)
    result = run_code(**args)
    print(result['outputs'][0]['text'])
