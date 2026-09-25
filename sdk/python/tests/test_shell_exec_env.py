"""
Tests for the env parameter in /v1/shell/exec request.

Validates that the env field is correctly accepted by both sync and async
ShellClient and RawShellClient, and is properly serialized in the request body.
"""

import inspect
import typing
import unittest
from unittest.mock import MagicMock, AsyncMock, patch

from agent_sandbox.shell.client import ShellClient, AsyncShellClient
from agent_sandbox.shell.raw_client import RawShellClient, AsyncRawShellClient


class TestShellExecEnvParameterSignature(unittest.TestCase):
    """Verify that the env parameter exists in all exec_command signatures."""

    def test_raw_shell_client_has_env_param(self):
        sig = inspect.signature(RawShellClient.exec_command)
        self.assertIn("env", sig.parameters)
        param = sig.parameters["env"]
        self.assertEqual(param.kind, inspect.Parameter.KEYWORD_ONLY)

    def test_async_raw_shell_client_has_env_param(self):
        sig = inspect.signature(AsyncRawShellClient.exec_command)
        self.assertIn("env", sig.parameters)
        param = sig.parameters["env"]
        self.assertEqual(param.kind, inspect.Parameter.KEYWORD_ONLY)

    def test_shell_client_has_env_param(self):
        sig = inspect.signature(ShellClient.exec_command)
        self.assertIn("env", sig.parameters)
        param = sig.parameters["env"]
        self.assertEqual(param.kind, inspect.Parameter.KEYWORD_ONLY)

    def test_async_shell_client_has_env_param(self):
        sig = inspect.signature(AsyncShellClient.exec_command)
        self.assertIn("env", sig.parameters)
        param = sig.parameters["env"]
        self.assertEqual(param.kind, inspect.Parameter.KEYWORD_ONLY)


class TestShellExecEnvParameterSerialization(unittest.TestCase):
    """Verify that the env parameter is included in the request JSON body."""

    def _make_sync_client(self):
        """Create a RawShellClient with mocked httpx client."""
        wrapper = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "id": "test-session",
                "status": "completed",
                "exit_code": 0,
                "output": "test output",
            },
        }
        mock_response.headers = {}
        wrapper.httpx_client.request.return_value = mock_response
        return RawShellClient(client_wrapper=wrapper), wrapper

    def test_env_included_in_request_body(self):
        """Env dict should appear in the JSON body sent to the API."""
        client, wrapper = self._make_sync_client()
        env_vars = {"MY_VAR": "hello", "PATH": "/usr/bin"}

        try:
            client.exec_command(command="echo $MY_VAR", env=env_vars)
        except Exception:
            pass  # We only care about what was sent

        call_args = wrapper.httpx_client.request.call_args
        json_body = call_args.kwargs.get("json") or call_args[1].get("json")

        self.assertIn("env", json_body)
        self.assertEqual(json_body["env"], {"MY_VAR": "hello", "PATH": "/usr/bin"})

    def test_env_none_included_in_request_body(self):
        """When env=None, it should be sent as None in the body."""
        client, wrapper = self._make_sync_client()

        try:
            client.exec_command(command="ls", env=None)
        except Exception:
            pass

        call_args = wrapper.httpx_client.request.call_args
        json_body = call_args.kwargs.get("json") or call_args[1].get("json")

        self.assertIn("env", json_body)
        self.assertIsNone(json_body["env"])

    def test_env_omitted_when_not_provided(self):
        """When env is not provided, it should use the OMIT sentinel."""
        client, wrapper = self._make_sync_client()

        try:
            client.exec_command(command="ls")
        except Exception:
            pass

        call_args = wrapper.httpx_client.request.call_args
        json_body = call_args.kwargs.get("json") or call_args[1].get("json")

        # The OMIT sentinel is used; the httpx client wrapper will strip it
        self.assertIn("env", json_body)

    def test_env_empty_dict_included(self):
        """An empty env dict should be sent as-is."""
        client, wrapper = self._make_sync_client()

        try:
            client.exec_command(command="ls", env={})
        except Exception:
            pass

        call_args = wrapper.httpx_client.request.call_args
        json_body = call_args.kwargs.get("json") or call_args[1].get("json")

        self.assertIn("env", json_body)
        self.assertEqual(json_body["env"], {})

    def test_env_with_special_values(self):
        """Env values with special characters should be preserved."""
        client, wrapper = self._make_sync_client()
        env_vars = {
            "SPACES": "value with spaces",
            "EQUALS": "key=value",
            "EMPTY": "",
            "QUOTES": '"quoted"',
            "NEWLINE": "line1\nline2",
        }

        try:
            client.exec_command(command="printenv", env=env_vars)
        except Exception:
            pass

        call_args = wrapper.httpx_client.request.call_args
        json_body = call_args.kwargs.get("json") or call_args[1].get("json")

        self.assertEqual(json_body["env"]["SPACES"], "value with spaces")
        self.assertEqual(json_body["env"]["EQUALS"], "key=value")
        self.assertEqual(json_body["env"]["EMPTY"], "")
        self.assertEqual(json_body["env"]["QUOTES"], '"quoted"')
        self.assertEqual(json_body["env"]["NEWLINE"], "line1\nline2")

    def test_env_coexists_with_other_params(self):
        """Env should work alongside all other parameters."""
        client, wrapper = self._make_sync_client()

        try:
            client.exec_command(
                command="echo $DB_HOST",
                id="session-1",
                exec_dir="/tmp",
                async_mode=False,
                timeout=30.0,
                strict=True,
                no_change_timeout=10,
                hard_timeout=60.0,
                preserve_symlinks=False,
                truncate=True,
                env={"DB_HOST": "localhost", "DB_PORT": "5432"},
            )
        except Exception:
            pass

        call_args = wrapper.httpx_client.request.call_args
        json_body = call_args.kwargs.get("json") or call_args[1].get("json")

        self.assertEqual(json_body["command"], "echo $DB_HOST")
        self.assertEqual(json_body["id"], "session-1")
        self.assertEqual(json_body["exec_dir"], "/tmp")
        self.assertEqual(json_body["env"], {"DB_HOST": "localhost", "DB_PORT": "5432"})


