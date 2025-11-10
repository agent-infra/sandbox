/**
 * Tests for SandboxClient initialization and configuration.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { SandboxClient } from '../src';

describe('SandboxClient Initialization', () => {
  let client: SandboxClient;

  beforeEach(() => {
    client = new SandboxClient({
      environment: 'http://localhost:8080',
    });
  });

  it('should create a client instance', () => {
    expect(client).toBeDefined();
    expect(client).toBeInstanceOf(SandboxClient);
  });

  it('should have all required module properties', () => {
    expect(client.sandbox).toBeDefined();
    expect(client.shell).toBeDefined();
    expect(client.file).toBeDefined();
    expect(client.jupyter).toBeDefined();
    expect(client.nodejs).toBeDefined();
    expect(client.mcp).toBeDefined();
    expect(client.browser).toBeDefined();
    expect(client.code).toBeDefined();
    expect(client.util).toBeDefined();
    expect(client.skills).toBeDefined();
  });

  it('should allow custom environment configuration', () => {
    const customClient = new SandboxClient({
      environment: 'https://custom-sandbox.example.com',
    });
    expect(customClient).toBeDefined();
  });

  it('should allow custom headers', () => {
    const clientWithHeaders = new SandboxClient({
      environment: 'http://localhost:8080',
      headers: {
        'X-Custom-Header': 'test-value',
      },
    });
    expect(clientWithHeaders).toBeDefined();
  });

  it('should allow custom timeout', () => {
    const clientWithTimeout = new SandboxClient({
      environment: 'http://localhost:8080',
      timeoutInSeconds: 60,
    });
    expect(clientWithTimeout).toBeDefined();
  });
});
