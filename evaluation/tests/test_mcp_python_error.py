"""Run against a live sandbox by setting MCP_SERVER_URL to its /mcp endpoint."""

import json
import os
import unittest


@unittest.skipUnless(os.getenv("MCP_SERVER_URL"), "requires a live sandbox MCP_SERVER_URL")
class TestPythonExecutionError(unittest.IsolatedAsyncioTestCase):
    async def test_division_by_zero_reaches_tool_response(self):
        from mcp import ClientSession
        from mcp.client.streamable_http import streamablehttp_client

        api_key = os.getenv("SANDBOX_API_KEY")
        headers = {"X-AIO-API-Key": api_key} if api_key else None
        async with streamablehttp_client(os.environ["MCP_SERVER_URL"], headers=headers) as (reader, writer, _):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                result = await session.call_tool("sandbox_execute_code", {"language": "python", "code": "1 / 0"})

        payload = json.loads(result.content[0].text)
        self.assertEqual(payload["status"], "error")
        details = [payload.get("stderr") or "", *(payload.get("traceback") or [])]
        self.assertIn("ZeroDivisionError", "\n".join(details), payload)
