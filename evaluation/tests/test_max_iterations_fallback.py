"""
Unit tests for the max_iterations fallback behavior in agent loops.

Verifies that when max_iterations is reached, the agent returns the last
assistant message rather than the last message (which may be a tool response).
"""

import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Mock external dependencies before importing agent_loop
sys.modules.setdefault("mcp", MagicMock())
sys.modules.setdefault("openai", MagicMock())

from agent_loop import AzureOpenAIAgentLoop, OpenAIAgentLoop


class _FakeChoice:
    """Minimal stand-in for ``response.choices[0]``."""

    def __init__(self, content, tool_calls=None):
        self.message = MagicMock()
        self.message.content = content
        self.message.tool_calls = tool_calls


class _FakeResponse:
    def __init__(self, content, tool_calls=None):
        self.choices = [_FakeChoice(content, tool_calls)]


class _FakeToolCall:
    def __init__(self, name, arguments):
        self.id = "call_test123"
        self.function = MagicMock()
        self.function.name = name
        self.function.arguments = arguments


class TestMaxIterationsFallback(unittest.IsolatedAsyncioTestCase):
    """When max_iterations is exhausted the loop must return the last *assistant* message."""

    @patch("agent_loop.OpenAI")
    async def test_openai_returns_last_assistant_message(self, mock_openai_cls):
        """OpenAIAgentLoop should return the last assistant content, not a tool response."""
        session = AsyncMock()

        # Simulate: every iteration the model calls a tool (never finishes naturally)
        tool_call = _FakeToolCall("some_tool", '{"arg": "val"}')
        tool_response = _FakeResponse("I am working on it...", tool_calls=[tool_call])

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = tool_response
        mock_openai_cls.return_value = mock_client

        # MCP tool execution returns a dummy result
        session.call_tool = AsyncMock(return_value={"content": [{"type": "text", "text": "tool output"}]})

        loop = OpenAIAgentLoop(
            mcp_session=session,
            max_iterations=2,
            api_key="test",
        )

        result_text, metrics = await loop.run(
            "test prompt",
            tools=[{"type": "function", "function": {"name": "some_tool", "parameters": {}}}],
        )

        # The result should be the assistant's content, not the tool response string
        self.assertEqual(result_text, "I am working on it...")
        # It should NOT be the stringified tool result
        self.assertNotIn("tool output", result_text)

    @patch("agent_loop.AzureOpenAI")
    async def test_azure_returns_last_assistant_message(self, mock_azure_cls):
        """AzureOpenAIAgentLoop should return the last assistant content, not a tool response."""
        session = AsyncMock()

        tool_call = _FakeToolCall("another_tool", '{}')
        tool_response = _FakeResponse("Processing your request...", tool_calls=[tool_call])

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = tool_response
        mock_azure_cls.return_value = mock_client

        session.call_tool = AsyncMock(return_value={"content": [{"type": "text", "text": "result"}]})

        loop = AzureOpenAIAgentLoop(
            mcp_session=session,
            max_iterations=2,
            azure_endpoint="https://test.openai.azure.com",
            azure_api_key="test",
            azure_deployment="gpt-4",
        )

        result_text, metrics = await loop.run(
            "test prompt",
            tools=[{"type": "function", "function": {"name": "another_tool", "parameters": {}}}],
        )

        self.assertEqual(result_text, "Processing your request...")

    @patch("agent_loop.OpenAI")
    async def test_returns_empty_when_no_assistant_message(self, mock_openai_cls):
        """If somehow there are no assistant messages, return empty string."""
        session = AsyncMock()

        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        loop = OpenAIAgentLoop(
            mcp_session=session,
            max_iterations=0,  # Will never enter the while loop
            api_key="test",
        )

        result_text, metrics = await loop.run("test prompt")

        # With 0 iterations, messages only has system+user, no assistant
        self.assertEqual(result_text, "")


if __name__ == "__main__":
    unittest.main()
