# Agent Runtime Implementations

This directory contains concrete implementations of agent runtimes that are **external** to the evaluation framework.

## 🚀 Quick Start - Add Your Own Agent in 3 Steps

**Want to integrate your own agent? It's super easy!**

1. **Copy the template**:
   ```bash
   cp agent_runtime/_template.py agent_runtime/my_agent.py
   ```

2. **Add the decorator** and implement your logic:
   ```python
   @AgentRegistry.register("my_agent")  # ← Just change this name
   class MyCustomAgent(BaseAgentLoop):
       # Implement __init__, run(), _execute_tool_call()
       # See _template.py for detailed guide
   ```

3. **Run it**:
   ```bash
   # Using CLI (recommended)
   aio-eval --agent my_agent

   # Or using main.py with environment variable
   export AGENT_TYPE=my_agent
   uv run main.py
   ```

That's it! The framework will **auto-discover** your agent. No need to modify `main.py` or any other files! 🎉

