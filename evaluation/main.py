"""
CLI entry point for aio-sandbox evaluation framework.

This module provides the command-line interface for running tool evaluations.
Can be invoked via:
- uv run aio-eval [args]
- uv run main.py [args]
- python main.py [args]
"""

import argparse
import asyncio
import os
import sys
import traceback
from pathlib import Path

from aio_sandbox_eval import EvaluationRunner, AgentRegistry
from aio_sandbox_eval.cli.utils import (
    get_all_evaluation_files,
    resolve_eval_file,
    list_available_evaluations,
    build_agent_config,
    create_report_output_path,
    get_report_filename,
    print_config_summary,
    print_evaluation_progress,
    print_evaluation_summary,
)

# Auto-discover agent implementations from agent_runtime directory
AgentRegistry.auto_discover("agent_runtime")


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure argument parser for CLI.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="aio-eval",
        description="Run aio-sandbox tool evaluations with specified evaluation file(s)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all evaluation files
  %(prog)s

  # Run specific evaluation
  %(prog)s --eval basic
  %(prog)s --eval browser

  # Use different agent runtime
  %(prog)s --eval basic --agent langchain

  # Custom model and parameters
  %(prog)s --eval basic --model gpt-4o --temperature 0.3 --max-iterations 100

Environment Variables:
  AGENT_TYPE            Agent runtime type (default: openai)
  AGENT_TEMPERATURE     Temperature (default: 0.0)
  AGENT_MAX_ITERATIONS  Max iterations (default: 50)
  MCP_SERVER_URL        MCP server URL (required)
        """,
    )

    parser.add_argument(
        "--eval",
        type=str,
        default=None,
        metavar="NAME",
        help="Evaluation file name (e.g., 'basic', 'browser'). If not specified, runs all evaluation files serially.",
    )

    parser.add_argument(
        "--agent",
        type=str,
        default=None,
        metavar="TYPE",
        help="Agent runtime type: 'openai' (default), 'langchain', etc. Can also be set via AGENT_TYPE env var.",
    )

    parser.add_argument(
        "--model",
        type=str,
        default=None,
        metavar="NAME",
        help="Model name to use (e.g., 'gpt-4', 'gpt-4o', 'claude-3-5-sonnet-20241022'). Can also be set via OPENAI_MODEL_ID env var.",
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        metavar="TEMP",
        help="Temperature for model inference (default: 0.0). Can also be set via AGENT_TEMPERATURE env var.",
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        metavar="N",
        help="Maximum iterations for agent loop (default: 50). Can also be set via AGENT_MAX_ITERATIONS env var.",
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available evaluation files and exit.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    return parser


async def run_evaluation(args: argparse.Namespace) -> int:
    """
    Run evaluation based on CLI arguments.

    Args:
        args: Parsed CLI arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if args.eval is None:
        eval_files = get_all_evaluation_files()
        if not eval_files:
            print("❌ Error: No evaluation files found in dataset directory")
            return 1
    else:
        eval_file = resolve_eval_file(args.eval)
        if not eval_file.exists():
            print(f"❌ Error: Evaluation file not found: {eval_file}")
            print("\nAvailable evaluation files:")
            for short_name, filename in list_available_evaluations():
                print(f"  - {short_name} (→ {filename})")
            return 1
        eval_files = [eval_file]

    agent_type, agent_config = build_agent_config(
        model=args.model,
        temperature=args.temperature,
        max_iterations=args.max_iterations,
        agent_type=args.agent,
    )

    model_name = agent_config.get("model_name", "gpt-4")
    temperature = agent_config.get("temperature", 0.0)

    mcp_url = os.getenv("MCP_SERVER_URL")
    if not mcp_url:
        print("❌ Error: MCP_SERVER_URL environment variable is not set")
        print("Please set MCP_SERVER_URL to your MCP server endpoint")
        return 1

    output_dir = create_report_output_path(
        agent_type=agent_type,
        model_name=model_name,
        temperature=temperature,
    )

    print_config_summary(
        agent_type=agent_type,
        agent_config=agent_config,
        mcp_url=mcp_url,
        eval_files=eval_files,
        output_dir=output_dir,
    )

    successful = 0
    failed = 0

    for idx, eval_file in enumerate(eval_files, 1):
        print_evaluation_progress(idx, len(eval_files), eval_file)

        try:
            runner = EvaluationRunner(
                mcp_server_url=mcp_url,
                agent_type=agent_type,
                agent_config=agent_config,
            )
            report = await runner.run(eval_path=str(eval_file))

            output_filename = get_report_filename(eval_file)
            output_path = output_dir / output_filename

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)

            print(f"✅ Evaluation report saved to: {output_path}")
            successful += 1

        except Exception as e:
            print(f"❌ Failed to process {eval_file.name}: {e}")
            traceback.print_exc()
            failed += 1

    print_evaluation_summary(successful, failed, len(eval_files))

    return 0 if failed == 0 else 1


def main() -> int:
    """
    Main CLI entry point.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = create_parser()
    args = parser.parse_args()

    if args.list:
        print("Available evaluation files:")
        for short_name, filename in list_available_evaluations():
            print(f"  - {short_name} (→ {filename})")
        return 0

    try:
        exit_code = asyncio.run(run_evaluation(args))
        return exit_code
    except KeyboardInterrupt:
        print("\n\n⚠️  Evaluation interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
