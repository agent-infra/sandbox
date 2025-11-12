"""
Exception Type Definitions

Defines custom exceptions for agent runtime operations.
"""


class AgentLoopError(Exception):
    """Base exception for agent loop errors."""

    pass


class ToolExecutionError(AgentLoopError):
    """Raised when tool execution fails."""

    pass


class LLMCallError(AgentLoopError):
    """Raised when LLM API call fails."""

    pass


class MaxIterationsError(AgentLoopError):
    """Raised when max iterations exceeded."""

    pass


__all__ = [
    "AgentLoopError",
    "ToolExecutionError",
    "LLMCallError",
    "MaxIterationsError",
]
