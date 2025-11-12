"""
Agent Module

Provides extensible agent runtime architecture for evaluation framework.

This module only defines abstractions and the registry mechanism.
Agent implementations should be provided externally and registered
using AgentRegistry.

Users can extend BaseAgentLoop to create custom agent runtimes.
"""

from .abc import BaseAgentLoop
from .registry import AgentRegistry
from .type import (
    # Type definitions
    AgentLoopError,
    AgentMessage,
    AgentResponse,
    LLMCallError,
    LLMChoice,
    LLMMessage,
    LLMResponse,
    LLMToolCall,
    MaxIterationsError,
    ToolCall,
    ToolCallRecord,
    ToolDefinition,
    ToolExecutionError,
    ToolFunction,
    ToolFunctionParameters,
    ToolMetricsDict,
    ToolResult,
)

__all__ = [
    # Type definitions
    "ToolFunctionParameters",
    "ToolFunction",
    "ToolDefinition",
    "LLMToolCall",
    "LLMMessage",
    "LLMChoice",
    "LLMResponse",
    "ToolResult",
    "ToolCallRecord",
    "ToolMetricsDict",
    # Base classes and data classes
    "BaseAgentLoop",
    "AgentMessage",
    "AgentResponse",
    "ToolCall",
    # Exceptions
    "AgentLoopError",
    "LLMCallError",
    "ToolExecutionError",
    "MaxIterationsError",
    # Registry
    "AgentRegistry",
]
