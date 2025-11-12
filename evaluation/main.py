"""
Tool Evaluation Framework using Azure OpenAI and MCP Streamable HTTP

Run from tool_evaluation directory:
    uv run main.py                    # Run ALL evaluation files serially
    uv run main.py --eval basic       # Run basic evaluation only
    uv run main.py --eval browser     # Run browser evaluation only
    uv run main.py --eval collaboration # Run collaboration evaluation only
"""

import argparse
import asyncio
from datetime import datetime, timezone, timedelta
import json
import os
import re
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from dotenv import load_dotenv

from agent_loop import AzureOpenAIAgentLoop, BaseAgentLoop
from dataset_parser import XMLDatasetParser

load_dotenv()

# ============================================================================
# Configuration
# ============================================================================

# Azure OpenAI Configuration
AZURE_ENDPOINT = os.getenv(
    "AZURE_OPENAI_ENDPOINT", "https://your-endpoint.openai.azure.com"
)
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "your-api-key")
AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

# MCP Server Configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8080/mcp")

# Concurrency Configuration
MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", "5"))

# Global MCP Session
_mcp_session: ClientSession = None
_mcp_streams = None


# ============================================================================
# Global MCP Session Management
# ============================================================================


async def init_global_mcp_session(server_url: str) -> ClientSession:
    """Initialize global MCP session once."""
    global _mcp_session, _mcp_streams

    if _mcp_session is not None:
        return _mcp_session

    try:
        _mcp_streams = streamablehttp_client(server_url)
        read_stream, write_stream, _ = await _mcp_streams.__aenter__()
        _mcp_session = ClientSession(read_stream, write_stream)
        await _mcp_session.__aenter__()
        await _mcp_session.initialize()
        print(f"✅ Global MCP session initialized: {server_url}")
        return _mcp_session
    except Exception as e:
        print(f"❌ Failed to initialize MCP session: {e}")
        traceback.print_exc()
        return None


async def cleanup_global_mcp_session():
    """Cleanup global MCP session."""
    global _mcp_session, _mcp_streams

    if _mcp_session:
        try:
            await _mcp_session.__aexit__(None, None, None)
        except:
            pass
        _mcp_session = None

    if _mcp_streams:
        try:
            await _mcp_streams.__aexit__(None, None, None)
        except:
            pass
        _mcp_streams = None


# ============================================================================
# MCP Tool Retrieval
# ============================================================================


async def get_mcp_tools() -> List[Dict[str, Any]]:
    """
    Retrieve tools from global MCP session.

    Returns:
        List of tool definitions in Azure OpenAI format
    """
    global _mcp_session

    if not _mcp_session:
        print("⚠️  MCP session not initialized")
        return []

    try:
        tools_response = await _mcp_session.list_tools()
        print(f"🔍 DEBUG: tools_response type = {type(tools_response)}")
        print(
            f"🔍 DEBUG: tools_response.tools length = {len(tools_response.tools) if hasattr(tools_response, 'tools') else 'N/A'}"
        )

        # Convert MCP tools to Azure OpenAI format
        azure_tools = []
        for tool in tools_response.tools:
            azure_tool = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema
                    if hasattr(tool, "inputSchema")
                    else {"type": "object", "properties": {}, "required": []},
                },
            }
            azure_tools.append(azure_tool)
            print(f"  - {tool.name}")

        return azure_tools
    except Exception as e:
        print(f"Error retrieving MCP tools: {e}")
        traceback.print_exc()
        return []


# ============================================================================
# Helper Functions
# ============================================================================