class TestShellClientEnvDelegation(unittest.TestCase):
    """Verify that ShellClient properly delegates env to RawShellClient."""

    def test_shell_client_passes_env_to_raw_client(self):
        """ShellClient.exec_command should forward env to RawShellClient."""
        wrapper = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "id": "test",
                "status": "completed",
                "exit_code": 0,
                "output": "",
            },
        }
        mock_response.headers = {}
        wrapper.httpx_client.request.return_value = mock_response

        client = ShellClient(client_wrapper=wrapper)
        env_vars = {"FOO": "bar"}

        try:
            client.exec_command(command="echo $FOO", env=env_vars)
        except Exception:
            pass

        call_args = wrapper.httpx_client.request.call_args
        json_body = call_args.kwargs.get("json") or call_args[1].get("json")

        self.assertEqual(json_body["env"], {"FOO": "bar"})


class TestOpenAPISpecEnvField(unittest.TestCase):
    """Verify the OpenAPI spec includes the env field."""

    def test_openapi_spec_has_env_field(self):
        import json
        import os

        spec_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "website",
            "docs",
            "public",
            "v1",
            "openapi.json",
        )
        spec_path = os.path.normpath(spec_path)

        if not os.path.exists(spec_path):
            self.skipTest(f"OpenAPI spec not found at {spec_path}")

        with open(spec_path, "r") as f:
            spec = json.load(f)

        shell_exec_schema = spec["components"]["schemas"]["ShellExecRequest"]
        self.assertIn("env", shell_exec_schema["properties"])

        env_prop = shell_exec_schema["properties"]["env"]
        # Should be nullable (anyOf with object and null)
        self.assertIn("anyOf", env_prop)

        any_of_types = [item.get("type") for item in env_prop["anyOf"]]
        self.assertIn("object", any_of_types)
        self.assertIn("null", any_of_types)

        # The object type should have additionalProperties: { type: string }
        obj_schema = next(s for s in env_prop["anyOf"] if s.get("type") == "object")
        self.assertIn("additionalProperties", obj_schema)
        self.assertEqual(obj_schema["additionalProperties"]["type"], "string")


if __name__ == "__main__":
    unittest.main()
