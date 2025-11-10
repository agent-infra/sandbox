"""Pytest configuration and fixtures for agent-sandbox tests."""

import pytest
from agent_sandbox import Sandbox, AsyncSandbox


@pytest.fixture
def mock_base_url():
    """Mock base URL for testing."""
    return "http://localhost:8080"


@pytest.fixture
def sandbox_client(mock_base_url):
    """Create a Sandbox client for testing."""
    return Sandbox(base_url=mock_base_url)


@pytest.fixture
def async_sandbox_client(mock_base_url):
    """Create an AsyncSandbox client for testing."""
    return AsyncSandbox(base_url=mock_base_url)