async def evaluate_single_task(
    task: Dict[str, Any],
    agent: BaseAgentLoop,
    tools: List[Dict[str, Any]],
    task_index: int,
) -> Dict[str, Any]:
    """Evaluate a single task with the given agent and tools."""
    start_time = time.time()

    print(f"Task {task_index + 1}: Running task with prompt: {task['prompt']}")

    # Wrap task execution in try-except to ensure single task failure doesn't kill entire evaluation
    try:
        response, tool_metrics = await agent.run(task["prompt"], tools)

        # Extract all tagged content
        def _extract_xml_content(text, tag):
            if not text:
                return None
            pattern = rf"<{tag}>(.*?)</{tag}>"
            matches = re.findall(pattern, text, re.DOTALL)
            return matches[-1].strip() if matches else None

        actual_response = _extract_xml_content(response, "response")
        summary = _extract_xml_content(response, "summary")
        feedback = _extract_xml_content(response, "feedback")

        duration_seconds = time.time() - start_time

        # Use regex matching for evaluation
        # Ground truth is expected to be a regex pattern
        score = 0
        if actual_response:
            try:
                # Use search to check if pattern exists in response (partial match)
                # This allows response_pattern to match substrings
                if re.search(task["response"], actual_response, re.DOTALL):
                    score = 1
            except re.error:
                # If pattern is invalid, fall back to exact string comparison
                score = int(actual_response == task["response"])

        return {
            "prompt": task["prompt"],
            "expected": task["response"],
            "actual": actual_response,
            "score": score,
            "total_duration": duration_seconds,
            "tool_calls": tool_metrics,
            "num_tool_calls": sum(
                len(metrics["durations"]) for metrics in tool_metrics.values()
            ),
            "summary": summary,
            "feedback": feedback,
        }

    except Exception as e:
        # If task execution fails completely, return failed result
        duration_seconds = time.time() - start_time
        error_type = type(e).__name__
        error_msg = str(e)

        print(f"❌ Task {task_index + 1} failed completely: {error_type}: {error_msg}")
        traceback.print_exc()

        return {
            "prompt": task["prompt"],
            "expected": task["response"],
            "actual": f"TASK_EXECUTION_ERROR: {error_type}: {error_msg}",
            "score": 0,
            "total_duration": duration_seconds,
            "tool_calls": {},
            "num_tool_calls": 0,
            "summary": f"Task execution failed with {error_type}",
            "feedback": f"Error during task execution: {error_msg}",
        }


# ============================================================================
# Main Evaluation Function
# ============================================================================

REPORT_HEADER = """
# Evaluation Report

## Summary

- **Accuracy**: {correct}/{total} ({accuracy:.1f}%)
- **Average Task Duration**: {average_duration_s:.2f}s
- **Average Tool Calls per Task**: {average_tool_calls:.2f}
- **Total Tool Calls**: {total_tool_calls}

---
"""

TASK_TEMPLATE = """
### Task {task_number}

- **Prompt**: {prompt}
- **Ground Truth Response**: `{expected_response}`
- **Actual Response**: `{actual_response}`
- **Correct**: {correct_indicator}
- **Duration**: {total_duration:.2f}s
- **Tool Calls Summary**: {tool_calls_count}

{tool_calls_detail}

#### Summary
{summary}

#### Feedback
{feedback}

---
"""

SUMMARY_TABLE_HEADER = """
## 📊 Detailed Summary Table

| # | Prompt | 操作时间 | 是否成功 | 工具调用数量 | 操作步骤 | 失败原因 |
|---|--------|----------|----------|--------------|----------|----------|
"""


def format_summary_table_row(
    task_number: int,
    prompt: str,
    duration: float,
    is_success: bool,
    tool_calls: Dict[str, Any],
    failure_reason: str = "",
) -> str:
    """
    Format a single row for the summary table.

    Args:
        task_number: Task number
        prompt: Task prompt (full content, not truncated)
        duration: Task duration in seconds
        is_success: Whether task succeeded
        tool_calls: Tool call metrics
        failure_reason: Reason for failure if applicable

    Returns:
        Markdown table row
    """
    # Clean prompt: replace newlines and extra spaces for Markdown table
    # Keep full content without truncation
    cleaned_prompt = " ".join(prompt.split())

    # Format duration
    duration_str = f"{duration:.2f}s"

    # Success indicator
    success_str = "✅" if is_success else "❌"

    # Calculate total tool calls count
    tool_call_count = 0
    if tool_calls:
        for metrics in tool_calls.values():
            tool_call_count += len(metrics.get("calls", []))

    # Extract tool execution steps
    tool_steps = []
    if tool_calls:
        all_calls = []
        for tool_name, metrics in tool_calls.items():
            for call in metrics.get("calls", []):
                all_calls.append({
                    "tool_name": tool_name,
                    "timestamp": call.get("timestamp", 0),
                })
        all_calls.sort(key=lambda x: x["timestamp"])
        tool_steps = [f"{i+1}. {call['tool_name']}" for i, call in enumerate(all_calls)]

    steps_str = "<br>".join(tool_steps) if tool_steps else "N/A"

    # Failure reason (only show if failed)
    failure_str = failure_reason if not is_success else "-"

    return f"| {task_number} | {cleaned_prompt} | {duration_str} | {success_str} | {tool_call_count} | {steps_str} | {failure_str} |\n"


