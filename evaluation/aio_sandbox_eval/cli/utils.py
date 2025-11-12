"""
CLI utilities for evaluation framework.

Provides helper functions for:
- Environment variable loading
- Dataset file discovery and resolution
- Agent configuration building
- Report output path organization
"""

import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


def get_all_evaluation_files(dataset_dir: Optional[Path] = None) -> List[Path]:
    """
    Get all evaluation XML files from dataset directory.

    Args:
        dataset_dir: Dataset directory path. If None, uses default 'dataset' directory.

    Returns:
        Sorted list of evaluation XML file paths
    """
    if dataset_dir is None:
        dataset_dir = Path(__file__).parent.parent.parent / "dataset"

    return sorted(dataset_dir.glob("evaluation*.xml"))


def resolve_eval_file(eval_name: str, dataset_dir: Optional[Path] = None) -> Path:
    """
    Resolve evaluation file name to full path.

    Supports multiple input formats:
    - Short names: 'basic' -> 'dataset/evaluation_basic.xml'
    - Full names: 'evaluation_basic.xml' -> 'dataset/evaluation_basic.xml'
    - With extension: 'basic.xml' -> 'dataset/evaluation_basic.xml'
    - Default: 'evaluation.xml' -> 'dataset/evaluation.xml'

    Args:
        eval_name: Evaluation file name (short or full)
        dataset_dir: Dataset directory path. If None, uses default 'dataset' directory.

    Returns:
        Full path to evaluation XML file
    """
    if dataset_dir is None:
        dataset_dir = Path(__file__).parent.parent.parent / "dataset"

    if eval_name == "evaluation.xml":
        return dataset_dir / "evaluation.xml"

    eval_name = eval_name.replace(".xml", "")

    if eval_name.startswith("evaluation_"):
        eval_name = eval_name[12:]

    if eval_name == "evaluation" or eval_name == "":
        filename = "evaluation.xml"
    else:
        filename = f"evaluation_{eval_name}.xml"

    return dataset_dir / filename


def list_available_evaluations(
    dataset_dir: Optional[Path] = None,
) -> List[Tuple[str, str]]:
    """
    List all available evaluation files with their short names.

    Args:
        dataset_dir: Dataset directory path. If None, uses default 'dataset' directory.

    Returns:
        List of tuples: (short_name, filename)
    """
    if dataset_dir is None:
        dataset_dir = Path(__file__).parent.parent.parent / "dataset"

    results = []
    for file in sorted(dataset_dir.glob("evaluation*.xml")):
        short_name = file.stem.replace("evaluation_", "")
        if short_name == "evaluation":
            short_name = "evaluation"
        results.append((short_name, file.name))

    return results


def load_env_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables.

    Returns:
        Dictionary with environment configuration:
        - agent_type: Agent runtime type
        - model_name: Model name
        - temperature: Temperature value
        - max_iterations: Max iterations for agent loop
        - mcp_server_url: MCP server URL
    """
    return {
        "agent_type": os.getenv("AGENT_TYPE", "openai"),
        "model_name": os.getenv("OPENAI_MODEL_ID", "gpt-4"),
        "temperature": float(os.getenv("AGENT_TEMPERATURE", "0.0")),
        "max_iterations": int(os.getenv("AGENT_MAX_ITERATIONS", "50")),
        "mcp_server_url": os.getenv("MCP_SERVER_URL"),
    }


def build_agent_config(
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_iterations: Optional[int] = None,
    agent_type: Optional[str] = None,
) -> Tuple[str, Dict[str, Any]]:
    """
    Build agent configuration from CLI args and environment variables.

    CLI args take precedence over environment variables.

    Args:
        model: Model name override
        temperature: Temperature override
        max_iterations: Max iterations override
        agent_type: Agent type override

    Returns:
        Tuple of (agent_type, agent_config_dict)
    """
    env_config = load_env_config()

    final_agent_type = agent_type or env_config["agent_type"]

    agent_config = {}
    if model is not None:
        agent_config["model_name"] = model
    elif env_config["model_name"]:
        agent_config["model_name"] = env_config["model_name"]

    if temperature is not None:
        agent_config["temperature"] = temperature
    elif env_config["temperature"] is not None:
        agent_config["temperature"] = env_config["temperature"]

    if max_iterations is not None:
        agent_config["max_iterations"] = max_iterations
    elif env_config["max_iterations"]:
        agent_config["max_iterations"] = env_config["max_iterations"]

    return final_agent_type, agent_config


def create_report_output_path(
    agent_type: str,
    model_name: str,
    temperature: float,
    base_dir: Optional[Path] = None,
) -> Path:
    """
    Create organized output directory path for evaluation reports.

    Directory structure:
        result/
            YYYYMMDD/           # Date in UTC+8
                {agent_type}-{model_name}-{temperature}/
                    evaluation_basic.md
                    evaluation_browser.md
                    ...

    Args:
        agent_type: Agent runtime type
        model_name: Model name
        temperature: Temperature value
        base_dir: Base directory for results. If None, uses 'result' under project root.

    Returns:
        Path to output directory (created if not exists)
    """
    if base_dir is None:
        base_dir = Path(__file__).parent.parent.parent / "result"

    safe_model_name = model_name.replace("/", "-").replace(":", "-").replace(" ", "-")
    subdir_name = f"{agent_type}-{safe_model_name}-{temperature}"

    utc_plus_8 = timezone(timedelta(hours=8))
    date_str = datetime.now(utc_plus_8).strftime("%Y%m%d")

    output_dir = base_dir / date_str / subdir_name
    output_dir.mkdir(parents=True, exist_ok=True)

    return output_dir


def get_report_filename(eval_file_path: Path) -> str:
    """
    Generate report filename from evaluation file path.

    Args:
        eval_file_path: Path to evaluation XML file

    Returns:
        Report filename (e.g., 'evaluation_basic.md')
    """
    return f"{eval_file_path.stem}.md"


def print_config_summary(
    agent_type: str,
    agent_config: Dict[str, Any],
    mcp_url: Optional[str],
    eval_files: List[Path],
    output_dir: Path,
):
    """
    Print configuration summary for CLI.

    Args:
        agent_type: Agent runtime type
        agent_config: Agent configuration dictionary
        mcp_url: MCP server URL
        eval_files: List of evaluation files to run
        output_dir: Output directory for reports
    """
    print(f"🔍 MCP_SERVER_URL: {mcp_url}")
    print(f"🤖 Agent Type: {agent_type}")
    if agent_config:
        print(f"⚙️  Agent Config: {agent_config}")
    print(f"📁 Output Directory: {output_dir}")
    print(f"🚀 Running {len(eval_files)} evaluation file(s)")


def print_evaluation_progress(current: int, total: int, eval_file: Path):
    """
    Print evaluation progress for CLI.

    Args:
        current: Current file index (1-based)
        total: Total number of files
        eval_file: Current evaluation file
    """
    print(f"\n{'=' * 80}")
    print(f"📋 Processing [{current}/{total}]: {eval_file.name}")
    print(f"{'=' * 80}")


def print_evaluation_summary(successful: int, failed: int, total: int):
    """
    Print evaluation summary for CLI.

    Args:
        successful: Number of successful evaluations
        failed: Number of failed evaluations
        total: Total number of evaluations
    """
    print(f"\n{'=' * 80}")
    print(f"📊 Summary: {successful} successful, {failed} failed out of {total} total")
    print(f"{'=' * 80}")
