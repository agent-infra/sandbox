"""
Evaluation Runner

Orchestrates the evaluation process by coordinating all components.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional


from aio_sandbox_eval.agent import AgentRegistry, BaseAgentLoop
from aio_sandbox_eval.services.dataset_parser import XMLDatasetParser
from aio_sandbox_eval.services.evaluator import TaskEvaluator
from aio_sandbox_eval.services.mcp_client import MCPClient
from aio_sandbox_eval.services.report import ReportGenerator
from aio_sandbox_eval.services.uploader import SandboxUploader


class EvaluationRunner:
    """
    Coordinates the evaluation workflow.

    Responsibilities:
    - Parse evaluation dataset
    - Initialize MCP client and get tools
    - Upload test files
    - Run task evaluations
    - Generate reports
    """

    def __init__(
        self,
        mcp_server_url: str = None,
        agent_type: str = None,
        agent_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize evaluation runner.

        Args:
            mcp_server_url: Optional MCP server URL
            agent_type: Agent runtime type ("openai", "langchain_tool_calling", "langchain_react", "anthropic")
            agent_config: Additional configuration for the agent (model_name, temperature, etc.)
        """
        self.mcp_server_url = mcp_server_url
        self.agent_type = agent_type or os.getenv("AGENT_TYPE", "openai")
        self.agent_config = agent_config or {}
        self.parser = XMLDatasetParser()
        self.evaluator = TaskEvaluator()
        self.report_generator = ReportGenerator()

    async def run(self, eval_path: str) -> str:
        """
        Run complete evaluation workflow.

        Args:
            eval_path: Path to XML evaluation file

        Returns:
            Markdown evaluation report

        Raises:
            Exception: If evaluation fails
        """
        print("🚀 Starting Evaluation")

        eval_file = Path(eval_path)

        tasks = self.parser.parse(eval_file)
        print(f"📋 Loaded {len(tasks)} evaluation tasks")

        if self.mcp_server_url:
            async with MCPClient(self.mcp_server_url) as mcp_client:
                uploader = SandboxUploader(mcp_client)
                await uploader.upload_test_files(eval_file)

                tools = await mcp_client.get_tools()
                print(f"✅ Retrieved {len(tools)} tools from MCP server")

                return await self._run_evaluation(tasks, tools, mcp_client.session)
        else:
            return await self._run_evaluation(tasks, [], None)

    async def _run_evaluation(
        self,
        tasks: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        mcp_session,
    ) -> str:
        """
        Run evaluation with given tasks and tools.

        Args:
            tasks: List of task definitions
            tools: List of available tools
            mcp_session: MCP session (may be None)

        Returns:
            Markdown evaluation report
        """
        agent = self._create_agent(mcp_session)
        print(f"🤖 Using agent: {agent.__class__.__name__} (type: {self.agent_type})")

        model_name = self.agent_config.get("model_name", "gpt-4")
        temperature = self.agent_config.get("temperature", 0.0)

        results = []
        for i, task in enumerate(tasks):
            print(f"Processing task {i + 1}/{len(tasks)}")
            result = await self.evaluator.evaluate(task, agent, tools, i)
            results.append(result)

        report = self.report_generator.generate(
            tasks,
            results,
            agent_type=self.agent_type,
            model_name=model_name,
            temperature=temperature,
        )

        return report

    def _create_agent(self, mcp_session) -> BaseAgentLoop:
        """
        Create agent instance based on configuration.

        Uses AgentRegistry to instantiate the agent, which allows
        users to register custom agent implementations without modifying
        this code.

        Args:
            mcp_session: MCP session (may be None)

        Returns:
            Agent instance

        Raises:
            ValueError: If agent_type is not registered
        """
        return AgentRegistry.create(
            agent_type=self.agent_type,
            mcp_session=mcp_session,
            model_id=self.agent_config.get(
                "model_id", os.getenv("OPENAI_MODEL_ID", "gpt-4")
            ),
            max_iterations=self.agent_config.get(
                "max_iterations", int(os.getenv("AGENT_MAX_ITERATIONS", "50"))
            ),
            base_url=self.agent_config.get(
                "base_url", os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            ),
            api_key=self.agent_config.get(
                "api_key", os.getenv("OPENAI_API_KEY", "your-api-key")
            ),
        )
