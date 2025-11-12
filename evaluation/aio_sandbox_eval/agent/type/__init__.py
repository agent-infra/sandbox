"""
Type Definitions for Agent Runtime

This module exports type definitions for the agent runtime.

Uses OpenAI SDK official types for LLM-related types (recommended approach).
"""

from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessage,
    ChatCompletionMessageToolCall,
    ChatCompletionToolParam,
)
from openai.types.chat.chat_completion import Choice
from openai.types.shared_params import FunctionDefinition

LLMResponse = ChatCompletion
LLMMessage = ChatCompletionMessage
LLMToolCall = ChatCompletionMessageToolCall
LLMChoice = Choice
ToolDefinition = ChatCompletionToolParam
ToolFunction = FunctionDefinition

from typing import Dict, Any
ToolFunctionParameters = Dict[str, Any]

from .exception import (
    AgentLoopError,
    LLMCallError,
    MaxIterationsError,
    ToolExecutionError,
)
from .message import AgentMessage, AgentResponse, ToolCall
from .tool_result import ToolCallRecord, ToolMetricsDict, ToolResult

__all__ = [
    "ChatCompletion",
    "ChatCompletionMessage",
    "ChatCompletionMessageToolCall",
    "ChatCompletionToolParam",
    "Choice",
    "FunctionDefinition",
    "LLMResponse",
    "LLMMessage",
    "LLMToolCall",
    "LLMChoice",
    "ToolDefinition",
    "ToolFunction",
    "ToolFunctionParameters",
    "ToolResult",
    "ToolCallRecord",
    "ToolMetricsDict",
    "AgentMessage",
    "ToolCall",
    "AgentResponse",
    "AgentLoopError",
    "ToolExecutionError",
    "LLMCallError",
    "MaxIterationsError",
]
