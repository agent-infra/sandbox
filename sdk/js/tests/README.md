# TypeScript SDK Tests

This directory contains the test suite for the @agent-infra/sandbox TypeScript SDK.

## Installation

Install dependencies:

```bash
npm install
```

## Running Tests

Run all tests:

```bash
npm test
```

Run tests in watch mode:

```bash
npm test -- --watch
```

Run tests with coverage:

```bash
npm run test:coverage
```

Run tests with UI:

```bash
npm run test:ui
```

Run specific test file:

```bash
npm test -- tests/client.test.ts
```

## Test Structure

- `client.test.ts` - Client initialization and configuration tests
- `sandbox.test.ts` - Sandbox context and package information tests
- `shell.test.ts` - Shell command execution tests
- `file.test.ts` - File operations tests
- `code.test.ts` - Code execution tests
- `providers.test.ts` - Cloud provider tests

## Test Framework

This project uses [Vitest](https://vitest.dev/) as the test framework, which provides:

- Fast test execution with ESM support
- TypeScript support out of the box
- Compatible with Jest API
- Built-in code coverage
- Watch mode and UI

## Coverage

After running tests with coverage (`npm run test:coverage`), you can find the coverage report in:

- Terminal output (text summary)
- `coverage/index.html` (HTML report)
- `coverage/coverage-final.json` (JSON report)

## Writing Tests

Tests follow the Vitest API, which is compatible with Jest:

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { SandboxClient } from '../src';

describe('Feature Name', () => {
  let client: SandboxClient;

  beforeEach(() => {
    client = new SandboxClient({
      environment: 'http://localhost:8080',
    });
  });

  it('should test something', () => {
    expect(client).toBeDefined();
  });
});
```

## Mocking

Tests use Vitest's built-in mocking capabilities to mock API responses:

```typescript
const mockFetch = vi.fn().mockResolvedValue({
  ok: true,
  status: 200,
  json: async () => ({ data: { /* mock data */ } }),
});

global.fetch = mockFetch;
```
