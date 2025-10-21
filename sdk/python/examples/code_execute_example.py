import asyncio
from agent_sandbox import Sandbox

sandbox = Sandbox(base_url="http://localhost:8080")

async def main():
    session = sandbox.jupyter.create_session(
        kernel_name="python3",
    )
    sandbox.jupyter.execute_code(
        code="foo=1",
        kernel_name="python3",
        session_id=session.data.session_id
    )
    result = sandbox.jupyter.execute_code(
        code="print(foo)",
        session_id=session.data.session_id,
        kernel_name="python3",
    )
    print("Code execution result:", result.data.outputs[0].text)
    sandbox.shell.exec_command(command="pip3.12 install agent-sandbox")

    result = sandbox.jupyter.execute_code(
        code="""from agent_sandbox import Sandbox
sandbox = Sandbox(base_url="http://localhost:8080")
context = sandbox.sandbox.get_context()
print(context)
""",
        kernel_name="python3.12",
    )
    print("After installed code result:", result.data.outputs[0].text)
if __name__ == "__main__":
    asyncio.run(main())
