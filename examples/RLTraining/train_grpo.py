"""
GRPO training demo: reinforcement learning for code generation with sandboxed reward evaluation.

Fine-tunes a small Qwen coder model with TRL's GRPOTrainer on a toy dataset of
Python function stubs. For each generated completion, the reward function writes
the candidate solution plus its hidden test file into an AIO Sandbox
(http://localhost:8080) and executes the tests there. Every rollout is graded in
its own process-level sandbox: the tests run under `nono run --allow-cwd`, so a
candidate solution is confined to its working directory and cannot touch the rest
of the sandbox filesystem or the host. Grading is on a -1.0 to +1.0 scale based on
whether the tests passed, failed, or crashed. Running the module benchmarks two
full training passes.

Requirements: agent_sandbox SDK, trl, datasets, and a reachable AIO Sandbox.
"""

import re
import textwrap
from typing import List


import time
from statistics import mean

from datasets import Dataset
from agent_sandbox import Sandbox

from trl import GRPOConfig, GRPOTrainer


# -----------------------------
# Tiny toy dataset
# -----------------------------
# Each row has:
# - prompt: what the model sees
# - tests: hidden validation code run inside AIO Sandbox
#
# For a real demo, expand this to 50-500 easy coding tasks.

dataset = Dataset.from_list(
    [
        {
            "prompt": "def add(a, b):\n",
            "tests": textwrap.dedent(
                """
                from solution import add
                assert add(1, 2) == 3
                assert add(-5, 2) == -3
                assert add(0, 0) == 0
                print("ALL_TESTS_PASSED")
                """
            ),
        },
        {
            "prompt": "def is_even(n):\n",
            "tests": textwrap.dedent(
                """
                from solution import is_even
                assert is_even(2) is True
                assert is_even(3) is False
                assert is_even(0) is True
                print("ALL_TESTS_PASSED")
                """
            ),
        },
    ]
)


# -----------------------------
# Helpers
# -----------------------------
def strip_code_fences(text: str) -> str:
    """
    Extract Python code from markdown fences if present.
    """
    match = re.search(r"```python\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    match = re.search(r"```(.*?)```", text, flags=re.DOTALL)
    if match:
        return match.group(1).strip()

    return text.strip()


def evaluate_in_aio(completion: str, tests: str) -> float:
    """
    Run a single completion inside a fresh AIO sandbox and return a scalar reward.

    Reward shaping:
      +1.0  all tests passed
      +0.2  code ran but tests did not fully pass
      -0.5  import/runtime/assertion failure
      -1.0  obvious syntax error / execution failure / timeout
    """
    code = strip_code_fences(completion)

    # Tiny guardrails for a demo.
    banned = ["subprocess", "socket", "requests", "os.system", "shutil.rmtree"]
    if any(tok in code for tok in banned):
        return -1.0

    sandbox = None
    try:
        
        sandbox = Sandbox(base_url="http://localhost:8080")

        workdir = "/tmp/grpo_demo"
        result = sandbox.shell.exec_command(command=f"rm -rf {workdir}")
        result = sandbox.shell.exec_command(command=f"mkdir -p {workdir}")
        sandbox.file.write_file(file=f"{workdir}/solution.py", content=code)
        sandbox.file.write_file(file=f"{workdir}/test_solution.py", content=tests)

        # Run tests in the sandbox.
        # We avoid relying on pytest so the example stays simpler.
        # cmd = (
        #     f"cd {workdir} && "
        #     f"python test_solution.py"
        # )
        cmd = (
            f"cd {workdir} && "
            f"HOME=/tmp/nono-home "
            # f"nono run --allow {workdir} "
            f"nono run --allow-cwd "
            f"python test_solution.py"
        )

        result = sandbox.shell.exec_command(command=cmd)
        
        data = getattr(result, "data", None)

        if data is not None:
            combined = getattr(data, "output", "") or ""
            exit_code = getattr(data, "exit_code", None)
        else:
            combined = str(result)
            exit_code = None

        print("EXIT CODE:", exit_code)
        print("COMBINED OUTPUT:", combined)
    
        if "ALL_TESTS_PASSED" in combined:
            return 1.0

        if "SyntaxError" in combined:
            return -1.0

        if "AssertionError" in combined or "Traceback" in combined:
            return -0.5

        return -1.0


    except Exception:
        # In a real setup, log the exception details.
        return -1.0

    # finally:
    #     if sandbox is not None:
    #         try:
    #             sandbox.kill()
    #         except Exception:
    #             pass


def keep_first_function_only(code: str) -> str:
    lines = code.splitlines()
    kept = []

    for line in lines:
        kept.append(line)

        # Stop once the function returns.
        if line.strip().startswith("return "):
            break

    return "\n".join(kept).rstrip() + "\n"

# -----------------------------
# GRPO reward function
# -----------------------------
def reward_func(prompts: List[str], completions: List[str], tests: List[str], **kwargs):
    """
    TRL passes prompts, generated completions, and any extra dataset columns
    (like `tests`) into custom reward functions.
    """
    rewards = []

    for i, (prompt, completion, test_code) in enumerate(zip(prompts, completions, tests)):
        full_code = keep_first_function_only(prompt + completion)

        print(f"\n=== CANDIDATE {i} ===")
        print(full_code)

        reward = evaluate_in_aio(full_code, test_code)

        print("REWARD:", reward)

        rewards.append(reward)

    return rewards


# -----------------------------
# Training config
# -----------------------------
# Notes:
# - Keep this tiny for a demo.
# - Exact GRPOConfig args can vary a bit by TRL version.
training_args = GRPOConfig(
    output_dir="./grpo_aio_demo",
    per_device_train_batch_size=16,
    gradient_accumulation_steps=1,
    learning_rate=1e-6,
    logging_steps=1,
    save_steps=20,
    num_generations=16,
    # max_prompt_length=256,
    max_completion_length=16,
    num_train_epochs=1,
    bf16=False,
    fp16=False,
    report_to=[],
)


def benchmark(fn, n=2):
    times = []

    for _ in range(n):
        start = time.perf_counter()
        fn()
        elapsed = time.perf_counter() - start

        times.append(elapsed)

    return {
        "runs": n,
        "avg_seconds": mean(times),
        "min_seconds": min(times),
        "max_seconds": max(times),
    }

def main():
    # model_name = "Qwen/Qwen2.5-0.5B-Instruct"
    model_name = "Qwen/Qwen2.5-Coder-1.5B-Instruct"

    trainer = GRPOTrainer(
        model=model_name,
        reward_funcs=reward_func,
        args=training_args,
        train_dataset=dataset,
    )

    trainer.train()
    # trainer.save_model("./grpo_aio_demo/final")


if __name__ == "__main__":
    # main()
    print(benchmark(main, n=2))