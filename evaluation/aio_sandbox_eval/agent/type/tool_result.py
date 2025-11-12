"""
Tool Result and Metrics Type Definitions

Defines types for tool execution results and performance metrics.
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from mcp.types import CallToolResult

    ToolResult = CallToolResult
else:
    # At runtime, ToolResult is just a dict
    ToolResult = Dict[str, Any]


class ToolCallRecord(BaseModel):
    """Record of a single tool call."""

    tool_name: str
    args: Dict[str, Any] = Field(default_factory=dict)
    duration: float
    timestamp: float
    success: bool
    error: Optional[str] = None


class ToolMetricsDict(BaseModel):
    """Complete metrics collection."""

    calls: List[ToolCallRecord] = Field(
        default_factory=list, description="all calls in chronological order"
    )
    start_time: float
    end_time: Optional[float] = None


__all__ = [
    "ToolResult",
    "ToolCallRecord",
    "ToolMetricsDict",
]
