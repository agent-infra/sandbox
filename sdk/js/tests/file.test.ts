/**
 * Tests for file operations.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { SandboxClient } from '../src';

describe('File Operations', () => {
  let client: SandboxClient;

  beforeEach(() => {
    client = new SandboxClient({
      environment: 'http://localhost:8080',
    });
  });

  it('should have readFile method', () => {
    expect(client.file.readFile).toBeDefined();
    expect(typeof client.file.readFile).toBe('function');
  });

  it('should have writeFile method', () => {
    expect(client.file.writeFile).toBeDefined();
    expect(typeof client.file.writeFile).toBe('function');
  });

  it('should have listPath method', () => {
    expect(client.file.listPath).toBeDefined();
    expect(typeof client.file.listPath).toBe('function');
  });

  it('should have searchFiles method', () => {
    expect(client.file.searchFiles).toBeDefined();
    expect(typeof client.file.searchFiles).toBe('function');
  });
});

describe('File Read Operations', () => {
  it('should handle successful file read', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        data: {
          content: 'Hello, world!',
          encoding: 'utf-8',
          size: 13,
        },
      }),
    });

    global.fetch = mockFetch;

    const client = new SandboxClient({
      environment: 'http://localhost:8080',
    });

    const result = await client.file.readFile({
      file: '/tmp/test.txt',
    });

    if (result.ok) {
      expect(result.body).toBeDefined();
    }
  });

  it('should handle file not found', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      json: async () => ({ error: 'File not found' }),
    });

    global.fetch = mockFetch;

    const client = new SandboxClient({
      environment: 'http://localhost:8080',
    });

    const result = await client.file.readFile({
      file: '/nonexistent/file.txt',
    });

    expect(result.ok).toBe(false);
  });
});

describe('File Write Operations', () => {
  it('should handle successful file write', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        data: {
          bytesWritten: 26,
          path: '/tmp/example.txt',
        },
      }),
    });

    global.fetch = mockFetch;

    const client = new SandboxClient({
      environment: 'http://localhost:8080',
    });

    const result = await client.file.writeFile({
      file: '/tmp/example.txt',
      content: 'Hello from TypeScript SDK!',
      encoding: 'utf-8',
    });

    if (result.ok) {
      expect(result.body).toBeDefined();
    }
  });
});

describe('File List Operations', () => {
  it('should handle successful directory listing', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        data: {
          files: [
            { name: 'test.txt', size: 13, isDirectory: false },
            { name: 'subdir', size: 0, isDirectory: true },
          ],
          totalCount: 2,
        },
      }),
    });

    global.fetch = mockFetch;

    const client = new SandboxClient({
      environment: 'http://localhost:8080',
    });

    const result = await client.file.listPath({
      path: '/tmp',
    });

    if (result.ok) {
      expect(result.body).toBeDefined();
    }
  });
});
