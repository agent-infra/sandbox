"""
Metrics Collection

Helper class for collecting and tracking tool execution metrics.
"""

from typing import Any, Dict, List, Optional

from ..type.tool_result import ToolCallRecord, ToolMetricsDict


class MetricsCollector:
    """
    Helper class for collecting tool metrics.

    Example:
        collector = MetricsCollector()
        collector.record_call("get_weather", {...}, 0.5, success=True)
        metrics = collector.to_dict()
    """

    def __init__(self):
        """Initialize empty metrics collector."""
        import time

        self._start_time = time.time()
        self._end_time: Optional[float] = None
        self._calls: List[ToolCallRecord] = []

    def record_call(
        self,
        tool_name: str,
        args: Dict[str, Any],
        duration: float,
        timestamp: Optional[float] = None,
        success: bool = True,
        error: Optional[str] = None,
    ) -> None:
        """Record a tool call."""
        import time

        if timestamp is None:
            timestamp = time.time()

        record = ToolCallRecord(
            tool_name=tool_name,
            args=args,
            duration=duration,
            timestamp=timestamp,
            success=success,
            error=error,
        )
        self._calls.append(record)

    def finalize(self) -> None:
        """Mark metrics collection as complete."""
        import time

        self._end_time = time.time()

    def to_dict(self) -> ToolMetricsDict:
        """Export metrics as structured dictionary."""
        return ToolMetricsDict(
            calls=self._calls.copy(),
            start_time=self._start_time,
            end_time=self._end_time,
        )
