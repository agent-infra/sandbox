"""Tests for code execution."""

import pytest
import respx
from httpx import Response


@pytest.mark.unit
class TestCodeExecution:
    """Test code execution."""

    @respx.mock
    def test_execute_python_code(self, sandbox_client):
        """Test executing Python code."""
        mock_response = {
            "output": "4\n",
            "error": "",
            "exit_code": 0,
        }

        route = respx.post("http://localhost:8080/v1/code/execute").mock(
            return_value=Response(200, json={"data": mock_response})
        )

        result = sandbox_client.code.execute_code(
            language="python",
            code="print(2 + 2)"
        )
        assert route.called
        assert result.data.exit_code == 0
        assert "4" in result.data.output

    @respx.mock
    def test_execute_javascript_code(self, sandbox_client):
        """Test executing JavaScript code."""
        mock_response = {
            "output": "4\n",
            "error": "",
            "exit_code": 0,
        }

        route = respx.post("http://localhost:8080/v1/code/execute").mock(
            return_value=Response(200, json={"data": mock_response})
        )

        result = sandbox_client.code.execute_code(
            language="javascript",
            code="console.log(2 + 2)"
        )
        assert route.called
        assert result.data.exit_code == 0

    @respx.mock
    def test_execute_code_with_error(self, sandbox_client):
        """Test executing code that produces an error."""
        mock_response = {
            "output": "",
            "error": "NameError: name 'undefined_var' is not defined",
            "exit_code": 1,
        }

        route = respx.post("http://localhost:8080/v1/code/execute").mock(
            return_value=Response(200, json={"data": mock_response})
        )

        result = sandbox_client.code.execute_code(
            language="python",
            code="print(undefined_var)"
        )
        assert route.called
        assert result.data.exit_code == 1
        assert "NameError" in result.data.error


@pytest.mark.asyncio
class TestAsyncCodeExecution:
    """Test async code execution."""

    @respx.mock
    async def test_async_execute_python_code(self, async_sandbox_client):
        """Test executing Python code asynchronously."""
        mock_response = {
            "output": "Hello from async Python!\n",
            "error": "",
            "exit_code": 0,
        }

        route = respx.post("http://localhost:8080/v1/code/execute").mock(
            return_value=Response(200, json={"data": mock_response})
        )

        result = await async_sandbox_client.code.execute_code(
            language="python",
            code="print('Hello from async Python!')"
        )
        assert route.called
        assert result.data.exit_code == 0
        assert "Hello from async Python!" in result.data.output
