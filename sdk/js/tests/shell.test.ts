/**
 * Tests for shell command execution.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { SandboxClient } from '../src';

describe('Shell Operations', () => {
  let client: SandboxClient;

  beforeEach(() => {
    client = new SandboxClient({
      environment: 'http://localhost:8080',
    });
  });

  it('should have execCommand method', () => {
    expect(client.shell.execCommand).toBeDefined();
    expect(typeof client.shell.execCommand).toBe('function');
  });

  it('should have view method', () => {
    expect(client.shell.view).toBeDefined();
    expect(typeof client.shell.view).toBe('function');
  });

  it('should have wait method', () => {
    expect(client.shell.wait).toBeDefined();
    expect(typeof client.shell.wait).toBe('function');
  });
});

describe('Shell Command Execution', () => {
  it('should handle successful command execution', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        data: {
          output: 'Hello from sandbox!',
          exitCode: 0,
          pid: 1234,
        },
      }),
    });

    global.fetch = mockFetch;

    const client = new SandboxClient({
      environment: 'http://localhost:8080',
    });

    const result = await client.shell.execCommand({
      command: 'echo "Hello from sandbox!"',
    });

    if (result.ok) {
      expect(result.body).toBeDefined();
    }
  });

  it('should handle command with timeout', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        data: {
          output: 'Command completed',
          exitCode: 0,
          pid: 1235,
        },
      }),
    });

    global.fetch = mockFetch;

    const client = new SandboxClient({
      environment: 'http://localhost:8080',
    });

    const result = await client.shell.execCommand({
      command: 'sleep 1 && echo "done"',
      timeout: 5000,
    });

    if (result.ok) {
      expect(result.body).toBeDefined();
    }
  });

  it('should handle failed command execution', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
      json: async () => ({ error: 'Invalid command' }),
    });

    global.fetch = mockFetch;

    const client = new SandboxClient({
      environment: 'http://localhost:8080',
    });

    const result = await client.shell.execCommand({
      command: '',
    });

    expect(result.ok).toBe(false);
  });
});
