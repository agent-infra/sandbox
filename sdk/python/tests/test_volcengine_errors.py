"""Provider failures must reach callers rather than masquerading as results."""

from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
import volcenginesdkcore
from agent_sandbox.providers import VolcengineProvider


@pytest.fixture
def provider(monkeypatch):
    # The constructor sets an SDK-wide default; keep that change test-local.
    monkeypatch.setattr(volcenginesdkcore.Configuration, "_default", None)
    return VolcengineProvider(
        access_key="test-access-key", secret_key="test-secret-key"
    )


@pytest.mark.parametrize(
    "method, args, sdk_method",
    [
        ("create_sandbox", ("function-id",), "create_sandbox"),
        ("delete_sandbox", ("function-id", "sandbox-id"), "kill_sandbox"),
        ("get_sandbox", ("function-id", "sandbox-id"), "describe_sandbox"),
        (
            "set_sandbox_timeout",
            ("function-id", "sandbox-id", 60),
            "set_sandbox_timeout",
        ),
        ("list_sandboxes", ("function-id",), "list_sandboxes"),
    ],
)
def test_sdk_failures_are_raised(provider, monkeypatch, method, args, sdk_method):
    error = volcenginesdkcore.rest.ApiException(status=403, reason="Permission denied")
    monkeypatch.setattr(provider._client, sdk_method, Mock(side_effect=error))

    with pytest.raises(volcenginesdkcore.rest.ApiException) as raised:
        getattr(provider, method)(*args)

    assert raised.value is error


@pytest.mark.parametrize("method", ["get_sandbox", "list_sandboxes"])
def test_domain_lookup_failures_are_raised(provider, monkeypatch, method):
    sandbox = Mock()
    sandbox.to_dict.return_value = {"sandbox_id": "sandbox-id"}
    monkeypatch.setattr(
        provider._client, "describe_sandbox", Mock(return_value=sandbox)
    )
    monkeypatch.setattr(
        provider._client,
        "list_sandboxes",
        Mock(return_value=SimpleNamespace(sandboxes=[sandbox])),
    )
    error = httpx.ConnectError("APIG connection failed")
    monkeypatch.setattr(
        "agent_sandbox.providers.volcengine.request", Mock(side_effect=error)
    )
    args = (
        ("function-id", "sandbox-id") if method == "get_sandbox" else ("function-id",)
    )

    with pytest.raises(httpx.ConnectError) as raised:
        getattr(provider, method)(*args)

    assert raised.value is error


def test_successful_sandbox_operations_keep_their_results(provider, monkeypatch):
    monkeypatch.setattr(
        provider._client,
        "create_sandbox",
        Mock(return_value=SimpleNamespace(sandbox_id="sandbox-id")),
    )
    killed = object()
    updated = object()
    described = object()
    monkeypatch.setattr(provider._client, "kill_sandbox", Mock(return_value=killed))
    monkeypatch.setattr(
        provider._client, "set_sandbox_timeout", Mock(return_value=updated)
    )
    monkeypatch.setattr(
        provider._client, "describe_sandbox", Mock(return_value=described)
    )
    monkeypatch.setattr(
        provider._client,
        "list_sandboxes",
        Mock(return_value=SimpleNamespace(sandboxes=[])),
    )
    monkeypatch.setattr(provider, "get_apig_domains", Mock(return_value=[]))

    assert provider.create_sandbox("function-id") == "sandbox-id"
    assert provider.delete_sandbox("function-id", "sandbox-id") is killed
    assert provider.set_sandbox_timeout("function-id", "sandbox-id", 60) is updated
    assert (
        provider.get_sandbox("function-id", "sandbox-id", include_domains=False)
        is described
    )
    assert provider.list_sandboxes("function-id") == []
