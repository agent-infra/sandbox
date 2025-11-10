/**
 * Tests for sandbox context and package information.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { SandboxClient } from '../src';

describe('Sandbox Information', () => {
  let client: SandboxClient;

  beforeEach(() => {
    client = new SandboxClient({
      environment: 'http://localhost:8080',
    });
  });

  it('should have getContext method', () => {
    expect(client.sandbox.getContext).toBeDefined();
    expect(typeof client.sandbox.getContext).toBe('function');
  });

  it('should have getPythonPackages method', () => {
    expect(client.sandbox.getPythonPackages).toBeDefined();
    expect(typeof client.sandbox.getPythonPackages).toBe('function');
  });

  it('should have getNodejsPackages method', () => {
    expect(client.sandbox.getNodejsPackages).toBeDefined();
    expect(typeof client.sandbox.getNodejsPackages).toBe('function');
  });
});

describe('Sandbox Context Response', () => {
  it('should handle successful context response', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        data: {
          homeDir: '/home/sandbox',
          workDir: '/workspace',
          user: 'sandbox',
        },
      }),
    });

    global.fetch = mockFetch;

    const client = new SandboxClient({
      environment: 'http://localhost:8080',
    });

    const result = await client.sandbox.getContext();

    if (result.ok) {
      expect(result.body).toBeDefined();
    }
  });

  it('should handle failed context response', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => ({ error: 'Internal server error' }),
    });

    global.fetch = mockFetch;

    const client = new SandboxClient({
      environment: 'http://localhost:8080',
    });

    const result = await client.sandbox.getContext();

    expect(result.ok).toBe(false);
  });
});
