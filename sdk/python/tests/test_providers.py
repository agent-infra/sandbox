"""Tests for cloud providers."""

import pytest
from agent_sandbox.providers import VolcengineProvider


@pytest.mark.unit
class TestVolcengineProvider:
    """Test Volcengine provider."""

    def test_provider_initialization(self):
        """Test initializing Volcengine provider."""
        provider = VolcengineProvider(
            access_key="test-key",
            secret_key="test-secret",
            region="cn-beijing"
        )
        assert provider is not None
        assert provider.region == "cn-beijing"

    def test_provider_with_custom_endpoint(self):
        """Test provider with custom endpoint."""
        provider = VolcengineProvider(
            access_key="test-key",
            secret_key="test-secret",
            region="cn-beijing",
            endpoint="https://custom.endpoint.com"
        )
        assert provider is not None

    def test_provider_signature_generation(self):
        """Test that provider can generate signatures."""
        provider = VolcengineProvider(
            access_key="test-key",
            secret_key="test-secret",
            region="cn-beijing"
        )
        # The provider should have methods for signing requests
        assert hasattr(provider, 'sign_request') or hasattr(provider, '_sign')
