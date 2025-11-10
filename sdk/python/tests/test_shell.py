"""Tests for shell command execution."""

import pytest
import respx
from httpx import Response


@pytest.mark.unit
class TestShellExecution:
    """Test shell command execution."""

    @respx.mock
    def test_exec_command(self, sandbox_client):
        """Test executing a shell command."""
        mock_response = {
            "output": "Hello from sandbox!",
            "exit_code": 0,
            "pid": 1234,
        }

        route = respx.post("http://localhost:8080/v1/shell/exec").mock(
            return_value=Response(200, json={"data": mock_response})
        )

        result = sandbox_client.shell.exec_command(
            command="echo 'Hello from sandbox!'"
        )
        assert route.called
        assert result.data.exit_code == 0

    @respx.mock
    def test_exec_command_with_timeout(self, sandbox_client):
        """Test executing a command with timeout."""
        mock_response = {
            "output": "Command completed",
            "exit_code": 0,
            "pid": 1235,
        }

        route = respx.post("http://localhost:8080/v1/shell/exec").mock(
            return_value=Response(200, json={"data": mock_response})
        )

        result = sandbox_client.shell.exec_command(
            command="sleep 1 && echo 'done'",
            timeout=5000
        )
        assert route.called
        assert result.data.exit_code == 0

    @respx.mock
    def test_view_output(self, sandbox_client):
        """Test viewing shell output."""
        mock_response = {
            "output": "Command output",
            "complete": True,
        }

        route = respx.post("http://localhost:8080/v1/shell/view").mock(
            return_value=Response(200, json={"data": mock_response})
        )

        result = sandbox_client.shell.view(pid=1234)
        assert route.called
        assert result.data.complete is True


@pytest.mark.asyncio
class TestAsyncShellExecution:
    """Test async shell command execution."""

    @respx.mock
    async def test_async_exec_command(self, async_sandbox_client):
        """Test executing a shell command asynchronously."""
        mock_response = {
            "output": "Hello from async!",
            "exit_code": 0,
            "pid": 5678,
        }

        route = respx.post("http://localhost:8080/v1/shell/exec").mock(
            return_value=Response(200, json={"data": mock_response})
        )

        result = await async_sandbox_client.shell.exec_command(
            command="echo 'Hello from async!'"
        )
        assert route.called
        assert result.data.exit_code == 0
