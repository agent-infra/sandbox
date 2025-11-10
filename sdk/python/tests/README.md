# Python SDK Tests

This directory contains the test suite for the agent-sandbox Python SDK.

## Installation

Install the package with development dependencies:

```bash
pip install -e ".[dev]"
```

## Running Tests

Run all tests:

```bash
pytest
```

Run specific test file:

```bash
pytest tests/test_client.py
```

Run with coverage:

```bash
pytest --cov=agent_sandbox --cov-report=html
```

Run only unit tests:

```bash
pytest -m unit
```

Run only integration tests:

```bash
pytest -m integration
```

## Test Structure

- `test_client.py` - Client initialization and configuration tests
- `test_sandbox.py` - Sandbox context and package information tests
- `test_shell.py` - Shell command execution tests
- `test_file.py` - File operations tests
- `test_code.py` - Code execution tests
- `test_providers.py` - Cloud provider tests
- `conftest.py` - Shared fixtures and configuration

## Test Categories

Tests are marked with the following markers:

- `@pytest.mark.unit` - Unit tests (mocked, no external dependencies)
- `@pytest.mark.integration` - Integration tests (require running sandbox)
- `@pytest.mark.asyncio` - Async tests

## Coverage

After running tests with coverage, open `htmlcov/index.html` to view the coverage report.