def format_tool_calls(tool_metrics: Dict[str, Any]) -> Tuple[str, str]:
    """
    Format tool calls into summary and detailed views.

    Args:
        tool_metrics: Dictionary with tool call metrics

    Returns:
        Tuple of (summary_str, detail_str)
    """
    if not tool_metrics:
        return "No tools called", ""

    # Summary: total count
    total_calls = sum(m["count"] for m in tool_metrics.values())
    summary = f"{total_calls} calls across {len(tool_metrics)} tools"

    # Detail: reconstruct chronological order from all tool calls
    all_calls = []
    for tool_name, metrics in tool_metrics.items():
        for call in metrics.get("calls", []):
            all_calls.append(
                {
                    "tool_name": tool_name,
                    "args": call["args"],
                    "duration": call["duration"],
                    "timestamp": call.get("timestamp", 0),
                }
            )

    # Sort by timestamp to maintain chronological order
    all_calls.sort(key=lambda x: x["timestamp"])

    # Format in chronological order
    detail_lines = ["#### Tool Execution Timeline", ""]
    for i, call in enumerate(all_calls, 1):
        detail_lines.append(f"{i}. **{call['tool_name']}** ({call['duration']:.2f}s)")

        # Format arguments
        if call["args"]:
            for key, value in call["args"].items():
                # Format value for display
                if isinstance(value, str):
                    value_str = f'"{value}"'
                else:
                    value_str = json.dumps(value, ensure_ascii=False)
                detail_lines.append(f"   - {key}: {value_str}")
        else:
            detail_lines.append("   - (no arguments)")

        detail_lines.append("")

    return summary, "\n".join(detail_lines)


async def upload_file_to_sandbox(local_path: Path, sandbox_path: str) -> bool:
    """
    Upload a file to sandbox /tmp directory using MCP file_operations tool.

    Args:
        local_path: Local file path to upload
        sandbox_path: Target path in sandbox (should be under /tmp)

    Returns:
        True if upload successful, False otherwise
    """
    global _mcp_session

    if not _mcp_session:
        print(f"⚠️  MCP session not initialized, skipping upload: {local_path}")
        return False

    try:
        if not local_path.exists():
            print(f"⚠️  Warning: {local_path} not found, skipping upload")
            return False

        with open(local_path, "r", encoding="utf-8") as f:
            file_content = f.read()

        # Upload to sandbox using global MCP session
        await _mcp_session.call_tool(
            "sandbox_file_operations",
            arguments={
                "action": "write",
                "path": sandbox_path,
                "content": file_content,
                "encoding": "utf-8",
            },
        )

        print(f"📤 Uploaded {local_path.name} to sandbox:{sandbox_path}")
        return True

    except Exception as e:
        print(f"⚠️  Failed to upload {local_path}: {e}")
        return False


async def upload_test_files_to_sandbox(eval_file: Path) -> bool:
    """
    Upload test files to sandbox /tmp directory based on evaluation file.

    Args:
        eval_file: Path to the evaluation XML file being run

    Returns:
        True if all required uploads successful, False otherwise
    """
    eval_file_name = eval_file.name
    base_dir = Path(__file__).parent
    success = True

    # Upload main.py for collaboration and workflow tests
    if "collaboration" in eval_file_name or "workflow" in eval_file_name:
        main_py_path = base_dir / "main.py"
        if not await upload_file_to_sandbox(main_py_path, "/tmp/main.py"):
            success = False

    # Upload evaluation.xml for workflow tests
    if "workflow" in eval_file_name:
        # Try to find evaluation.xml in dataset directory
        eval_xml_path = base_dir / "dataset" / "evaluation.xml"
        if eval_xml_path.exists():
            if not await upload_file_to_sandbox(eval_xml_path, "/tmp/evaluation.xml"):
                success = False
        else:
            # If evaluation.xml doesn't exist, use the current eval file
            if not await upload_file_to_sandbox(eval_file, "/tmp/evaluation.xml"):
                success = False

    return success


