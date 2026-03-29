"""Unit tests for the OpenAIAgentLoop in agent_loop.py."""

import json
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Ensure the evaluation package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent_loop import (
    OpenAIAgentLoop,
    AzureOpenAIAgentLoop,
    BaseAgentLoop,
    DEFAULT_SYSTEM_PROMPT,
)


class TestOpenAIAgentLoopInit(unittest.TestCase):
    """Test OpenAIAgentLoop initialisation and configuration."""

    @patch("agent_loop.OpenAI")
    def test_default_init(self, mock_openai_cls):
        """Constructor should accept a bare MCP session and set sensible defaults."""
        session = MagicMock()
        loop = OpenAIAgentLoop(mcp_session=session)

        self.assertIsNotNone(loop.client)
        self.assertEqual(loop.model, os.getenv("OPENAI_MODEL", "gpt-4"))
        self.assertEqual(loop.max_iterations, 50)
        self.assertIsNone(loop.temperature)

    @patch("agent_loop.OpenAI")
    def test_custom_base_url(self, mock_openai_cls):
        """Constructor should forward base_url to the OpenAI client."""
        session = MagicMock()
        OpenAIAgentLoop(
            mcp_session=session,
            api_key="test-key",
            base_url="https://api.minimax.io/v1",
            model="MiniMax-M2.7",
        )
        mock_openai_cls.assert_called_once_with(
            api_key="test-key",
            base_url="https://api.minimax.io/v1",
        )

    @patch("agent_loop.OpenAI")
    def test_env_fallback(self, mock_openai_cls):
        """Constructor should read OPENAI_* env vars when explicit args are omitted."""
        session = MagicMock()
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "env-key",
            "OPENAI_BASE_URL": "https://env.example.com/v1",
            "OPENAI_MODEL": "env-model",
        }):
            loop = OpenAIAgentLoop(mcp_session=session)
            self.assertEqual(loop.api_key, "env-key")
            self.assertEqual(loop.base_url, "https://env.example.com/v1")
            self.assertEqual(loop.model, "env-model")

    @patch("agent_loop.OpenAI")
    def test_is_base_agent_loop(self, mock_openai_cls):
        """OpenAIAgentLoop must be a subclass of BaseAgentLoop."""
        self.assertTrue(issubclass(OpenAIAgentLoop, BaseAgentLoop))


class TestTemperatureClamping(unittest.TestCase):
    """Test MiniMax-specific temperature > 0 constraint."""

    @patch("agent_loop.OpenAI")
    def test_minimax_clamps_zero(self, mock_openai_cls):
        """For MiniMax models, temperature=0 should be clamped to 0.01."""
        session = MagicMock()
        loop = OpenAIAgentLoop(
            mcp_session=session,
            model="MiniMax-M2.7",
            temperature=0.0,
        )
        self.assertGreater(loop._effective_temperature(), 0)
        self.assertAlmostEqual(loop._effective_temperature(), 0.01)

    @patch("agent_loop.OpenAI")
    def test_minimax_preserves_nonzero(self, mock_openai_cls):
        """Non-zero temperatures should pass through unchanged."""
        session = MagicMock()
        loop = OpenAIAgentLoop(
            mcp_session=session,
            model="MiniMax-M2.5",
            temperature=0.7,
        )
        self.assertAlmostEqual(loop._effective_temperature(), 0.7)

    @patch("agent_loop.OpenAI")
    def test_non_minimax_allows_zero(self, mock_openai_cls):
        """Non-MiniMax models should allow temperature=0."""
        session = MagicMock()
        loop = OpenAIAgentLoop(
            mcp_session=session,
            model="gpt-4",
            temperature=0.0,
        )
        self.assertAlmostEqual(loop._effective_temperature(), 0.0)

    @patch("agent_loop.OpenAI")
    def test_none_temperature(self, mock_openai_cls):
        """If temperature is None, _effective_temperature should return None."""
        session = MagicMock()
        loop = OpenAIAgentLoop(
            mcp_session=session,
            model="MiniMax-M2.7",
            temperature=None,
        )
        self.assertIsNone(loop._effective_temperature())


