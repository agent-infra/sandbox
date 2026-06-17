"""
Agent Loop Module

Provides different agent loop implementations (Azure OpenAI, OpenAI-compatible, LangGraph, etc.).
Follows the strategy pattern for easy runtime switching.

Supported backends:
- Azure OpenAI (AzureOpenAIAgentLoop)
- OpenAI and compatible APIs such as MiniMax (OpenAIAgentLoop)
- LangGraph (LangGraphAgentLoop) — placeholder
"""

import json
import os
import re
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

from mcp import ClientSession
from openai import AzureOpenAI, OpenAI


# ============================================================================
# Default System Prompt
# ============================================================================

DEFAULT_SYSTEM_PROMPT = """You are an AI assistant with access to tools.

When given a task, you MUST:
1. Use the available tools to complete the task
2. Provide summary of each step in your approach, wrapped in <summary> tags
3. Provide feedback on the tools provided, wrapped in <feedback> tags
4. Provide your final response, wrapped in <response> tags
5. Don't use VLM tools, like screenshot, etc.

Summary Requirements:
- In your <summary> tags, you must explain:
  - The steps you took to complete the task
  - Which tools you used, in what order, and why
  - The inputs you provided to each tool
  - The outputs you received from each tool
  - A summary for how you arrived at the response

Feedback Requirements:
- In your <feedback> tags, provide constructive feedback on the tools:
  - Comment on tool names: Are they clear and descriptive?
  - Comment on input parameters: Are they well-documented? Are required vs optional parameters clear?
  - Comment on descriptions: Do they accurately describe what the tool does?
  - Comment on any errors encountered during tool usage: Did the tool fail to execute? Did the tool return too many tokens?
  - Identify specific areas for improvement and explain WHY they would help
  - Be specific and actionable in your suggestions

Response Requirements:
- Your response should be concise and directly address what was asked
- Always wrap your final response in <response> tags
- If you cannot solve the task return <response>NOT_FOUND</response>
- For numeric responses, provide just the number
- For IDs, provide just the ID
- For names or text, provide the exact text requested
- Your response should go last"""


# ============================================================================
# Base Agent Loop
# ============================================================================


