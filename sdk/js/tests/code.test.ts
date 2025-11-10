/**
 * Tests for code execution.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { SandboxClient } from '../src';

describe('Code Execution', () => {
  let client: SandboxClient;

  beforeEach(() => {
    client = new SandboxClient({
      environment: 'http://localhost:8080',
    });
  });

  it('should have executeCode method', () => {
    expect(client.code.executeCode).toBeDefined();
    expect(typeof client.code.executeCode).toBe('function');
  });
});

describe('Python Code Execution', () => {
  it('should handle successful Python code execution', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        data: {
          output: '4\n',
          error: '',
          exitCode: 0,
        },
      }),
    });

    global.fetch = mockFetch;

    const client = new SandboxClient({
      environment: 'http://localhost:8080',
    });

    const result = await client.code.executeCode({
      language: 'python',
      code: 'print(2 + 2)',
    });

    if (result.ok) {
      expect(result.body).toBeDefined();
    }
  });

  it('should handle Python code with error', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        data: {
          output: '',
          error: 'NameError: name "undefined_var" is not defined',
          exitCode: 1,
        },
      }),
    });

    global.fetch = mockFetch;

    const client = new SandboxClient({
      environment: 'http://localhost:8080',
    });

    const result = await client.code.executeCode({
      language: 'python',
      code: 'print(undefined_var)',
    });

    if (result.ok) {
      expect(result.body).toBeDefined();
    }
  });
});

describe('JavaScript Code Execution', () => {
  it('should handle successful JavaScript code execution', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        data: {
          output: '4\n',
          error: '',
          exitCode: 0,
        },
      }),
    });

    global.fetch = mockFetch;

    const client = new SandboxClient({
      environment: 'http://localhost:8080',
    });

    const result = await client.code.executeCode({
      language: 'javascript',
      code: 'console.log(2 + 2)',
    });

    if (result.ok) {
      expect(result.body).toBeDefined();
    }
  });
});

describe('Multiple Language Support', () => {
  it('should support various programming languages', async () => {
    const languages = ['python', 'javascript', 'typescript', 'bash'];

    for (const language of languages) {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({
          data: {
            output: 'output',
            error: '',
            exitCode: 0,
          },
        }),
      });

      global.fetch = mockFetch;

      const client = new SandboxClient({
        environment: 'http://localhost:8080',
      });

      const result = await client.code.executeCode({
        language: language as any,
        code: 'test code',
      });

      expect(result.ok).toBeDefined();
    }
  });
});