async def run_evaluation(
    eval_path: str,
    mcp_server_url: str = None,
) -> str:
    """
    Run evaluation with tools from MCP server.

    Args:
        eval_path: Path to XML evaluation file
        mcp_server_url: URL of MCP server (optional)

    Returns:
        Markdown evaluation report
    """
    print("🚀 Starting Evaluation")

    eval_file = Path(eval_path)

    # Initialize global MCP session
    if mcp_server_url:
        await init_global_mcp_session(mcp_server_url)
        # Upload test files to sandbox based on evaluation file
        await upload_test_files_to_sandbox(eval_file)

    # Parse evaluation tasks using parser
    parser = XMLDatasetParser()
    tasks = parser.parse(eval_file)
    print(f"📋 Loaded {len(tasks)} evaluation tasks")

    # Get tools from MCP server
    tools = []
    if mcp_server_url:
        tools = await get_mcp_tools()
        print(f"✅ Retrieved {len(tools)} tools from MCP server")

    # Initialize agent loop
    # TODO: Support selecting agent type via config/CLI args
    agent = AzureOpenAIAgentLoop(mcp_session=_mcp_session)
    print(f"🤖 Using agent: {agent.__class__.__name__}")

    try:
        # Run all tasks serially
        results = []
        for i, task in enumerate(tasks):
            print(f"Processing task {i + 1}/{len(tasks)}")
            result = await evaluate_single_task(task, agent, tools, i)
            results.append(result)

        # Calculate summary statistics
        correct = sum(r["score"] for r in results)
        accuracy = (correct / len(results)) * 100 if results else 0
        average_duration_s = (
            sum(r["total_duration"] for r in results) / len(results) if results else 0
        )
        average_tool_calls = (
            sum(r["num_tool_calls"] for r in results) / len(results) if results else 0
        )
        total_tool_calls = sum(r["num_tool_calls"] for r in results)

        report = REPORT_HEADER.format(
            correct=correct,
            total=len(results),
            accuracy=accuracy,
            average_duration_s=average_duration_s,
            average_tool_calls=average_tool_calls,
            total_tool_calls=total_tool_calls,
        )

        for i, (task, result) in enumerate(zip(tasks, results)):
            tool_calls_count, tool_calls_detail = format_tool_calls(
                result["tool_calls"]
            )
            report += TASK_TEMPLATE.format(
                task_number=i + 1,
                prompt=task["prompt"],
                expected_response=task["response"],
                actual_response=result["actual"] or "N/A",
                correct_indicator="✅" if result["score"] else "❌",
                total_duration=result["total_duration"],
                tool_calls_count=tool_calls_count,
                tool_calls_detail=tool_calls_detail,
                summary=result["summary"] or "N/A",
                feedback=result["feedback"] or "N/A",
            )

        # Add summary table at the end
        report += SUMMARY_TABLE_HEADER
        for i, (task, result) in enumerate(zip(tasks, results)):
            # Extract failure reason from actual response if task failed
            failure_reason = ""
            if not result["score"]:
                actual = result["actual"] or ""
                if "ERROR" in actual:
                    # Extract first line of error or first 100 chars
                    failure_reason = actual.split("\n")[0][:100]
                elif result["feedback"]:
                    # Use feedback as failure reason
                    failure_reason = result["feedback"].split("\n")[0][:100]
                else:
                    failure_reason = "Response mismatch"

            report += format_summary_table_row(
                task_number=i + 1,
                prompt=task["prompt"],
                duration=result["total_duration"],
                is_success=bool(result["score"]),
                tool_calls=result["tool_calls"],
                failure_reason=failure_reason,
            )

        return report
    finally:
        # Cleanup global MCP session
        if mcp_server_url:
            await cleanup_global_mcp_session()
            print("🧹 Cleaned up MCP session")


# ============================================================================
# Main Entry Point
# ============================================================================


def get_all_evaluation_files() -> List[Path]:
    """
    Get all evaluation XML files from dataset directory.

    Returns:
        Sorted list of evaluation XML file paths
    """
    dataset_dir = Path(__file__).parent / "dataset"
    return sorted(dataset_dir.glob("evaluation*.xml"))


