"""AIO Sandbox backend for LangChain DeepAgents.

Implements the DeepAgents BaseSandbox protocol using the agent-sandbox SDK.
All operations call the SDK APIs directly (file API for file ops, shell API
for execute/grep), following the same pattern as the eino aiosandbox-backend.
"""

from __future__ import annotations

import base64
import uuid

from agent_sandbox import Sandbox as SandboxClient
from deepagents.backends.protocol import (
    EditResult,
    ExecuteResponse,
    FileDownloadResponse,
    FileInfo,
    FileUploadResponse,
    GrepMatch,
    WriteResult,
)
from deepagents.backends.sandbox import BaseSandbox


class AIOSandboxBackend(BaseSandbox):
    """DeepAgents sandbox backend powered by AIO Sandbox.

    All methods call the sandbox SDK APIs directly:
    - File ops (read/write/edit/ls/glob) → file API
    - Search (grep) → shell API (single-line command, clean output)
    - Command execution → shell API (persistent session)

    Usage:
        from agent_sandbox import Sandbox
        from sandbox_backend import AIOSandboxBackend

        client = Sandbox(base_url="http://localhost:8080")
        backend = AIOSandboxBackend(client)

        agent = create_deep_agent(
            model=...,
            backend=backend,
        )
    """

    def __init__(
        self,
        client: SandboxClient,
        *,
        working_dir: str = "/home/gem",
        default_timeout: float = 120,
        hard_timeout: float = 600,
        no_change_timeout: int = 300,
    ):
        self.client = client
        self.working_dir = working_dir
        self.default_timeout = default_timeout
        self.hard_timeout = hard_timeout
        self._id = str(uuid.uuid4())

        # Create a persistent shell session for execute/grep
        session_resp = self.client.shell.create_session(
            exec_dir=working_dir,
            no_change_timeout=no_change_timeout,
        )
        self.session_id = session_resp.data.session_id

    @property
    def id(self) -> str:
        return self._id

    # --- Execute: shell API ---

    def execute(
        self,
        command: str,
        *,
        timeout: int | None = None,
    ) -> ExecuteResponse:
        """Execute a command in the persistent shell session."""
        effective_timeout = timeout if timeout is not None else self.default_timeout

        result = self.client.shell.exec_command(
            command=command,
            id=self.session_id,
            timeout=effective_timeout,
            hard_timeout=self.hard_timeout,
        )

        output = getattr(result.data, "output", "") or ""
        exit_code = getattr(result.data, "exit_code", 0) or 0

        return ExecuteResponse(output=output, exit_code=exit_code)

    # --- File operations: file API ---

    def ls_info(self, path: str) -> list[FileInfo]:
        """List directory contents via file API."""
        try:
            resp = self.client.file.list_path(path=path, include_size=True)
            result: list[FileInfo] = []
            for f in resp.data.files or []:
                info: FileInfo = {
                    "path": f.path,
                    "is_dir": f.is_directory or False,
                }
                if f.size is not None:
                    info["size"] = f.size
                if f.modified_time is not None:
                    info["modified_at"] = f.modified_time
                result.append(info)
            return result
        except Exception:
            return []

    def read(
        self,
        file_path: str,
        offset: int = 0,
        limit: int = 2000,
    ) -> str:
        """Read file content via file API, formatted with line numbers."""
        try:
            resp = self.client.file.read_file(
                file=file_path,
                start_line=offset,
                end_line=offset + limit,
            )
            content = getattr(resp.data, "content", "") or ""
            if not content:
                return "System reminder: File exists but has empty contents"

            lines = content.split("\n")
            formatted = []
            for i, line in enumerate(lines):
                line_num = offset + i + 1
                formatted.append(f"{line_num:6d}\t{line}")
            return "\n".join(formatted)
        except Exception:
            return f"Error: File '{file_path}' not found"

    def write(
        self,
        file_path: str,
        content: str,
    ) -> WriteResult:
        """Create a new file via file API. Errors if file already exists."""
        try:
            # Check existence first
            try:
                self.client.file.read_file(file=file_path, start_line=0, end_line=1)
                return WriteResult(error=f"Error: File '{file_path}' already exists")
            except Exception:
                pass

            self.client.file.write_file(file=file_path, content=content)
            return WriteResult(path=file_path, files_update=None)
        except Exception as e:
            return WriteResult(error=f"Failed to write file '{file_path}': {e}")

    def edit(
        self,
        file_path: str,
        old_string: str,
        new_string: str,
        replace_all: bool = False,
    ) -> EditResult:
        """Edit file via str_replace_editor API (atomic, server-side)."""
        try:
            replace_mode = "ALL" if replace_all else None
            resp = self.client.file.str_replace_editor(
                command="str_replace",
                path=file_path,
                old_str=old_string,
                new_str=new_string,
                replace_mode=replace_mode,
            )
            # Count occurrences from old_content if available
            old_content = getattr(resp.data, "old_content", None) or ""
            count = old_content.count(old_string) if old_content else 1
            return EditResult(path=file_path, files_update=None, occurrences=count)
        except Exception as e:
            err_msg = str(e)
            if "not found" in err_msg.lower() or "No such file" in err_msg:
                return EditResult(error=f"Error: File '{file_path}' not found")
            if "not unique" in err_msg.lower() or "multiple" in err_msg.lower():
                return EditResult(
                    error=f"Error: String '{old_string}' appears multiple times. "
                    "Use replace_all=True to replace all occurrences."
                )
            if "No replacement was performed" in err_msg or "not found in" in err_msg.lower():
                return EditResult(error=f"Error: String not found in file: '{old_string}'")
            return EditResult(error=f"Edit failed: {err_msg}")

    def glob_info(self, pattern: str, path: str = "/") -> list[FileInfo]:
        """Find files matching glob pattern via file API."""
        try:
            resp = self.client.file.find_files(path=path, glob=pattern)
            result: list[FileInfo] = []
            for f in resp.data.files or []:
                result.append({"path": f})
            return result
        except Exception:
            return []

    def grep_raw(
        self,
        pattern: str,
        path: str | None = None,
        glob: str | None = None,
    ) -> list[GrepMatch] | str:
        """Search files via shell grep (single-line command, clean output)."""
        # Delegate to BaseSandbox's default grep implementation which uses execute()
        return super().grep_raw(pattern, path, glob)

    # --- File transfer: file API ---

    def upload_files(self, files: list[tuple[str, bytes]]) -> list[FileUploadResponse]:
        """Upload files via file API."""
        responses = []
        for path, content in files:
            try:
                encoded = base64.b64encode(content).decode("ascii")
                self.client.file.write_file(
                    file=path,
                    content=encoded,
                    encoding="base64",
                )
                responses.append(FileUploadResponse(path=path))
            except Exception:
                responses.append(FileUploadResponse(path=path, error="permission_denied"))
        return responses

    def download_files(self, paths: list[str]) -> list[FileDownloadResponse]:
        """Download files via file API."""
        responses = []
        for path in paths:
            try:
                resp = self.client.file.read_file(file=path)
                content_str = getattr(resp.data, "content", "") or ""
                responses.append(FileDownloadResponse(
                    path=path,
                    content=content_str.encode("utf-8"),
                ))
            except Exception:
                responses.append(FileDownloadResponse(
                    path=path,
                    error="file_not_found",
                ))
        return responses

    def close(self):
        """Clean up the shell session."""
        try:
            self.client.shell.cleanup_session(session_id=self.session_id)
        except Exception:
            pass
