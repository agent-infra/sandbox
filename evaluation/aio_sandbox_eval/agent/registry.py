"""
Agent Registry and Factory

Provides a registration mechanism for agent implementations,
allowing users to easily extend with custom agents without modifying core code.
"""

import importlib
import pkgutil
from pathlib import Path
from typing import Any, Callable, Dict, Type

from .abc import BaseAgentLoop


class AgentRegistry:
    """
    Registry for agent implementations.

    Allows registration of custom agent classes that can be instantiated
    by name without modifying the core evaluation framework.

    Example:
        # Register a custom agent
        @AgentRegistry.register("my_custom_agent")
        class MyCustomAgent(BaseAgentLoop):
            def __init__(self, mcp_session, model_name="gpt-4", **kwargs):
                super().__init__()
                self.mcp_session = mcp_session
                self.model_name = model_name

        # Or register without decorator
        AgentRegistry.register("another_agent", AnotherAgentClass)
    """

    _registry: Dict[str, Type[BaseAgentLoop]] = {}

    @classmethod
    def register(cls, name: str, agent_class: Type[BaseAgentLoop] = None) -> Callable:
        """
        Register an agent implementation.

        Can be used as a decorator or called directly.

        Args:
            name: Agent type name (e.g., "openai", "langchain", "custom")
            agent_class: Agent class to register (optional if used as decorator)

        Returns:
            The agent class (for decorator usage)

        Raises:
            ValueError: If agent_class doesn't inherit from BaseAgentLoop

        Example:
            @AgentRegistry.register("my_agent")
            class MyAgent(BaseAgentLoop):
                pass
        """

        def decorator(agent_cls: Type[BaseAgentLoop]) -> Type[BaseAgentLoop]:
            if not issubclass(agent_cls, BaseAgentLoop):
                raise ValueError(
                    f"Agent class {agent_cls.__name__} must inherit from BaseAgentLoop"
                )
            cls._registry[name] = agent_cls
            return agent_cls

        if agent_class is None:
            return decorator
        else:
            return decorator(agent_class)

    @classmethod
    def create(
        cls,
        agent_type: str,
        *,
        mcp_session,
        model_id: str,
        max_iterations: int,
        base_url: str,
        api_key: str,
    ) -> BaseAgentLoop:
        """
        Create an agent instance by type name.

        Args:
            agent_type: Registered agent type name
            mcp_session: MCP session for tool execution
            model_id: Model identifier
            max_iterations: Maximum agent iterations
            base_url: API base URL (for OpenAI-compatible APIs)
            api_key: API key

        Returns:
            Initialized agent instance

        Raises:
            ValueError: If agent_type is not registered
        """
        if agent_type not in cls._registry:
            available = ", ".join(cls._registry.keys())
            raise ValueError(
                f"Unknown agent_type: {agent_type}. "
                f"Available types: {available}. "
                f"Register custom agents using AgentRegistry.register()"
            )

        agent_class = cls._registry[agent_type]
        return agent_class(
            mcp_session=mcp_session,
            model_id=model_id,
            max_iterations=max_iterations,
            base_url=base_url,
            api_key=api_key,
        )

    @classmethod
    def list_agents(cls) -> list[str]:
        """
        List all registered agent types.

        Returns:
            List of registered agent type names
        """
        return list(cls._registry.keys())

    @classmethod
    def get_agent_class(cls, agent_type: str) -> Type[BaseAgentLoop]:
        """
        Get the agent class for a given type.

        Args:
            agent_type: Registered agent type name

        Returns:
            Agent class

        Raises:
            ValueError: If agent_type is not registered
        """
        if agent_type not in cls._registry:
            raise ValueError(f"Unknown agent_type: {agent_type}")
        return cls._registry[agent_type]

    @classmethod
    def auto_discover(cls, package_path: str = "agent_runtime") -> None:
        """
        Automatically discover and import agent implementations from a package.

        This method scans the specified package directory for Python modules,
        imports them, and any classes decorated with @AgentRegistry.register
        will be automatically registered.

        Args:
            package_path: Path to the package containing agent implementations.
                         Can be a package name (e.g., "agent_runtime") or absolute path.

        Example:
            # In main.py, replace manual registration with:
            AgentRegistry.auto_discover("agent_runtime")

            # In agent implementation files:
            @AgentRegistry.register("openai")
            class OpenAISDKAgentLoop(BaseAgentLoop):
                pass
        """
        import sys

        # Determine the package directory
        package_dir = None
        is_package = False

        try:
            # Try to import as a package name first
            package = importlib.import_module(package_path)
            if hasattr(package, "__file__") and package.__file__:
                package_dir = Path(package.__file__).parent
                is_package = True
        except ImportError:
            pass

        # If not a package, try as a relative/absolute path
        if package_dir is None:
            candidate = Path(package_path)
            if not candidate.is_absolute():
                # Try relative to current working directory
                candidate = Path.cwd() / candidate

            if candidate.exists() and candidate.is_dir():
                package_dir = candidate
                # Add parent to sys.path if needed
                parent = str(package_dir.parent)
                if parent not in sys.path:
                    sys.path.insert(0, parent)
            else:
                print(f"⚠️  Agent discovery: package path not found: {package_path}")
                return

        # Scan for Python modules
        discovered_count = 0
        for finder, name, ispkg in pkgutil.walk_packages([str(package_dir)]):
            if name.startswith("_"):  # Skip private modules
                continue

            # Build module name
            if is_package:
                module_name = f"{package_path}.{name}"
            else:
                # Use the directory name as package name
                module_name = f"{package_dir.name}.{name}"

            try:
                # Import the module (this will trigger @register decorators)
                importlib.import_module(module_name)
                discovered_count += 1
            except ImportError as e:
                # Some modules might have optional dependencies (e.g., langchain)
                # Print warning but continue
                print(f"⚠️  Agent discovery: could not import {module_name}: {e}")
                continue

        print(
            f"✅ Agent discovery complete: scanned {discovered_count} modules, "
            f"registered {len(cls._registry)} agents: {', '.join(cls.list_agents())}"
        )
