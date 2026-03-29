"""Integration tests for MiniMax via OpenAIAgentLoop.

These tests require a live MiniMax API key (MINIMAX_API_KEY env var).
They are skipped automatically when the key is not set.

Run:
    MINIMAX_API_KEY=your_key python -m pytest evaluation/tests/test_minimax_integration.py -v
"""

import os
import sys
import unittest

# Ensure the evaluation package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")

skip_reason = "MINIMAX_API_KEY not set — skipping live integration tests"


@unittest.skipUnless(MINIMAX_API_KEY, skip_reason)
class TestMiniMaxLiveCompletion(unittest.TestCase):
    """Smoke-test that MiniMax API can be reached via OpenAI SDK."""

    def test_simple_completion(self):
        """A basic chat completion should return a non-empty string."""
        from openai import OpenAI

        client = OpenAI(
            api_key=MINIMAX_API_KEY,
            base_url="https://api.minimax.io/v1",
        )
        response = client.chat.completions.create(
            model="MiniMax-M2.7",
            messages=[{"role": "user", "content": "Reply with exactly: pong"}],
            temperature=0.01,
            max_tokens=16,
        )
        text = response.choices[0].message.content or ""
        self.assertTrue(len(text) > 0, "Expected non-empty response from MiniMax")

    def test_function_calling(self):
        """MiniMax should be able to produce tool_calls."""
        from openai import OpenAI

        client = OpenAI(
            api_key=MINIMAX_API_KEY,
            base_url="https://api.minimax.io/v1",
        )
        response = client.chat.completions.create(
            model="MiniMax-M2.7",
            messages=[{"role": "user", "content": "What is 2 + 3? Use the calculator tool."}],
            tools=[{
                "type": "function",
                "function": {
                    "name": "calculator",
                    "description": "Evaluate a math expression",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {"type": "string"},
                        },
                        "required": ["expression"],
                    },
                },
            }],
            temperature=0.01,
            max_tokens=128,
        )
        message = response.choices[0].message
        # The model should either call the tool or give a direct answer
        has_tool_call = message.tool_calls is not None and len(message.tool_calls) > 0
        has_content = message.content is not None and len(message.content) > 0
        self.assertTrue(
            has_tool_call or has_content,
            "Expected tool call or content from MiniMax function calling",
        )

    def test_m27_highspeed_model(self):
        """MiniMax-M2.7-highspeed should also work."""
        from openai import OpenAI

        client = OpenAI(
            api_key=MINIMAX_API_KEY,
            base_url="https://api.minimax.io/v1",
        )
        response = client.chat.completions.create(
            model="MiniMax-M2.7-highspeed",
            messages=[{"role": "user", "content": "Say hello"}],
            temperature=0.01,
            max_tokens=16,
        )
        text = response.choices[0].message.content or ""
        self.assertTrue(len(text) > 0)


@unittest.skipUnless(MINIMAX_API_KEY, skip_reason)
class TestOpenAIAgentLoopWithMiniMax(unittest.IsolatedAsyncioTestCase):
    """Test OpenAIAgentLoop end-to-end with MiniMax (no sandbox required)."""

    async def test_agent_loop_simple_prompt(self):
        """OpenAIAgentLoop should complete a simple prompt using MiniMax."""
        from unittest.mock import MagicMock
        from agent_loop import OpenAIAgentLoop

        # Use a mock MCP session since we're not testing tool execution
        session = MagicMock()

        loop = OpenAIAgentLoop(
            mcp_session=session,
            api_key=MINIMAX_API_KEY,
            base_url="https://api.minimax.io/v1",
            model="MiniMax-M2.7-highspeed",
            max_iterations=3,
        )

        response_text, metrics = await loop.run(
            "Reply with exactly these three XML tags and nothing else:\n"
            "<summary>test</summary>\n<feedback>test</feedback>\n<response>hello</response>"
        )
        self.assertIn("<response>", response_text)
        self.assertIn("</response>", response_text)


if __name__ == "__main__":
    unittest.main()
