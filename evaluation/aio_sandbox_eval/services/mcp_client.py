"""
MCP Client Manager

Manages MCP session lifecycle and tool retrieval.
Replaces global session variables with a clean class-based approach.
"""

import traceback
from typing import Any, Dict, List, Optional

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


class MCPClient:
    """
    Manages MCP session lifecycle.

    Usage:
        async with MCPClient(server_url) as client:
            tools = await client.get_tools()
            result = await client.call_tool("tool_name", {"arg": "value"})
    """

    def __init__(self, server_url: str):
        """
        Initialize MCP client.

        Args:
            server_url: URL of the MCP server
        """
        self.server_url = server_url
        self._session: Optional[ClientSession] = None
        self._streams = None

    async def __aenter__(self) -> "MCPClient":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

    async def connect(self) -> None:
        """
        Initialize connection to MCP server.

        Raises:
            Exception: If connection fails
        """
        try:
            self._streams = streamablehttp_client(self.server_url)
            read_stream, write_stream, _ = await self._streams.__aenter__()
            self._session = ClientSession(read_stream, write_stream)
            await self._session.__aenter__()
            await self._session.initialize()
            print(f"✅ MCP session initialized: {self.server_url}")
        except Exception as e:
            print(f"❌ Failed to initialize MCP session: {e}")
            traceback.print_exc()
            raise

    async def disconnect(self) -> None:
        """Cleanup MCP session and streams."""
        if self._session:
            try:
                await self._session.__aexit__(None, None, None)
            except Exception:
                pass
            self._session = None

        if self._streams:
            try:
                await self._streams.__aexit__(None, None, None)
            except Exception:
                pass
            self._streams = None

    async def get_tools(self) -> List[Dict[str, Any]]:
        """
        Retrieve tools from MCP server in OpenAI format.

        Returns:
            List of tool definitions compatible with OpenAI API

        Raises:
            RuntimeError: If session is not initialized
        """
        if not self._session:
            raise RuntimeError("MCP session not initialized. Call connect() first.")

        try:
            tools_response = await self._session.list_tools()
            print(f"🔍 Retrieved {len(tools_response.tools)} tools from MCP")

            # Convert MCP tools to OpenAI format
            openai_tools = []
            for tool in tools_response.tools:
                openai_tool = {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.inputSchema
                        if hasattr(tool, "inputSchema")
                        else {"type": "object", "properties": {}, "required": []},
                    },
                }
                openai_tools.append(openai_tool)
                print(f"  - {tool.name}")

            return openai_tools

        except Exception as e:
            print(f"❌ Error retrieving MCP tools: {e}")
            traceback.print_exc()
            return []

    async def call_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Any:
        """
        Call an MCP tool.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result

        Raises:
            RuntimeError: If session is not initialized
        """
        if not self._session:
            raise RuntimeError("MCP session not initialized. Call connect() first.")

        return await self._session.call_tool(tool_name, arguments=arguments)

    @property
    def session(self) -> Optional[ClientSession]:
        """Get the underlying MCP session."""
        return self._session
