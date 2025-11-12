"""
Task Evaluator

Handles evaluation of individual tasks with agent execution and scoring.
"""

import re
import time
import traceback
from typing import Any, Dict, List

from aio_sandbox_eval.agent import BaseAgentLoop


class TaskEvaluator:
    """
    Evaluates tasks by running them with an agent and scoring results.

    Responsibilities:
    - Execute tasks with agents
    - Extract responses from agent output
    - Score responses against ground truth
    - Handle errors gracefully
    """

    @staticmethod
    def _extract_xml_content(text: str, tag: str) -> str | None:
        """
        Extract content from XML-like tags.

        Args:
            text: Text containing XML tags
            tag: Tag name to extract

        Returns:
            Extracted content or None if not found
        """
        if not text:
            return None
        pattern = rf"<{tag}>(.*?)</{tag}>"
        matches = re.findall(pattern, text, re.DOTALL)
        return matches[-1].strip() if matches else None

    @staticmethod
    def _score_response(actual: str, expected: str) -> int:
        """
        Score actual response against expected response.

        Uses regex matching if expected is a valid regex pattern,
        otherwise falls back to exact string comparison.

        Args:
            actual: Actual response from agent
            expected: Expected response (may be regex pattern)

        Returns:
            1 if match, 0 otherwise
        """
        if not actual:
            return 0

        try:
            # Use regex search for pattern matching (allows partial match)
            if re.search(expected, actual, re.DOTALL):
                return 1
        except re.error:
            # If pattern is invalid, fall back to exact comparison
            return int(actual == expected)

        return 0

    async def evaluate(
        self,
        task: Dict[str, Any],
        agent: BaseAgentLoop,
        tools: List[Dict[str, Any]],
        task_index: int,
    ) -> Dict[str, Any]:
        """
        Evaluate a single task.

        Args:
            task: Task definition with 'prompt' and 'response' keys
            agent: Agent instance to execute the task
            tools: Available tools for the agent
            task_index: Index of the task (for logging)

        Returns:
            Dictionary with evaluation results including:
            - prompt: Original prompt
            - expected: Expected response
            - actual: Actual response
            - score: 1 if correct, 0 otherwise
            - total_duration: Execution time in seconds
            - tool_calls: Tool call metrics
            - num_tool_calls: Total number of tool calls
            - summary: Agent's summary
            - feedback: Agent's feedback
        """
        start_time = time.time()

        print(f"Task {task_index + 1}: Running task with prompt: {task['prompt']}")

        try:
            # Execute task with agent
            response, tool_metrics = await agent.run_in_eval(task["prompt"], tools)

            # Extract tagged content from response
            actual_response = self._extract_xml_content(response, "response")
            summary = self._extract_xml_content(response, "summary")
            feedback = self._extract_xml_content(response, "feedback")

            # Calculate duration and score
            duration_seconds = time.time() - start_time
            score = self._score_response(actual_response, task["response"])

            # Handle both Pydantic model and dict for tool_metrics
            if hasattr(tool_metrics, "calls"):
                num_tool_calls = len(tool_metrics.calls)
            else:
                num_tool_calls = len(tool_metrics.get("calls", []))

            return {
                "prompt": task["prompt"],
                "expected": task["response"],
                "actual": actual_response,
                "score": score,
                "total_duration": duration_seconds,
                "tool_calls": tool_metrics,
                "num_tool_calls": num_tool_calls,
                "summary": summary,
                "feedback": feedback,
            }

        except Exception as e:
            # Handle complete task failure
            duration_seconds = time.time() - start_time
            error_type = type(e).__name__
            error_msg = str(e)

            print(
                f"❌ Task {task_index + 1} failed completely: {error_type}: {error_msg}"
            )
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
