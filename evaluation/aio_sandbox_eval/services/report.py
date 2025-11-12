"""
Report Generator

Generates markdown evaluation reports from task results.
Separates presentation logic from evaluation logic.
"""

import json
from typing import Any, Dict, List, Tuple, Union

from aio_sandbox_eval.agent.type import ToolMetricsDict


class ReportGenerator:
    """Generates markdown reports for evaluation results."""
    HEADER_TEMPLATE = """
# Evaluation Report

## Configuration

- **Agent Type**: {agent_type}
- **Model Name**: {model_name}
- **Temperature**: {temperature}

---

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
## Detailed Summary Table

| # | Prompt | Duration | Success | Tool Calls | Steps | Failure Reason |
|---|--------|----------|---------|------------|-------|----------------|
"""

    def generate(
        self,
        tasks: List[Dict[str, Any]],
        results: List[Dict[str, Any]],
        agent_type: str = "N/A",
        model_name: str = "N/A",
        temperature: float = 0.0,
    ) -> str:
        """
        Generate complete evaluation report.

        Args:
            tasks: List of task definitions
            results: List of evaluation results
            agent_type: Agent type used for evaluation
            model_name: Model name used for evaluation
            temperature: Temperature setting used for evaluation

        Returns:
            Markdown formatted report
        """
        stats = self._calculate_statistics(results)

        stats["agent_type"] = agent_type
        stats["model_name"] = model_name
        stats["temperature"] = temperature

        report = self._generate_header(stats)
        report += self._generate_task_details(tasks, results)
        report += self._generate_summary_table(tasks, results)

        return report

    def _calculate_statistics(
        self, results: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate summary statistics from results."""
        if not results:
            return {
                "correct": 0,
                "total": 0,
                "accuracy": 0,
                "average_duration_s": 0,
                "average_tool_calls": 0,
                "total_tool_calls": 0,
            }

        correct = sum(r["score"] for r in results)
        total = len(results)
        accuracy = (correct / total) * 100

        total_duration = sum(r["total_duration"] for r in results)
        average_duration_s = total_duration / total

        total_tool_calls = sum(r["num_tool_calls"] for r in results)
        average_tool_calls = total_tool_calls / total

        return {
            "correct": correct,
            "total": total,
            "accuracy": accuracy,
            "average_duration_s": average_duration_s,
            "average_tool_calls": average_tool_calls,
            "total_tool_calls": total_tool_calls,
        }

    def _generate_header(self, stats: Dict[str, float]) -> str:
        """Generate report header with summary statistics."""
        return self.HEADER_TEMPLATE.format(**stats)

    def _generate_task_details(
        self,
        tasks: List[Dict[str, Any]],
        results: List[Dict[str, Any]],
    ) -> str:
        """Generate detailed section for each task."""
        report = ""

        for i, (task, result) in enumerate(zip(tasks, results)):
            tool_calls_count, tool_calls_detail = self._format_tool_calls(
                result["tool_calls"]
            )

            report += self.TASK_TEMPLATE.format(
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

        return report

    def _generate_summary_table(
        self,
        tasks: List[Dict[str, Any]],
        results: List[Dict[str, Any]],
    ) -> str:
        """Generate summary table with all tasks."""
        table = self.SUMMARY_TABLE_HEADER

        for i, (task, result) in enumerate(zip(tasks, results)):
            failure_reason = ""
            if not result["score"]:
                actual = result["actual"] or ""
                if "ERROR" in actual:
                    failure_reason = actual.split("\n")[0][:100]
                elif result["feedback"]:
                    failure_reason = result["feedback"].split("\n")[0][:100]
                else:
                    failure_reason = "Response mismatch"

            table += self._format_summary_row(
                task_number=i + 1,
                prompt=task["prompt"],
                duration=result["total_duration"],
                is_success=bool(result["score"]),
                tool_calls=result["tool_calls"],
                failure_reason=failure_reason,
            )

        return table

    def _format_tool_calls(
        self, tool_metrics: Union[ToolMetricsDict, Dict[str, Any]]
    ) -> Tuple[str, str]:
        """
        Format tool calls into summary and detailed views.

        Args:
            tool_metrics: ToolMetricsDict instance or dict with 'calls' list

        Returns:
            Tuple of (summary_str, detail_str)
        """
        # Handle both Pydantic model and dict for backward compatibility
        if isinstance(tool_metrics, ToolMetricsDict):
            calls = tool_metrics.calls
        elif isinstance(tool_metrics, dict):
            calls = tool_metrics.get("calls", [])
        else:
            return "No tools called", ""

        if not calls:
            return "No tools called", ""

        total_calls = len(calls)

        # Count unique tools - handle both Pydantic models and dicts
        unique_tools = set()
        for call in calls:
            if hasattr(call, "tool_name"):
                unique_tools.add(call.tool_name)
            else:
                unique_tools.add(call.get("tool_name", "unknown"))

        summary = f"{total_calls} calls across {len(unique_tools)} tools"

        detail_lines = ["#### Tool Execution Timeline", ""]
        for i, call in enumerate(calls, 1):
            # Handle both Pydantic models and dicts
            if hasattr(call, "tool_name"):
                tool_name = call.tool_name
                duration = call.duration
                args = call.args
            else:
                tool_name = call.get("tool_name", "unknown")
                duration = call.get("duration", 0)
                args = call.get("args", {})

            detail_lines.append(
                f"{i}. **{tool_name}** ({duration:.2f}s)"
            )

            if args:
                for key, value in args.items():
                    if isinstance(value, str):
                        value_str = f'"{value}"'
                    else:
                        value_str = json.dumps(value, ensure_ascii=False)
                    detail_lines.append(f"   - {key}: {value_str}")
            else:
                detail_lines.append("   - (no arguments)")

            detail_lines.append("")

        return summary, "\n".join(detail_lines)

    def _format_summary_row(
        self,
        task_number: int,
        prompt: str,
        duration: float,
        is_success: bool,
        tool_calls: Union[ToolMetricsDict, Dict[str, Any]],
        failure_reason: str = "",
    ) -> str:
        """
        Format a single row for the summary table.

        Args:
            task_number: Task number
            prompt: Task prompt
            duration: Task duration in seconds
            is_success: Whether task succeeded
            tool_calls: ToolMetricsDict instance or dict with 'calls' list
            failure_reason: Reason for failure if applicable

        Returns:
            Markdown table row
        """
        cleaned_prompt = " ".join(prompt.split())

        duration_str = f"{duration:.2f}s"
        success_str = "✅" if is_success else "❌"

        # Get calls from ToolMetricsDict - handle both Pydantic model and dict
        if isinstance(tool_calls, ToolMetricsDict):
            calls = tool_calls.calls
        elif isinstance(tool_calls, dict):
            calls = tool_calls.get("calls", [])
        else:
            calls = []

        tool_call_count = len(calls)

        # Format tool steps - handle both Pydantic models and dicts
        tool_steps = []
        if calls:
            for i, call in enumerate(calls):
                if hasattr(call, "tool_name"):
                    tool_steps.append(f"{i+1}. {call.tool_name}")
                else:
                    tool_steps.append(f"{i+1}. {call.get('tool_name', 'unknown')}")

        steps_str = "<br>".join(tool_steps) if tool_steps else "N/A"
        failure_str = failure_reason if not is_success else "-"

        return f"| {task_number} | {cleaned_prompt} | {duration_str} | {success_str} | {tool_call_count} | {steps_str} | {failure_str} |\n"
