"""
Configuration Management for Tool Evaluation Framework

Centralizes all configuration settings from environment variables.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class OpenAIConfig:
    """OpenAI API configuration."""

    base_url: str
    api_key: str
    model_id: str

    @classmethod
    def from_env(cls) -> "OpenAIConfig":
        """Create configuration from environment variables."""
        return cls(
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            api_key=os.getenv("OPENAI_API_KEY", "your-api-key"),
            model_id=os.getenv("OPENAI_MODEL_ID", "gpt-4"),
        )


@dataclass
class MCPConfig:
    """MCP Server configuration."""

    server_url: str

    @classmethod
    def from_env(cls) -> "MCPConfig":
        """Create configuration from environment variables."""
        return cls(
            server_url=os.getenv("MCP_SERVER_URL", "http://localhost:8080/mcp"),
        )


@dataclass
class AgentConfig:
    """Agent runtime configuration."""

    agent_type: str  # "openai", "langchain", "langchain-anthropic"
    model_name: str
    temperature: float
    max_iterations: int

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Create configuration from environment variables."""
        return cls(
            agent_type=os.getenv("AGENT_TYPE", "openai"),
            model_name=os.getenv("OPENAI_MODEL_ID", "gpt-4"),
            temperature=float(os.getenv("AGENT_TEMPERATURE", "0.0")),
            max_iterations=int(os.getenv("AGENT_MAX_ITERATIONS", "50")),
        )


@dataclass
class Config:
    """Complete application configuration."""

    openai: OpenAIConfig
    mcp: MCPConfig
    agent: AgentConfig

    @classmethod
    def from_env(cls) -> "Config":
        """Create complete configuration from environment variables."""
        return cls(
            openai=OpenAIConfig.from_env(),
            mcp=MCPConfig.from_env(),
            agent=AgentConfig.from_env(),
        )