class TestThinkingTagStrip(unittest.TestCase):
    """Test <think> tag removal for MiniMax models."""

    def test_strips_thinking_tags(self):
        text = "<think>internal reasoning</think>\nActual response"
        result = OpenAIAgentLoop._strip_thinking_tags(text)
        self.assertEqual(result, "Actual response")

    def test_strips_multiline_thinking(self):
        text = "<think>\nstep 1\nstep 2\n</think>\n\nFinal answer"
        result = OpenAIAgentLoop._strip_thinking_tags(text)
        self.assertEqual(result, "Final answer")

    def test_preserves_normal_text(self):
        text = "No thinking tags here"
        result = OpenAIAgentLoop._strip_thinking_tags(text)
        self.assertEqual(result, "No thinking tags here")

    def test_strips_multiple_think_blocks(self):
        text = "<think>a</think>Hello <think>b</think>World"
        result = OpenAIAgentLoop._strip_thinking_tags(text)
        self.assertEqual(result, "Hello World")


class TestOpenAIAgentLoopRun(unittest.IsolatedAsyncioTestCase):
    """Test the run() method with mocked OpenAI client."""

    @patch("agent_loop.OpenAI")
    async def test_simple_response_no_tools(self, mock_openai_cls):
        """Agent should return LLM text when no tool calls are made."""
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        # Simulate an LLM response with all required tags
        mock_message = MagicMock()
        mock_message.content = (
            "<summary>Did nothing</summary>\n"
            "<feedback>No feedback</feedback>\n"
            "<response>42</response>"
        )
        mock_message.tool_calls = None

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=mock_message)]
        mock_client.chat.completions.create.return_value = mock_response

        session = MagicMock()
        loop = OpenAIAgentLoop(
            mcp_session=session,
            model="MiniMax-M2.7",
            api_key="test",
        )

        response_text, metrics = await loop.run("what is 6*7?")
        self.assertIn("<response>42</response>", response_text)
        self.assertEqual(metrics, {})

    @patch("agent_loop.OpenAI")
    async def test_tool_call_flow(self, mock_openai_cls):
        """Agent should execute tool calls and feed results back to the LLM."""
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        # First response: tool call
        tool_call = MagicMock()
        tool_call.function.name = "run_code"
        tool_call.function.arguments = json.dumps({"code": "print(1+1)"})
        tool_call.id = "call_123"

        msg1 = MagicMock()
        msg1.content = ""
        msg1.tool_calls = [tool_call]

        # Second response: final answer
        msg2 = MagicMock()
        msg2.content = (
            "<summary>Ran code</summary>\n"
            "<feedback>Good</feedback>\n"
            "<response>2</response>"
        )
        msg2.tool_calls = None

        mock_client.chat.completions.create.side_effect = [
            MagicMock(choices=[MagicMock(message=msg1)]),
            MagicMock(choices=[MagicMock(message=msg2)]),
        ]

        session = MagicMock()
        session.call_tool = AsyncMock(return_value="result: 2")

        loop = OpenAIAgentLoop(
            mcp_session=session,
            model="gpt-4",
            api_key="test",
        )

        response_text, metrics = await loop.run("calculate 1+1", tools=[{"type": "function", "function": {"name": "run_code"}}])
        self.assertIn("2", response_text)
        self.assertIn("run_code", metrics)
        self.assertEqual(metrics["run_code"]["count"], 1)

    @patch("agent_loop.OpenAI")
    async def test_minimax_strips_think_tags_in_response(self, mock_openai_cls):
        """MiniMax models should have <think> tags stripped from content."""
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        mock_message = MagicMock()
        mock_message.content = (
            "<think>internal thought</think>\n"
            "<summary>Done</summary>\n"
            "<feedback>OK</feedback>\n"
            "<response>hello</response>"
        )
        mock_message.tool_calls = None

        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=mock_message)]
        )

        session = MagicMock()
        loop = OpenAIAgentLoop(
            mcp_session=session,
            model="MiniMax-M2.7",
            api_key="test",
        )

        response_text, _ = await loop.run("say hello")
        self.assertNotIn("<think>", response_text)
        self.assertIn("<response>hello</response>", response_text)

    @patch("agent_loop.OpenAI")
    async def test_missing_tags_triggers_retry(self, mock_openai_cls):
        """When required tags are missing, the loop should retry."""
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        # First: missing tags; second: all tags present
        msg_bad = MagicMock()
        msg_bad.content = "Just some text without tags"
        msg_bad.tool_calls = None

        msg_good = MagicMock()
        msg_good.content = (
            "<summary>Done</summary>\n"
            "<feedback>Good</feedback>\n"
            "<response>final</response>"
        )
        msg_good.tool_calls = None

        mock_client.chat.completions.create.side_effect = [
            MagicMock(choices=[MagicMock(message=msg_bad)]),
            MagicMock(choices=[MagicMock(message=msg_good)]),
        ]

        session = MagicMock()
        loop = OpenAIAgentLoop(
            mcp_session=session, model="gpt-4", api_key="test",
        )

        response_text, _ = await loop.run("test")
        self.assertIn("<response>final</response>", response_text)
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)

    @patch("agent_loop.OpenAI")
    async def test_max_iterations_guard(self, mock_openai_cls):
        """Agent should stop after max_iterations even if LLM keeps calling tools."""
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        # Always returns a tool call
        tool_call = MagicMock()
        tool_call.function.name = "run_code"
        tool_call.function.arguments = json.dumps({"code": "x"})
        tool_call.id = "call_inf"

        msg = MagicMock()
        msg.content = ""
        msg.tool_calls = [tool_call]

        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=msg)]
        )

        session = MagicMock()
        session.call_tool = AsyncMock(return_value="ok")

        loop = OpenAIAgentLoop(
            mcp_session=session, model="gpt-4", api_key="test",
            max_iterations=3,
        )

        await loop.run("infinite loop")
        # Should have called create exactly 3 times (max_iterations)
        self.assertEqual(mock_client.chat.completions.create.call_count, 3)

    @patch("agent_loop.OpenAI")
    async def test_tool_error_handling(self, mock_openai_cls):
        """When a tool raises, the error should be fed back as tool result."""
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        tool_call = MagicMock()
        tool_call.function.name = "bad_tool"
        tool_call.function.arguments = json.dumps({})
        tool_call.id = "call_err"

        msg1 = MagicMock()
        msg1.content = ""
        msg1.tool_calls = [tool_call]

        msg2 = MagicMock()
        msg2.content = (
            "<summary>Tool failed</summary>\n"
            "<feedback>Error</feedback>\n"
            "<response>error handled</response>"
        )
        msg2.tool_calls = None

        mock_client.chat.completions.create.side_effect = [
            MagicMock(choices=[MagicMock(message=msg1)]),
            MagicMock(choices=[MagicMock(message=msg2)]),
        ]

        session = MagicMock()
        session.call_tool = AsyncMock(side_effect=RuntimeError("boom"))

        loop = OpenAIAgentLoop(
            mcp_session=session, model="gpt-4", api_key="test",
        )

        response_text, metrics = await loop.run("try bad tool")
        self.assertIn("error handled", response_text)
        self.assertEqual(metrics["bad_tool"]["count"], 1)


class TestAzureOpenAIAgentLoopUnchanged(unittest.TestCase):
    """Verify AzureOpenAIAgentLoop still works after refactoring."""

    @patch("agent_loop.AzureOpenAI")
    def test_azure_init(self, mock_azure_cls):
        session = MagicMock()
        loop = AzureOpenAIAgentLoop(mcp_session=session)
        self.assertTrue(issubclass(AzureOpenAIAgentLoop, BaseAgentLoop))
        self.assertIsNotNone(loop.client)


if __name__ == "__main__":
    unittest.main()
