"""
Custom Agent Template

Copy this file to create your own agent implementation.

Steps:
1. Copy this file: cp agent_runtime/_template.py agent_runtime/my_agent.py
2. Rename the class and update the @register decorator
3. Implement __init__ and run() (call_tool() has default implementation)
4. Run: uv run main.py --agent my_agent
"""

from typing import Any, Dict, List, override

from aio_sandbox_eval.agent.abc import BaseAgentLoop
from aio_sandbox_eval.agent.registry import AgentRegistry
from aio_sandbox_eval.agent.type import (
    AgentMessage,
    ToolDefinition,
    ToolExecutionError,
    ToolResult,
)


@AgentRegistry.register("my_agent")  # ← Change "my_agent" to your agent name
class MyCustomAgent(BaseAgentLoop):  # ← Change class name
    """
    Custom agent implementation.

    TODO: Add your agent description here.
    """

    def __init__(
        self,
        mcp_session,
        model_name: str = "gpt-4",
        temperature: float = 0.0,
        max_iterations: int = 50,
        **kwargs,  # Accept additional parameters for compatibility
    ):
        """
        Initialize your custom agent.

        Args:
            mcp_session: MCP client session for tool execution
            model_name: Model name to use
            temperature: LLM temperature
            max_iterations: Maximum number of agent iterations
            **kwargs: Additional parameters (ignored, for compatibility)
        """
        super().__init__()

        # Store required attributes
        self.mcp_session = mcp_session
        self.model_name = model_name
        self.temperature = temperature
        self.max_iterations = max_iterations

        # TODO: Initialize your LLM client or agent framework here
        # Example:
        # self.client = YourLLMClient(model=model_name, temperature=temperature)

    @override
    async def run(
        self,
        prompt: str,
        tools: List[ToolDefinition],
    ) -> List[AgentMessage]:
        """
        Execute your agent loop.

        This is the main method where you implement your agent logic.

        Args:
            prompt: User prompt/task to execute
            tools: List of tool definitions in OpenAI function calling format

        Returns:
            List of conversation messages (system, user, assistant, tool)

        Example flow:
            1. Initialize conversation with system prompt and user prompt
            2. Loop:
               a. Call LLM with messages and tools
               b. If no tool calls, return messages
               c. Execute tool calls via self.call_tool()
               d. Add tool results to messages
            3. Return all messages
        """
        # Initialize conversation
        messages = [
            AgentMessage(role="system", content=self.system_prompt),
            AgentMessage(role="user", content=prompt),
        ]

        # TODO: Implement your agent loop here
        # This is a basic template - customize based on your agent framework

        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1

            # TODO: Call your LLM/agent framework
            # Example:
            # response = await self.client.generate(messages, tools)

            # TODO: Add assistant message to conversation
            # messages.append(AgentMessage(role="assistant", content=response.content))

            # TODO: Check for tool calls
            # if response.has_tool_calls():
            #     for tool_call in response.tool_calls:
            #         # Execute tool (metrics auto-tracked!)
            #         result = await self.call_tool(
            #             tool_name=tool_call.name,
            #             arguments=tool_call.arguments
            #         )
            #         # Add tool result to messages
            #         messages.append(AgentMessage(
            #             role="tool",
            #             content=str(result),
            #             tool_call_id=tool_call.id,
            #             name=tool_call.name,
            #         ))
            # else:
            #     # No tool calls - done
            #     break

            # REMOVE THIS: Placeholder return for template
            break

        return messages

    # =========================================================================
    # call_tool() - Optional Override
    # =========================================================================
    #
    # BaseAgentLoop provides a default implementation of call_tool() that
    # directly calls self.mcp_session.call_tool().
    #
    # You DON'T need to implement call_tool() unless you need custom behavior:
    #
    # ✓ When to override:
    #   - Adding retry logic for failed tool calls
    #   - Implementing tool result caching
    #   - Custom error handling or transformation
    #   - Tool call preprocessing/postprocessing
    #
    # ✗ When NOT to override:
    #   - Standard MCP tool execution (default works fine!)
    #   - No special requirements
    #
    # Example override (uncomment if needed):
    #
    # @override
    # async def call_tool(
    #     self,
    #     tool_name: str,
    #     arguments: Dict[str, Any],
    # ) -> ToolResult:
    #     """Custom tool execution with retry logic."""
    #     max_retries = 3
    #     for attempt in range(max_retries):
    #         try:
    #             result = await self.mcp_session.call_tool(tool_name, arguments=arguments)
    #             if hasattr(result, "model_dump"):
    #                 return result.model_dump()
    #             return result
    #         except Exception as e:
    #             if attempt == max_retries - 1:
    #                 raise ToolExecutionError(f"Tool {tool_name} failed after {max_retries} retries: {e}")
    #             await asyncio.sleep(2 ** attempt)  # Exponential backoff
    # =========================================================================


# ==============================================================================
# Usage Example
# ==============================================================================
"""
After implementing your agent:

1. Test locally:
   ```python
   from aio_sandbox_eval import AgentRegistry

   # Auto-discovery will find and register your agent
   AgentRegistry.auto_discover("agent_runtime")

   # Use your agent
   agent = AgentRegistry.create(
       agent_type="my_agent",
       mcp_session=session,
       model_name="gpt-4",
   )
   messages = await agent.run(prompt, tools)
   ```

2. Use with CLI or main.py:
   ```bash
   # Using CLI (recommended)
   aio-eval --agent my_agent --eval basic

   # Or using main.py with environment variable
   export AGENT_TYPE=my_agent
   uv run main.py
   ```

3. Check registered agents:
   ```bash
   python -c "from aio_sandbox_eval import AgentRegistry; \
              AgentRegistry.auto_discover('agent_runtime'); \
              print(AgentRegistry.list_agents())"
   ```
"""
