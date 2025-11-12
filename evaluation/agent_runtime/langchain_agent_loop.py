"""
LangChain Agent Loop Implementation

This implementation uses LangChain 1.0+ create_agent API with MCP adapter.
"""

import os
from typing import Any, Dict, List, override

try:
    from langchain.agents import create_agent
    from langchain_openai import ChatOpenAI
except ImportError:
    # Graceful fallback if LangChain not installed
    create_agent = None
    ChatOpenAI = None

from aio_sandbox_eval.agent.abc import BaseAgentLoop
from aio_sandbox_eval.agent.registry import AgentRegistry
from aio_sandbox_eval.agent.type import (
    AgentMessage,
    ToolDefinition,
    ToolExecutionError,
    ToolResult,
)


@AgentRegistry.register("langchain")
class LangChainAgentLoop(BaseAgentLoop):
    """
    Agent loop implementation using LangChain 1.0+ create_agent API.

    This implementation integrates LangChain agents with the evaluation framework
    using the modern create_agent API that returns a CompiledStateGraph.

    Example:
        agent = LangChainAgentLoop(
            mcp_session=session,
            model_name="gpt-4",
        )
        response, metrics = await agent.run(prompt, tools)
    """

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
        Initialize LangChain agent loop.

        Args:
            mcp_session: MCP client session for tool execution
            model_id: Model ID to use
            max_iterations: Maximum number of agent iterations
            base_url: API base URL
            api_key: API key

        Raises:
            ImportError: If langchain packages are not installed
        """
        if create_agent is None:
            raise ImportError(
                "langchain packages are required for LangChainAgentLoop. "
                "Install with: pip install langchain langchain-openai"
            )

        super().__init__(
            mcp_session=mcp_session,
            model_id=model_id,
            max_iterations=max_iterations,
            base_url=base_url,
            api_key=api_key,
        )

    @override
    async def run(
        self,
        prompt: str,
        tools: List[ToolDefinition],
    ) -> List[AgentMessage]:
        """
        Execute LangChain agent loop.

        Args:
            prompt: User prompt/task
            tools: List of tool definitions in OpenAI function calling format
                   (Not used - tools are loaded directly from MCP session)

        Returns:
            List of conversation messages
        """
        from langchain_mcp_adapters.tools import load_mcp_tools

        # Load MCP tools directly using langchain-mcp-adapters (one-liner!)
        langchain_tools = await load_mcp_tools(self.mcp_session)

        # Create and run agent
        agent_graph = create_agent(
            model=ChatOpenAI(
                model=self.model_id,
                base_url=self.base_url,
                api_key=self.api_key,
                temperature=0.0,
            ),
            tools=langchain_tools,
            system_prompt=self.system_prompt,
        )

        # Execute
        result = await agent_graph.ainvoke(
            {"messages": [{"role": "user", "content": prompt}]},
            config={"recursion_limit": self.max_iterations},
        )

        # Convert LangChain messages to AgentMessage
        agent_messages = []
        for msg in result.get("messages", []):
            if hasattr(msg, "content") and hasattr(msg, "type"):
                role = (
                    msg.type
                    if msg.type in ["user", "assistant", "system", "tool"]
                    else "assistant"
                )
                agent_messages.append(AgentMessage(role=role, content=msg.content))
            elif isinstance(msg, dict):
                agent_messages.append(
                    AgentMessage(
                        role=msg.get("role", "assistant"),
                        content=msg.get("content", ""),
                    )
                )

        return agent_messages