class BaseAgentLoop(ABC):
    """
    Abstract base class for agent loop implementations.

    An agent loop is responsible for:
    1. Taking a user prompt and available tools
    2. Executing an LLM reasoning loop with tool calling
    3. Returning the final response and execution metrics
    """

    def __init__(
        self,
        mcp_session: ClientSession,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ):
        """
        Initialize agent loop.

        Args:
            mcp_session: MCP client session for tool execution
            system_prompt: System prompt for the agent
        """
        self.mcp_session = mcp_session
        self.system_prompt = system_prompt

    @abstractmethod
    async def run(
        self,
        prompt: str,
        tools: List[Dict[str, Any]] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Execute agent loop.

        Args:
            prompt: User prompt/task
            tools: List of tool definitions

        Returns:
            Tuple of (response_text, tool_metrics)
            - response_text: Final LLM response (including <summary>, <feedback>, <response> tags)
            - tool_metrics: Dict mapping tool names to execution metrics
        """
        pass


# ============================================================================
# Azure OpenAI Agent Loop
# ============================================================================


class AzureOpenAIAgentLoop(BaseAgentLoop):
    """Agent loop implementation using Azure OpenAI."""

    def __init__(
        self,
        mcp_session: ClientSession,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        azure_endpoint: str = None,
        azure_api_key: str = None,
        azure_deployment: str = None,
        azure_api_version: str = None,
        max_iterations: int = 50,
    ):
        """
        Initialize Azure OpenAI agent loop.

        Args:
            mcp_session: MCP client session for tool execution
            system_prompt: System prompt for the agent
            azure_endpoint: Azure OpenAI endpoint (default: from env)
            azure_api_key: Azure OpenAI API key (default: from env)
            azure_deployment: Azure OpenAI deployment name (default: from env)
            azure_api_version: Azure OpenAI API version (default: from env)
            max_iterations: Maximum number of reasoning iterations
        """
        super().__init__(mcp_session, system_prompt)

        self.azure_endpoint = azure_endpoint or os.getenv(
            "AZURE_OPENAI_ENDPOINT", "https://your-endpoint.openai.azure.com"
        )
        self.azure_api_key = azure_api_key or os.getenv(
            "AZURE_OPENAI_API_KEY", "your-api-key"
        )
        self.azure_deployment = azure_deployment or os.getenv(
            "AZURE_OPENAI_DEPLOYMENT", "gpt-4"
        )
        self.azure_api_version = azure_api_version or os.getenv(
            "AZURE_OPENAI_API_VERSION", "2024-02-15-preview"
        )
        self.max_iterations = max_iterations

        self.client = AzureOpenAI(
            azure_endpoint=self.azure_endpoint,
            api_key=self.azure_api_key,
            api_version=self.azure_api_version,
        )

    async def run(
        self,
        prompt: str,
        tools: List[Dict[str, Any]] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Execute Azure OpenAI agent loop.

        Args:
            prompt: User prompt/task
            tools: List of tool definitions in Azure OpenAI format

        Returns:
            Tuple of (response_text, tool_metrics)
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]

        tool_metrics = {}
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1

            # Make API call
            kwargs = {
                "model": self.azure_deployment,
                "messages": messages,
                "max_tokens": 4096,
            }

            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = self.client.chat.completions.create(**kwargs)
            message = response.choices[0].message

            # Add assistant message to conversation
            messages.append(
                {
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": message.tool_calls
                    if hasattr(message, "tool_calls") and message.tool_calls
                    else None,
                }
            )

            # Check if we're done
            if not message.tool_calls:
                final_content = message.content or ""
                print(f"\n🔍 DEBUG: Final LLM response (first 1000 chars):")
                print(f"{final_content[:1000]}")
                if len(final_content) > 1000:
                    print(
                        f"... (truncated, total length: {len(final_content)} chars)"
                    )
                print()

                # Verify response contains required tags - force retry if missing
                missing_tags = []
                if "<response>" not in final_content:
                    missing_tags.append("<response>")
                if "<summary>" not in final_content:
                    missing_tags.append("<summary>")
                if "<feedback>" not in final_content:
                    missing_tags.append("<feedback>")

                if missing_tags:
                    print(
                        f"⚠️  LLM response missing required tags: {', '.join(missing_tags)}"
                    )
                    print(
                        f"   Forcing retry (iteration {iteration}/{self.max_iterations})..."
                    )
                    messages.append(
                        {
                            "role": "user",
                            "content": f"ERROR: Your response is missing required tags: {', '.join(missing_tags)}. You MUST provide ALL THREE tags: <summary>, <feedback>, and <response>. Please provide your complete response now with all three tags.",
                        }
                    )
                    continue  # Go back to the loop

                return final_content, tool_metrics

            # Process tool calls
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error for tool {tool_name}")
                    print(f"   Arguments: {tool_call.function.arguments[:200]}...")
                    print(f"   Error: {e}")
                    raise

                print(f"🔧 Executing tool: {tool_name}")
                print(f"   Arguments: {json.dumps(tool_args, ensure_ascii=False)}")
                tool_start_ts = time.time()

                # Execute tool with error handling
                try:
                    tool_result = await self.mcp_session.call_tool(tool_name, tool_args)
                    tool_duration = time.time() - tool_start_ts
                    print(f"✅ Tool {tool_name} completed in {tool_duration:.2f}s")
                except Exception as e:
                    tool_duration = time.time() - tool_start_ts
                    error_type = type(e).__name__
                    error_msg = str(e)
                    print(f"❌ Tool {tool_name} failed after {tool_duration:.2f}s")
                    print(f"   Error: {error_type}: {error_msg}")
                    # Return error as tool result so LLM knows what happened
                    tool_result = {
                        "isError": True,
                        "content": [
                            {
                                "type": "text",
                                "text": f"ERROR: Tool execution failed\nType: {error_type}\nMessage: {error_msg}\n\nThis tool is not available or encountered an error. Please try a different approach.",
                            }
                        ],
                    }

                # Update tool metrics
                if tool_name not in tool_metrics:
                    tool_metrics[tool_name] = {"count": 0, "durations": [], "calls": []}
                tool_metrics[tool_name]["count"] += 1
                tool_metrics[tool_name]["durations"].append(tool_duration)
                tool_metrics[tool_name]["calls"].append(
                    {
                        "args": tool_args,
                        "duration": tool_duration,
                        "timestamp": tool_start_ts,
                    }
                )

                # Add tool response to conversation
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(tool_result),
                    }
                )

        # If we hit max iterations, find the last assistant message
        for msg in reversed(messages):
            if msg.get("role") == "assistant" and msg.get("content"):
                return msg["content"], tool_metrics
        return "", tool_metrics


# ============================================================================
# OpenAI-Compatible Agent Loop
# ============================================================================

# Models that require temperature > 0
_TEMPERATURE_POSITIVE_MODELS = re.compile(r"MiniMax", re.IGNORECASE)

# Models that may wrap content in <think>...</think> tags
_THINKING_TAG_MODELS = re.compile(r"MiniMax-M2", re.IGNORECASE)


class OpenAIAgentLoop(BaseAgentLoop):
    """
    Agent loop implementation using the standard OpenAI SDK.

    Works with OpenAI and any OpenAI-compatible API by setting ``base_url``.
    For example, to use MiniMax::

        agent = OpenAIAgentLoop(
            mcp_session=session,
            api_key=os.getenv("MINIMAX_API_KEY"),
            base_url="https://api.minimax.io/v1",
            model="MiniMax-M2.7",
        )
    """

    def __init__(
        self,
        mcp_session: ClientSession,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        api_key: str = None,
        base_url: str = None,
        model: str = None,
        max_iterations: int = 50,
        temperature: float = None,
    ):
        """
        Initialize OpenAI-compatible agent loop.

        Args:
            mcp_session: MCP client session for tool execution
            system_prompt: System prompt for the agent
            api_key: API key (default: ``OPENAI_API_KEY`` env var)
            base_url: Base URL for the API. Set to
                ``https://api.minimax.io/v1`` for MiniMax, or leave as
                ``None`` for official OpenAI.
            model: Model name (default: ``OPENAI_MODEL`` env var or ``gpt-4``)
            max_iterations: Maximum number of reasoning iterations
            temperature: Sampling temperature. Auto-clamped for providers
                that require ``temperature > 0`` (e.g. MiniMax).
        """
        super().__init__(mcp_session, system_prompt)

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4")
        self.max_iterations = max_iterations
        self.temperature = temperature

        client_kwargs: Dict[str, Any] = {}
        if self.api_key:
            client_kwargs["api_key"] = self.api_key
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        self.client = OpenAI(**client_kwargs)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _effective_temperature(self) -> float | None:
        """Return temperature, clamped if the model requires it."""
        temp = self.temperature
        if temp is not None and _TEMPERATURE_POSITIVE_MODELS.search(self.model):
            temp = max(temp, 0.01)
        return temp

    @staticmethod
    def _strip_thinking_tags(text: str) -> str:
        """Remove ``<think>…</think>`` blocks some models emit."""
        return re.sub(r"<think>[\s\S]*?</think>\s*", "", text)

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    async def run(
        self,
        prompt: str,
        tools: List[Dict[str, Any]] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Execute the agent loop.

        Args:
            prompt: User prompt/task
            tools: List of tool definitions in OpenAI format

        Returns:
            Tuple of (response_text, tool_metrics)
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]

        tool_metrics: Dict[str, Any] = {}
        iteration = 0
        strip_think = bool(_THINKING_TAG_MODELS.search(self.model))

        while iteration < self.max_iterations:
            iteration += 1

            kwargs: Dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 4096,
            }

            temp = self._effective_temperature()
            if temp is not None:
                kwargs["temperature"] = temp

            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = self.client.chat.completions.create(**kwargs)
            message = response.choices[0].message

            content = message.content or ""
            if strip_think:
                content = self._strip_thinking_tags(content)

            messages.append(
                {
                    "role": "assistant",
                    "content": content,
                    "tool_calls": message.tool_calls
                    if hasattr(message, "tool_calls") and message.tool_calls
                    else None,
                }
            )

            if not message.tool_calls:
                final_content = content
                print(f"\n🔍 DEBUG: Final LLM response (first 1000 chars):")
                print(f"{final_content[:1000]}")
                if len(final_content) > 1000:
                    print(
                        f"... (truncated, total length: {len(final_content)} chars)"
                    )
                print()

                missing_tags = []
                if "<response>" not in final_content:
                    missing_tags.append("<response>")
                if "<summary>" not in final_content:
                    missing_tags.append("<summary>")
                if "<feedback>" not in final_content:
                    missing_tags.append("<feedback>")

                if missing_tags:
                    print(
                        f"⚠️  LLM response missing required tags: {', '.join(missing_tags)}"
                    )
                    print(
                        f"   Forcing retry (iteration {iteration}/{self.max_iterations})..."
                    )
                    messages.append(
                        {
                            "role": "user",
                            "content": f"ERROR: Your response is missing required tags: {', '.join(missing_tags)}. You MUST provide ALL THREE tags: <summary>, <feedback>, and <response>. Please provide your complete response now with all three tags.",
                        }
                    )
                    continue

                return final_content, tool_metrics

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error for tool {tool_name}")
                    print(f"   Arguments: {tool_call.function.arguments[:200]}...")
                    print(f"   Error: {e}")
                    raise

                print(f"🔧 Executing tool: {tool_name}")
                print(f"   Arguments: {json.dumps(tool_args, ensure_ascii=False)}")
                tool_start_ts = time.time()

                try:
                    tool_result = await self.mcp_session.call_tool(tool_name, tool_args)
                    tool_duration = time.time() - tool_start_ts
                    print(f"✅ Tool {tool_name} completed in {tool_duration:.2f}s")
                except Exception as e:
                    tool_duration = time.time() - tool_start_ts
                    error_type = type(e).__name__
                    error_msg = str(e)
                    print(f"❌ Tool {tool_name} failed after {tool_duration:.2f}s")
                    print(f"   Error: {error_type}: {error_msg}")
                    tool_result = {
                        "isError": True,
                        "content": [
                            {
                                "type": "text",
                                "text": f"ERROR: Tool execution failed\nType: {error_type}\nMessage: {error_msg}\n\nThis tool is not available or encountered an error. Please try a different approach.",
                            }
                        ],
                    }

                if tool_name not in tool_metrics:
                    tool_metrics[tool_name] = {"count": 0, "durations": [], "calls": []}
                tool_metrics[tool_name]["count"] += 1
                tool_metrics[tool_name]["durations"].append(tool_duration)
                tool_metrics[tool_name]["calls"].append(
                    {
                        "args": tool_args,
                        "duration": tool_duration,
                        "timestamp": tool_start_ts,
                    }
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(tool_result),
                    }
                )

        # If we hit max iterations, find the last assistant message
        for msg in reversed(messages):
            if msg.get("role") == "assistant" and msg.get("content"):
                return msg["content"], tool_metrics
        return "", tool_metrics


# ============================================================================
# LangGraph Agent Loop
# ============================================================================


class LangGraphAgentLoop(BaseAgentLoop):
    """
    Agent loop implementation using LangGraph runtime.

    TODO: Implement LangGraph integration.
    This is a placeholder for future implementation.
    """

    def __init__(
        self,
        mcp_session: ClientSession,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        langgraph_url: str = None,
        **kwargs,
    ):
        """
        Initialize LangGraph agent loop.

        Args:
            mcp_session: MCP client session for tool execution
            system_prompt: System prompt for the agent
            langgraph_url: LangGraph runtime URL
            **kwargs: Additional LangGraph configuration
        """
        super().__init__(mcp_session, system_prompt)
        self.langgraph_url = langgraph_url or os.getenv("LANGGRAPH_URL")
        self.config = kwargs

    async def run(
        self,
        prompt: str,
        tools: List[Dict[str, Any]] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Execute LangGraph agent loop.

        Args:
            prompt: User prompt/task
            tools: List of tool definitions

        Returns:
            Tuple of (response_text, tool_metrics)
        """
        # TODO: Implement LangGraph runtime integration
        # This should:
        # 1. Convert tools to LangGraph format
        # 2. Create a LangGraph agent with the tools
        # 3. Execute the agent with the prompt
        # 4. Track tool execution metrics
        # 5. Return response and metrics in the same format as AzureOpenAIAgentLoop

        raise NotImplementedError(
            "LangGraph agent loop is not yet implemented. "
            "Please use AzureOpenAIAgentLoop for now."
        )
