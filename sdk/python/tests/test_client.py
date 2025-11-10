"""Tests for Sandbox client initialization and configuration."""

import pytest
from agent_sandbox import Sandbox, AsyncSandbox


@pytest.mark.unit
class TestClientInitialization:
    """Test client initialization."""

    def test_sync_client_creation(self):
        """Test creating a synchronous Sandbox client."""
        client = Sandbox(base_url="http://localhost:8080")
        assert client is not None

    def test_async_client_creation(self):
        """Test creating an asynchronous Sandbox client."""
        client = AsyncSandbox(base_url="http://localhost:8080")
        assert client is not None

    def test_client_with_custom_headers(self):
        """Test creating a client with custom headers."""
        custom_headers = {"X-Custom-Header": "test-value"}
        client = Sandbox(
            base_url="http://localhost:8080",
            headers=custom_headers
        )
        assert client is not None

    def test_client_with_timeout(self):
        """Test creating a client with custom timeout."""
        client = Sandbox(
            base_url="http://localhost:8080",
            timeout=60.0
        )
        assert client is not None

    def test_client_has_required_modules(self, sandbox_client):
        """Test that client has all required module attributes."""
        assert hasattr(sandbox_client, 'sandbox')
        assert hasattr(sandbox_client, 'shell')
        assert hasattr(sandbox_client, 'file')
        assert hasattr(sandbox_client, 'jupyter')
        assert hasattr(sandbox_client, 'nodejs')
        assert hasattr(sandbox_client, 'mcp')
        assert hasattr(sandbox_client, 'browser')
        assert hasattr(sandbox_client, 'code')
        assert hasattr(sandbox_client, 'util')
        assert hasattr(sandbox_client, 'skills')