def resolve_eval_file(eval_name: str) -> Path:
    """
    Resolve evaluation file name to full path.

    Supports:
    - Short names: 'basic' -> 'dataset/evaluation_basic.xml'
    - Full names: 'evaluation_basic.xml' -> 'dataset/evaluation_basic.xml'
    - With extension: 'basic.xml' -> 'dataset/evaluation_basic.xml'
    - Default: 'evaluation.xml' -> 'dataset/evaluation.xml'
    """
    dataset_dir = Path(__file__).parent / "dataset"

    # Handle default case
    if eval_name == "evaluation.xml":
        return dataset_dir / "evaluation.xml"

    # Remove .xml extension if present
    eval_name = eval_name.replace(".xml", "")

    # If starts with 'evaluation_', remove the prefix
    if eval_name.startswith("evaluation_"):
        eval_name = eval_name[12:]  # Remove 'evaluation_' prefix

    # Construct full filename
    if eval_name == "evaluation" or eval_name == "":
        filename = "evaluation.xml"
    else:
        filename = f"evaluation_{eval_name}.xml"

    return dataset_dir / filename


async def main():
    """Main entry point for the tool evaluation."""
    parser = argparse.ArgumentParser(
        description="Run tool evaluation with specified evaluation file(s)"
    )
    parser.add_argument(
        "--eval",
        type=str,
        default=None,
        help="Evaluation file name (e.g., 'basic', 'browser'). If not specified, runs all evaluation files serially.",
    )
    args = parser.parse_args()

    # Determine which files to run
    if args.eval is None:
        # Run all evaluation files
        eval_files = get_all_evaluation_files()
        if not eval_files:
            print("❌ Error: No evaluation files found in dataset directory")
            return
        print(f"🚀 Running {len(eval_files)} evaluation files serially")
    else:
        # Run single evaluation file
        eval_file = resolve_eval_file(args.eval)
        if not eval_file.exists():
            print(f"❌ Error: Evaluation file not found: {eval_file}")
            print("Available evaluation files:")
            dataset_dir = Path(__file__).parent / "dataset"
            for file in sorted(dataset_dir.glob("evaluation*.xml")):
                # Extract short name for display
                short_name = file.stem.replace("evaluation_", "")
                if short_name == "evaluation":
                    short_name = "evaluation"
                print(f"  - {short_name} (→ {file.name})")
            return
        eval_files = [eval_file]

    # Process each evaluation file serially
    # Create date-based output directory (YYYYMMDD format in UTC+8)
    utc_plus_8 = timezone(timedelta(hours=8))
    date_str = datetime.now(utc_plus_8).strftime("%Y%m%d")
    output_dir = Path(__file__).parent / "result" / date_str
    output_dir.mkdir(parents=True, exist_ok=True)

    successful = 0
    failed = 0

    for idx, eval_file in enumerate(eval_files, 1):
        print(f"\n{'=' * 80}")
        print(f"📋 Processing [{idx}/{len(eval_files)}]: {eval_file.name}")
        print(f"{'=' * 80}")

        try:
            mcp_url = os.getenv("MCP_SERVER_URL")
            print(f"🔍 DEBUG: MCP_SERVER_URL = {mcp_url}")
            report = await run_evaluation(
                eval_path=str(eval_file),
                mcp_server_url=mcp_url,
            )

            # Generate output filename (will overwrite if exists)
            output_filename = f"{eval_file.stem}.md"
            output_path = output_dir / output_filename

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)

            print(f"✅ Evaluation report saved to: {output_path}")
            successful += 1

        except Exception as e:
            print(f"❌ Failed to process {eval_file.name}: {e}")
            traceback.print_exc()
            failed += 1
            # Continue with next file

    # Print summary
    print(f"\n{'=' * 80}")
    print(
        f"📊 Summary: {successful} successful, {failed} failed out of {len(eval_files)} total"
    )
    print(f"{'=' * 80}")


if __name__ == "__main__":
    # 运行所有评估文件（串行）
    # uv run main.py

    # 运行特定分类的评估（使用简短名称）
    # uv run main.py --eval basic
    # uv run main.py --eval browser
    # uv run main.py --eval collaboration
    # uv run main.py --eval workflow
    # uv run main.py --eval error
    # uv run main.py --eval util
    asyncio.run(main())
