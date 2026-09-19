# RL Training Example (GRPO)

This example demonstrates using AIO Sandbox as the **reward environment** for
reinforcement learning. It fine-tunes a small code model with GRPO (Group
Relative Policy Optimization) from [TRL](https://github.com/huggingface/trl),
where the reward comes from actually executing the model's generated code
against hidden tests inside the sandbox.

Each rollout is graded in its own **process-level sandbox**: the tests run under
`nono run --allow-cwd`, so a generated solution is confined to its working
directory and cannot reach the rest of the sandbox filesystem or the host.

## Prerequisites

- Python 3.11+
- Docker, to run the sandbox
- ~4GB of disk for the model weights (downloaded on first run)

## Sandbox Image

This example needs the [`nono`](https://github.com/always-further/nono) CLI
inside the sandbox, which the stock image does not ship. Build the image in this
directory first:

```bash
docker build -t aio-sandbox-nono .
```

Then start it:

```bash
docker run --security-opt seccomp=unconfined --rm -it -p 8080:8080 aio-sandbox-nono
```

## Running the Example

```bash
uv run train_grpo.py
```

## What This Example Does

1. Builds a small dataset of Python function stubs (`add`, `is_even`), each
   paired with hidden test code.
2. Runs GRPO training on `Qwen/Qwen2.5-Coder-1.5B-Instruct`, generating multiple
   candidate completions per prompt.
3. For every candidate, writes `solution.py` and `test_solution.py` into the
   sandbox at `/tmp/grpo_demo` and executes the tests under `nono`.
4. Converts the run's outcome into a scalar reward:

   | Reward | Condition                                    |
   | -----: | -------------------------------------------- |
   |  `+1.0` | `ALL_TESTS_PASSED` — every assertion held    |
   |  `-0.5` | `AssertionError` or runtime traceback        |
   |  `-1.0` | `SyntaxError`, execution failure, or timeout |

5. Reports timing for two full training passes via `benchmark()`.

## Why Sandbox the Rollouts

An RL loop executes untrusted model output thousands of times. Running that
directly on the training host means arbitrary generated code touches your
filesystem. Here the sandbox provides container-level isolation, and `nono`
adds a per-rollout boundary inside it, so one bad generation cannot corrupt
the environment that grades the next one.

## Customize

- Expand `dataset` with more tasks — two prompts is far too few for a real run,
  and easy tasks produce near-identical rewards, which collapses the GRPO
  advantage signal to zero.
- Raise `max_completion_length` in `training_args`. The default of `16` is small
  enough that a model opening with a docstring gets truncated mid-string, which
  scores as a syntax error rather than a genuine reasoning failure.
- Swap `model_name` in `main()` for a different base model.
- Adjust the reward shaping in `evaluate_in_aio()` for partial credit.
