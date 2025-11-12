"""
AIO Sandbox Evaluation Framework

A modular evaluation framework for testing AI agents with MCP tools.
"""

__version__ = "1.0.0"

from .core.config import AgentConfig, Config, MCPConfig, OpenAIConfig
from .core.runner import EvaluationRunner
from .services.evaluator import TaskEvaluator
from .services.mcp_client import MCPClient
from .services.report import ReportGenerator
from .services.uploader import SandboxUploader

# Agent (abstractions and registry only)
from .agent import (
    BaseAgentLoop,
    AgentMessage,
    AgentResponse,
    AgentRegistry,
    ToolCall,
)

__all__ = [
    # Version
    "__version__",
    # Core
    "Config",
    "OpenAIConfig",
    "MCPConfig",
    "AgentConfig",
    "EvaluationRunner",
    # Services
    "MCPClient",
    "TaskEvaluator",
    "ReportGenerator",
    "SandboxUploader",
    # Agent (abstractions and registry only)
    "BaseAgentLoop",
    "AgentMessage",
    "AgentResponse",
    "AgentRegistry",
    "ToolCall",
]
