"""Tests for sandbox context and package information."""

import pytest
import respx
from httpx import Response


@pytest.mark.unit
class TestSandboxInfo:
    """Test sandbox information retrieval."""

    @respx.mock
    def test_get_context(self, sandbox_client):
        """Test getting sandbox context."""
        mock_context = {
            "home_dir": "/home/sandbox",
            "work_dir": "/workspace",
            "user": "sandbox",
        }

        route = respx.get("http://localhost:8080/v1/sandbox").mock(
            return_value=Response(200, json={"data": mock_context})
        )

        result = sandbox_client.sandbox.get_context()
        assert route.called
        assert result.data.home_dir == "/home/sandbox"

    @respx.mock
    def test_get_python_packages(self, sandbox_client):
        """Test getting Python packages."""
        mock_packages = {
            "packages": [
                {"name": "pytest", "version": "7.0.0"},
                {"name": "httpx", "version": "0.24.0"},
            ]
        }

        route = respx.get("http://localhost:8080/v1/sandbox/packages/python").mock(
            return_value=Response(200, json={"data": mock_packages})
        )

        result = sandbox_client.sandbox.get_python_packages()
        assert route.called
        assert result.data is not None

    @respx.mock
    def test_get_nodejs_packages(self, sandbox_client):
        """Test getting Node.js packages."""
        mock_packages = {
            "packages": [
                {"name": "typescript", "version": "5.0.0"},
                {"name": "vitest", "version": "1.0.0"},
            ]
        }

        route = respx.get("http://localhost:8080/v1/sandbox/packages/nodejs").mock(
            return_value=Response(200, json={"data": mock_packages})
        )

        result = sandbox_client.sandbox.get_nodejs_packages()
        assert route.called
        assert result.data is not None


@pytest.mark.asyncio
class TestAsyncSandboxInfo:
    """Test async sandbox information retrieval."""

    @respx.mock
    async def test_async_get_context(self, async_sandbox_client):
        """Test getting sandbox context asynchronously."""
        mock_context = {
            "home_dir": "/home/sandbox",
            "work_dir": "/workspace",
        }

        route = respx.get("http://localhost:8080/v1/sandbox").mock(
            return_value=Response(200, json={"data": mock_context})
        )

        result = await async_sandbox_client.sandbox.get_context()
        assert route.called
        assert result.data.home_dir == "/home/sandbox"
