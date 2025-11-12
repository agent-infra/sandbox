"""
OpenAI Agent Loop Implementation

Implements the BaseAgentLoop interface using OpenAI's Chat Completions API.
"""

import json
import os
from typing import Any, Dict, List, Optional, override

from openai import AsyncOpenAI

from aio_sandbox_eval.agent.abc import BaseAgentLoop
from aio_sandbox_eval.agent.registry import AgentRegistry
from aio_sandbox_eval.agent.type import (
    AgentMessage,
    LLMCallError,
    LLMResponse,
    ToolDefinition,
    ToolExecutionError,
    ToolResult,
)


@AgentRegistry.register("openai")
class OpenAISDKAgentLoop(BaseAgentLoop):
    """
    Agent loop implementation using OpenAI's Chat Completions API.

    Features:
    - Automatic tool calling loop
    - Tool execution metrics tracking
    - Response validation
    - Error handling and retry logic
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
        Initialize OpenAI agent loop.

        Args:
            mcp_session: MCP client session for tool execution
            model_id: Model ID to use
            max_iterations: Maximum number of agent loop iterations
            base_url: OpenAI API base URL
            api_key: OpenAI API key
        """
        super().__init__(
            mcp_session=mcp_session,
            model_id=model_id,
            max_iterations=max_iterations,
            base_url=base_url,
            api_key=api_key,
        )

        # OpenAI client
        self.client = AsyncOpenAI(
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
        Execute OpenAI agent loop.

        Args:
            prompt: User prompt/task
            tools: List of tool definitions in OpenAI function calling format

        Returns:
            List of conversation messages
        """
        # Initialize conversation
        messages = [
            AgentMessage(role="system", content=self.system_prompt),
            AgentMessage(role="user", content=prompt),
        ]

        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1

            # Call OpenAI API
            try:
                response = await self._call_openai(messages, tools)
            except Exception as e:
                raise LLMCallError(f"LLM call failed: {e}") from e

            # Extract message from Pydantic model
            message = response.choices[0].message

            # Add assistant message to conversation
            messages.append(
                AgentMessage(
                    role="assistant",
                    content=message.content,
                    tool_calls=message.tool_calls,
                )
            )

            # Check if we're done (no tool calls)
            tool_calls = message.tool_calls
            if not tool_calls:
                final_content = message.content or ""

                # Validate required tags
                missing_tags = self._validate_response_tags(final_content)
                if missing_tags:
                    print(
                        f"⚠️  LLM response missing required tags: {', '.join(missing_tags)}"
                    )
                    print(
                        f"   Forcing retry (iteration {iteration}/{self.max_iterations})..."
                    )

                    # Add error message to force retry
                    messages.append(
                        AgentMessage(
                            role="user",
                            content=f"ERROR: Your response is missing required tags: {', '.join(missing_tags)}. You MUST provide ALL THREE tags: <summary>, <feedback>, and <response>. Please provide your complete response now with all three tags.",
                        )
                    )
                    continue

                # Done - return all messages
                return messages

            # Execute tool calls
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_call_id = tool_call.id

                # Parse arguments
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error for tool {tool_name}: {e}")
                    tool_args = {}

                # Execute tool (metrics tracked automatically by decorator)
                try:
                    result = await self.call_tool(tool_name, tool_args)
                    result_str = json.dumps(result, ensure_ascii=False)
                except Exception as e:
                    print(f"❌ Tool execution error for {tool_name}: {e}")
                    result_str = f"ERROR: {str(e)}"

                # Add tool result to conversation
                messages.append(
                    AgentMessage(
                        role="tool",
                        content=result_str,
                        tool_call_id=tool_call_id,
                        name=tool_name,
                    )
                )

        # Max iterations reached
        print(f"⚠️  Max iterations ({self.max_iterations}) reached without completion")
        # Add error message as last assistant message
        messages.append(
            AgentMessage(role="assistant", content="ERROR: Max iterations reached")
        )
        return messages

    async def _call_openai(
        self,
        messages: List[AgentMessage],
        tools: Optional[List[ToolDefinition]] = None,
    ) -> LLMResponse:
        """
        Call OpenAI Chat Completions API.

        Args:
            messages: Conversation history as AgentMessage objects
            tools: Available tools in OpenAI function calling format

        Returns:
            ChatCompletion Pydantic model from OpenAI SDK
        """
        # Format messages to OpenAI format
        formatted_messages = self._format_messages(messages)

        # Build request kwargs
        kwargs = {
            "model": self.model_id,
            "messages": formatted_messages,
            "max_tokens": 4096,
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        # Make API call (async)
        response = await self.client.chat.completions.create(**kwargs)

        # Return ChatCompletion (Pydantic model) directly
        return response

    def _validate_response_tags(self, content: str) -> List[str]:
        """
        Validate that response contains required tags.

        Args:
            content: Response content

        Returns:
            List of missing tag names
        """
        missing = []
        required_tags = ["response", "summary", "feedback"]

        for tag in required_tags:
            if f"<{tag}>" not in content:
                missing.append(f"<{tag}>")

        return missing

    def _format_messages(self, messages: List[AgentMessage]) -> List[Dict[str, Any]]:
        """
        Convert AgentMessage list to OpenAI format.

        Args:
            messages: List of AgentMessage objects

        Returns:
            List of message dicts in OpenAI format
        """
        formatted = []
        for msg in messages:
            message_dict = {"role": msg.role}

            if msg.content:
                message_dict["content"] = msg.content

            if msg.name:
                message_dict["name"] = msg.name

            if msg.tool_calls:
                message_dict["tool_calls"] = msg.tool_calls

            if msg.tool_call_id:
                message_dict["tool_call_id"] = msg.tool_call_id

            formatted.append(message_dict)

        return formatted
