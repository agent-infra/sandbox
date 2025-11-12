"""
Sandbox File Uploader

Handles uploading of test files to sandbox environment.
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .mcp_client import MCPClient


class SandboxUploader:
    """
    Uploads files to sandbox environment.

    Responsibilities:
    - Upload files to sandbox /tmp directory
    - Determine which files to upload based on evaluation type
    - Handle upload errors gracefully
    """

    def __init__(self, mcp_client: "MCPClient"):
        """
        Initialize uploader.

        Args:
            mcp_client: Connected MCP client instance
        """
        self.mcp_client = mcp_client

    async def upload_file(
        self, local_path: Path, sandbox_path: str
    ) -> bool:
        """
        Upload a single file to sandbox.

        Args:
            local_path: Local file path to upload
            sandbox_path: Target path in sandbox (should be under /tmp)

        Returns:
            True if upload successful, False otherwise
        """
        try:
            if not local_path.exists():
                print(f"⚠️  Warning: {local_path} not found, skipping upload")
                return False

            with open(local_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            # Upload using MCP client
            await self.mcp_client.call_tool(
                "sandbox_file_operations",
                arguments={
                    "action": "write",
                    "path": sandbox_path,
                    "content": file_content,
                    "encoding": "utf-8",
                },
            )

            print(f"📤 Uploaded {local_path.name} to sandbox:{sandbox_path}")
            return True

        except Exception as e:
            print(f"⚠️  Failed to upload {local_path}: {e}")
            return False

    async def upload_test_files(self, eval_file: Path) -> bool:
        """
        Upload test files based on evaluation type.

        Determines which files to upload based on evaluation file name.

        Args:
            eval_file: Path to the evaluation XML file being run

        Returns:
            True if all required uploads successful, False otherwise
        """
        eval_file_name = eval_file.name
        base_dir = Path(__file__).parent.parent.parent  # Go up to evaluation/
        success = True

        # Upload main.py for collaboration and workflow tests
        if "collaboration" in eval_file_name or "workflow" in eval_file_name:
            main_py_path = base_dir / "main.py"
            if not await self.upload_file(main_py_path, "/tmp/main.py"):
                success = False

        # Upload evaluation.xml for workflow tests
        if "workflow" in eval_file_name:
            # Try to find evaluation.xml in dataset directory
            eval_xml_path = base_dir / "dataset" / "evaluation.xml"
            if eval_xml_path.exists():
                if not await self.upload_file(
                    eval_xml_path, "/tmp/evaluation.xml"
                ):
                    success = False
            else:
                # If evaluation.xml doesn't exist, use the current eval file
                if not await self.upload_file(eval_file, "/tmp/evaluation.xml"):
                    success = False

        return success
