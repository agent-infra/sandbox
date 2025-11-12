"""
Dataset Parser Module

Responsible for parsing evaluation datasets from various formats (XML, JSON, etc.).
"""

import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List


class BaseDatasetParser(ABC):
    """Abstract base class for dataset parsers."""

    @abstractmethod
    def parse(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Parse evaluation dataset file.

        Args:
            file_path: Path to the dataset file

        Returns:
            List of evaluation tasks, each containing:
            - prompt: str - The task prompt
            - response: str - Expected response (or regex pattern)
        """
        pass


class XMLDatasetParser(BaseDatasetParser):
    """Parser for XML evaluation dataset files."""

    def parse(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Parse XML evaluation file and return list of evaluation tasks.

        Supports both <response> and <response_pattern> tags.
        Prefers <response> if both exist.

        Args:
            file_path: Path to XML evaluation file

        Returns:
            List of evaluation tasks with "prompt" and "response" keys
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            evaluations = []

            tasks = root.findall(".//task")
            for task in tasks:
                prompt_elem = task.find("prompt")
                response_elem = task.find("response")
                response_pattern_elem = task.find("response_pattern")

                # Support both <response> and <response_pattern>
                # Prefer <response> if both exist
                expected_response = None
                if response_elem is not None:
                    expected_response = (response_elem.text or "").strip()
                elif response_pattern_elem is not None:
                    expected_response = (response_pattern_elem.text or "").strip()

                if prompt_elem is not None and expected_response is not None:
                    eval_dict = {
                        "prompt": (prompt_elem.text or "").strip(),
                        "response": expected_response,
                    }
                    evaluations.append(eval_dict)

            return evaluations
        except Exception as e:
            print(f"Error parsing evaluation file {file_path}: {e}")
            return []
