"""
Message Type Definitions

Defines types for agent messages and responses.
"""

from typing import Any, Dict, List, Literal, Optional, Union

from openai.types.chat import ChatCompletionMessageToolCall
from pydantic import BaseModel, Field

from .tool_result import ToolMetricsDict

# Type alias for backward compatibility
LLMToolCall = ChatCompletionMessageToolCall


class AgentMessage(BaseModel):
    """
    Represents a message in the agent conversation.

    Attributes:
        role: Message role (user, assistant, system, tool)
        content: Message content
        name: Optional name for the message sender
        tool_calls: Optional list of tool calls made by assistant (OpenAI format)
        tool_call_id: Optional ID linking tool response to tool call
    """

    role: Literal["user", "assistant", "system", "tool"]
    content: Optional[str] = None
    name: Optional[str] = None
    tool_calls: Optional[List[LLMToolCall]] = None
    tool_call_id: Optional[str] = None


class ToolCall(BaseModel):
    """
    Represents a tool call made by the agent.

    Attributes:
        id: Unique identifier for this tool call
        name: Name of the tool being called
        arguments: Arguments passed to the tool
        timestamp: Timestamp when the call was made
        duration: Time taken to execute (in seconds)
    """

    id: str
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float
    duration: float = 0.0


class AgentResponse(BaseModel):
    """
    Complete response from agent execution.

    Attributes:
        content: Final response content
        tool_calls: List of all tool calls made
        tool_metrics: Detailed metrics for each tool
        messages: Complete conversation history
        metadata: Additional metadata (model, tokens, etc.)
    """

    content: str
    tool_calls: List[ToolCall] = Field(default_factory=list)
    tool_metrics: ToolMetricsDict = Field(default_factory=ToolMetricsDict)
    messages: List[AgentMessage] = Field(default_factory=list)
    metadata: Dict[str, Union[str, int, float, bool]] = Field(default_factory=dict)


__all__ = [
    "AgentMessage",
    "ToolCall",
    "AgentResponse",
]
