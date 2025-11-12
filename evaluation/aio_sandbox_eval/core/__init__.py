"""
Core modules for evaluation framework.

Contains configuration and main runner logic.
"""

from .config import Config, MCPConfig, OpenAIConfig
from .runner import EvaluationRunner

__all__ = [
    "Config",
    "OpenAIConfig",
    "MCPConfig",
    "EvaluationRunner",
]
