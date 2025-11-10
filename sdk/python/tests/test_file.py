"""Tests for file operations."""

import pytest
import respx
from httpx import Response


@pytest.mark.unit
class TestFileOperations:
    """Test file operations."""

    @respx.mock
    def test_read_file(self, sandbox_client):
        """Test reading a file."""
        mock_response = {
            "content": "Hello, world!",
            "encoding": "utf-8",
            "size": 13,
        }

        route = respx.post("http://localhost:8080/v1/file/read").mock(
            return_value=Response(200, json={"data": mock_response})
        )

        result = sandbox_client.file.read_file(file="/tmp/test.txt")
        assert route.called
        assert result.data.content == "Hello, world!"

    @respx.mock
    def test_write_file(self, sandbox_client):
        """Test writing a file."""
        mock_response = {
            "bytes_written": 26,
            "path": "/tmp/example.txt",
        }

        route = respx.post("http://localhost:8080/v1/file/write").mock(
            return_value=Response(200, json={"data": mock_response})
        )

        result = sandbox_client.file.write_file(
            file="/tmp/example.txt",
            content="Hello from TypeScript SDK!",
            encoding="utf-8"
        )
        assert route.called
        assert result.data.bytes_written == 26

    @respx.mock
    def test_list_path(self, sandbox_client):
        """Test listing directory contents."""
        mock_response = {
            "files": [
                {"name": "test.txt", "size": 13, "is_directory": False},
                {"name": "subdir", "size": 0, "is_directory": True},
            ],
            "total_count": 2,
        }

        route = respx.post("http://localhost:8080/v1/file/list").mock(
            return_value=Response(200, json={"data": mock_response})
        )

        result = sandbox_client.file.list_path(path="/tmp")
        assert route.called
        assert result.data.total_count == 2

    @respx.mock
    def test_search_files(self, sandbox_client):
        """Test searching for files."""
        mock_response = {
            "matches": [
                {"path": "/tmp/test.txt", "line": 1, "content": "Hello"},
            ],
            "total_matches": 1,
        }

        route = respx.post("http://localhost:8080/v1/file/search").mock(
            return_value=Response(200, json={"data": mock_response})
        )

        result = sandbox_client.file.search_files(
            path="/tmp",
            pattern="Hello"
        )
        assert route.called
        assert result.data.total_matches == 1


@pytest.mark.asyncio
class TestAsyncFileOperations:
    """Test async file operations."""

    @respx.mock
    async def test_async_read_file(self, async_sandbox_client):
        """Test reading a file asynchronously."""
        mock_response = {
            "content": "Async content",
            "encoding": "utf-8",
            "size": 13,
        }

        route = respx.post("http://localhost:8080/v1/file/read").mock(
            return_value=Response(200, json={"data": mock_response})
        )

        result = await async_sandbox_client.file.read_file(file="/tmp/async.txt")
        assert route.called
        assert result.data.content == "Async content"

    @respx.mock
    async def test_async_write_file(self, async_sandbox_client):
        """Test writing a file asynchronously."""
        mock_response = {
            "bytes_written": 15,
            "path": "/tmp/async.txt",
        }

        route = respx.post("http://localhost:8080/v1/file/write").mock(
            return_value=Response(200, json={"data": mock_response})
        )

        result = await async_sandbox_client.file.write_file(
            file="/tmp/async.txt",
            content="Async test data",
            encoding="utf-8"
        )
        assert route.called
        assert result.data.bytes_written == 15
