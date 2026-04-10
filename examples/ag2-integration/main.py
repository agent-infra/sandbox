"""AG2 Multi-Agent Code Execution with AIO Sandbox

A multi-agent system where a Coder agent writes and executes Python code inside
a sandboxed environment, and a Reviewer agent validates results. All code runs
safely inside the sandbox container — no local execution.
"""

import os
import uuid

from agent_sandbox import Sandbox
from autogen import (
    AssistantAgent,
    GroupChat,
    GroupChatManager,
    LLMConfig,
    UserProxyAgent,
)
from dotenv import load_dotenv


def _get_sandbox_url() -> str:
    return (
        os.getenv("SANDBOX_BASE_URL")
        or os.getenv("SANDBOX_URL")
        or "http://localhost:8080"
    )


def _require_openai_api_key() -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key
    raise RuntimeError(
        "OPENAI_API_KEY is required. Copy .env.example to .env and set it "
        "before running this example."
    )


def _extract_file_content(result: object) -> str:
    if isinstance(result, str):
        return result

    data = getattr(result, "data", None)
    if data is None:
        return str(result)

    content = getattr(data, "content", None)
    if content is not None:
        return str(content)

    return str(data)


def main() -> None:
    load_dotenv()

    # ---------------------------------------------------------------------------
    # 1. Sandbox setup — connect and create persistent sessions
    # ---------------------------------------------------------------------------
    sandbox_url = _get_sandbox_url()
    openai_api_key = _require_openai_api_key()
    openai_model_id = os.getenv("OPENAI_MODEL_ID", "gpt-4o-mini")

    sandbox = Sandbox(base_url=sandbox_url)

    jupyter_session = sandbox.jupyter.create_session(kernel_name="python3")
    shell_session = sandbox.shell.create_session(id=str(uuid.uuid4()))  # id is required

    jupyter_session_id = jupyter_session.data.session_id
    shell_session_id = shell_session.data.session_id

    print(f"✓ Sandbox connected: {sandbox_url}")
    print(f"✓ Jupyter session: {jupyter_session_id}")
    print(f"✓ Shell session:   {shell_session_id}")

    # ---------------------------------------------------------------------------
    # 2. AG2 setup — LLM config and agents
    # ---------------------------------------------------------------------------
    llm_config = LLMConfig(
        {
            "model": openai_model_id,
            "api_key": openai_api_key,
            "api_type": "openai",
        }
    )

    def is_termination(msg: dict) -> bool:
        """Signal the conversation to stop when Reviewer says TERMINATE."""
        content = msg.get("content", "") or ""
        return "TERMINATE" in content

    proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        code_execution_config=False,
        is_termination_msg=is_termination,
    )

    coder = AssistantAgent(
        name="coder",
        system_message=(
            "You are a Python developer. Write code to solve tasks.\n"
            "Use run_python to execute code in the sandboxed Jupyter environment.\n"
            "Use run_shell for system/shell commands.\n"
            "Use read_file / write_file for filesystem operations.\n"
            "Always verify results by reading output or checking files.\n"
            "The sandbox filesystem is at /home/gem — save any output files there."
        ),
        llm_config=llm_config,
    )

    reviewer = AssistantAgent(
        name="reviewer",
        system_message=(
            "You review code execution results and verify correctness.\n"
            "Check whether the task is fully solved and outputs are present.\n"
            "If issues remain, suggest specific fixes to the coder.\n"
            "When the task is complete and all results verified, reply with TERMINATE."
        ),
        llm_config=llm_config,
    )

    # ---------------------------------------------------------------------------
    # 3. Sandbox tool functions
    # ---------------------------------------------------------------------------

    @proxy.register_for_execution()
    @coder.register_for_llm(
        description="Execute Python code in a persistent sandboxed Jupyter environment"
    )
    def run_python(code: str) -> str:
        try:
            result = sandbox.jupyter.execute_code(
                code=code,
                session_id=jupyter_session_id,
            )
            data = getattr(result, "data", None)
            if data is None:
                return "Sandbox error: no data in response"

            # outputs is a list of JupyterOutput; collect stdout text and errors
            outputs = getattr(data, "outputs", []) or []
            stdout_parts = []
            error_parts  = []
            for o in outputs:
                output_type = getattr(o, "output_type", "")
                text = getattr(o, "text", None)
                if output_type in ("stream",) and text:
                    stdout_parts.append(text)
                elif output_type in ("error",):
                    ename    = getattr(o, "ename",    "")
                    evalue   = getattr(o, "evalue",   "")
                    traceback = getattr(o, "traceback", []) or []
                    error_parts.append(f"{ename}: {evalue}\n" + "\n".join(traceback))

            output = "".join(stdout_parts)
            error  = "\n".join(error_parts)

            # Also check .status for kernel-level errors
            status = getattr(data, "status", "ok")
            if status != "ok" and not error:
                error = f"Kernel status: {status}"

            if error:
                return f"ERROR:\n{error}\nOUTPUT:\n{output}"
            return output or "Code executed successfully (no output)"
        except Exception as exc:  # noqa: BLE001
            return f"Sandbox error: {exc}"

    @proxy.register_for_execution()
    @coder.register_for_llm(description="Execute a shell command inside the sandbox")
    def run_shell(command: str) -> str:
        try:
            result = sandbox.shell.exec_command(
                command=command,
                id=shell_session_id,   # verified from Cell 9: param is 'id=', not 'session_id='
            )
            output = getattr(result, "output", None)
            if output is None:
                data = getattr(result, "data", None)
                output = getattr(data, "output", None) if data else None
            return output or "Command completed (no output)"
        except Exception as exc:  # noqa: BLE001
            return f"Shell error: {exc}"

    @proxy.register_for_execution()
    @coder.register_for_llm(description="Read a file from the sandbox filesystem")
    def read_file(path: str) -> str:
        try:
            result = sandbox.file.read_file(file=path)  # verified: param is 'file=', not 'path='
            return _extract_file_content(result)
        except Exception as exc:  # noqa: BLE001
            return f"Read error: {exc}"

    @proxy.register_for_execution()
    @coder.register_for_llm(
        description="Write text content to a file in the sandbox filesystem"
    )
    def write_file(path: str, content: str) -> str:
        try:
            sandbox.file.write_file(file=path, content=content)  # verified: param is 'file=', not 'path='
            return f"File written: {path}"
        except Exception as exc:  # noqa: BLE001
            return f"Write error: {exc}"

    # ---------------------------------------------------------------------------
    # 4. GroupChat
    # ---------------------------------------------------------------------------
    group_chat = GroupChat(
        agents=[proxy, coder, reviewer],
        messages=[],
        max_round=15,
    )

    manager = GroupChatManager(
        groupchat=group_chat,
        llm_config=llm_config,
        is_termination_msg=is_termination,
    )

    # ---------------------------------------------------------------------------
    # 5. Demo task
    # ---------------------------------------------------------------------------
    TASK = (
        "Analyze the Iris dataset:\n"
        "1. Load it using sklearn.datasets.load_iris (no external downloads needed)\n"
        "2. Compute summary statistics (mean, std, min, max) per feature per species\n"
        "3. Save the statistics as a CSV to /home/gem/iris_stats.csv\n"
        "4. Create a scatter plot (sepal length vs sepal width, colored by species)\n"
        "   and save it as /home/gem/iris_chart.png\n"
        "5. Confirm both files exist by listing /home/gem and reading a few lines of the CSV"
    )

    # ---------------------------------------------------------------------------
    # 6. Run the multi-agent conversation
    # ---------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Starting AG2 multi-agent conversation…")
    print("=" * 60 + "\n")

    try:
        proxy.run(manager, message=TASK).process()
        print("\n" + "=" * 60)
        print("Conversation finished.")
        print("=" * 60)
    finally:
        # ---------------------------------------------------------------------------
        # 7. Cleanup
        # ---------------------------------------------------------------------------
        print("\nCleaning up sandbox sessions…")
        try:
            sandbox.jupyter.delete_session(jupyter_session_id)
            print(f"  ✓ Jupyter session {jupyter_session_id} deleted")
        except Exception as exc:  # noqa: BLE001
            print(f"  ✗ Could not delete Jupyter session: {exc}")

        try:
            sandbox.shell.cleanup_session(shell_session_id)
            print(f"  ✓ Shell session {shell_session_id} cleaned up")
        except Exception as exc:  # noqa: BLE001
            print(f"  ✗ Could not clean up shell session: {exc}")

        print("Done.")


if __name__ == "__main__":
    main()
