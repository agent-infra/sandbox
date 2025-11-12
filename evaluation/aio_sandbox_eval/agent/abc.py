"""
Abstract Base Classes for Agent Runtime

Defines the interface for custom agent implementations.
"""

import time
from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Callable, Dict, List, Tuple, TYPE_CHECKING

from ..prompt.eval_prompt import DEFAULT_SYSTEM_PROMPT
from .type import (
    AgentMessage,
    ToolMetricsDict,
    ToolResult,
    ToolDefinition,
    ToolExecutionError,
)
from .metrics import MetricsCollector

if TYPE_CHECKING:
    from typing import TypeVar

    _AgentT = TypeVar("_AgentT", bound="BaseAgentLoop")


def track_tool_calls(func: Callable) -> Callable:
    """
    Decorator to automatically track tool call metrics.

    Wraps call_tool to automatically record metrics without
    user intervention. The agent instance must have a _metrics_collector
    attribute.
    """

    @wraps(func)
    async def wrapper(
        self: "BaseAgentLoop", tool_name: str, arguments: Dict[str, Any], **kwargs
    ) -> ToolResult:
        start_time = time.time()
        error = None
        success = True

        try:
            result = await func(self, tool_name, arguments, **kwargs)
            return result
        except Exception as e:
            success = False
            error = str(e)
            raise
        finally:
            duration = time.time() - start_time

            if hasattr(self, "_metrics_collector"):
                self._metrics_collector.record_call(
                    tool_name=tool_name,
                    args=arguments,
                    duration=duration,
                    timestamp=start_time,
                    success=success,
                    error=error,
                )

    return wrapper


class BaseAgentLoop(ABC):
    """
    Abstract base class for agent runtime implementations.

    Subclasses must implement:
    - run(): Main execution loop - returns List[AgentMessage]
    - call_tool(): Tool execution

    Tool call metrics are automatically tracked - no decorator needed!

    Example:
        class MyAgent(BaseAgentLoop):
            def __init__(self, mcp_session):
                super().__init__()
                self.mcp_session = mcp_session

            async def run(self, prompt, tools):
                messages = [...]
                # Your agent loop implementation
                return messages

            async def call_tool(self, tool_name, args):
                # Your tool execution implementation
                # Metrics tracked automatically!
                result = await self.mcp_session.call_tool(tool_name, args)
                return result
    """

    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    _metrics_collector: MetricsCollector

    def __init_subclass__(cls, **kwargs):
        """
        Automatically wrap call_tool with metrics tracking.

        This is called when a subclass is created, so users don't need
        to manually add the @track_tool_calls decorator.
        """
        super().__init_subclass__(**kwargs)

        if "call_tool" in cls.__dict__:
            original_method = cls.__dict__["call_tool"]

            if not hasattr(original_method, "__wrapped__"):
                cls.call_tool = track_tool_calls(original_method)

    def __init__(
        self,
        *,
        mcp_session,
        model_id: str,
        max_iterations: int,
        base_url: str,
        api_key: str,
    ):
        """
        Initialize base agent loop.

        Args:
            mcp_session: MCP session for tool execution
            model_id: Model identifier
            max_iterations: Maximum agent iterations
            base_url: API base URL (for OpenAI-compatible APIs)
            api_key: API key

        Subclasses should call super().__init__() and then initialize
        their own specific attributes.
        """
        self._metrics_collector = MetricsCollector()
        self.mcp_session = mcp_session
        self.model_id = model_id
        self.max_iterations = max_iterations
        self.base_url = base_url
        self.api_key = api_key

    @abstractmethod
    async def run(
        self,
        prompt: str,
        tools: List[ToolDefinition],
    ) -> List[AgentMessage]:
        """
        Implement your agent loop here.

        Args:
            prompt: User prompt to process
            tools: Available tools in OpenAI function calling format

        Returns:
            List of conversation messages (the last assistant message will be extracted as response)

        Example:
            async def run(self, prompt, tools):
                messages = [
                    AgentMessage(role="system", content=self.system_prompt),
                    AgentMessage(role="user", content=prompt),
                ]

                while True:
                    response = await your_llm_call(messages, tools)
                    messages.append(response)

                    if no_tool_calls:
                        break

                    # Execute tools (metrics auto-tracked!)
                    for tool_call in response.tool_calls:
                        result = await self.call_tool(...)
                        messages.append(result)

                return messages
        """
        raise NotImplementedError("Subclasses must implement run()")

    async def run_in_eval(
        self,
        prompt: str,
        tools: List[ToolDefinition],
    ) -> Tuple[str, ToolMetricsDict]:
        """
        Execute the agent loop for evaluation.

        This is a wrapper that calls run() and automatically handles
        response extraction and metrics collection. Used by eval framework.

        Args:
            prompt: User prompt to process
            tools: Available tools in OpenAI function calling format

        Returns:
            Tuple of:
            - response_text: Final response containing <response>, <summary>, <feedback> XML tags
            - tool_metrics: Dictionary mapping tool names to their execution metrics

        Raises:
            LLMCallError: If LLM API call fails
            ToolExecutionError: If tool execution fails
            MaxIterationsError: If max iterations exceeded
        """
        messages = await self.run(prompt, tools)

        response_text = self._extract_final_response(messages)

        self._metrics_collector.finalize()
        metrics = self._metrics_collector.to_dict()

        return response_text, metrics

    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> ToolResult:
        """
        Execute a tool call via MCP.

        This method provides a default implementation that calls MCP session directly.
        You only need to override this if you have custom tool execution logic
        (e.g., retry logic, caching, custom error handling).

        Args:
            tool_name: Name of the tool to call (must match tool definition)
            arguments: Tool arguments as key-value pairs

        Returns:
            Tool execution result in MCP format:
            {
                "content": [{"type": "text", "text": "Result data"}],
                "isError": False  # Optional, indicates if execution failed
            }

        Raises:
            ToolExecutionError: If tool execution fails

        Example:
            result = await self.call_tool(
                tool_name="get_weather",
                arguments={"location": "Tokyo"}
            )
            # Returns: {"content": [{"type": "text", "text": "Sunny, 25°C"}]}

        Note:
            Override this method only if you need custom behavior:
            - Adding retry logic
            - Tool result caching
            - Custom error handling
            - Tool call transformation
        """
        if not self.mcp_session:
            raise ToolExecutionError("No MCP session available for tool execution")

        try:
            result = await self.mcp_session.call_tool(tool_name, arguments=arguments)
            # Convert CallToolResult (Pydantic model) to dict for JSON serialization
            if hasattr(result, "model_dump"):
                return result.model_dump()
            return result
        except Exception as e:
            raise ToolExecutionError(f"Failed to execute tool {tool_name}: {e}") from e

    def _extract_final_response(self, messages: List[AgentMessage]) -> str:
        """
        Extract final response from conversation messages.

        Args:
            messages: List of conversation messages

        Returns:
            Final response text from last assistant message
        """
        for message in reversed(messages):
            if message.role == "assistant" and message.content:
                return message.content

        return "ERROR: No assistant response found"


__all__ = [
    "BaseAgentLoop",
]
