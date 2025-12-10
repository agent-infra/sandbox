import { describe, it, expect, vi, beforeEach } from 'vitest';
import { makeRequest } from '../../src/core/fetcher/makeRequest.js';

describe('makeRequest', () => {
  const mockFetch = vi.fn();
  const mockUrl = 'https://api.example.com/test';

  beforeEach(() => {
    mockFetch.mockClear();
    mockFetch.mockResolvedValue(new Response('{}', { status: 200 }));
  });

  it('should make a request with basic parameters', async () => {
    await makeRequest(mockFetch, mockUrl, 'GET', {}, undefined);

    expect(mockFetch).toHaveBeenCalledWith(mockUrl, expect.objectContaining({
      method: 'GET',
      headers: {},
      body: undefined,
      signal: expect.any(AbortSignal),
    }));
  });

  it('should make a request with custom headers', async () => {
    const headers = { 'Content-Type': 'application/json' };
    await makeRequest(mockFetch, mockUrl, 'POST', headers, undefined);

    expect(mockFetch).toHaveBeenCalledWith(mockUrl, expect.objectContaining({
      method: 'POST',
      headers,
      body: undefined,
      signal: expect.any(AbortSignal),
    }));
  });

  it('should make a request with body', async () => {
    const body = JSON.stringify({ test: 'data' });
    await makeRequest(mockFetch, mockUrl, 'POST', {}, body);

    expect(mockFetch).toHaveBeenCalledWith(mockUrl, expect.objectContaining({
      method: 'POST',
      headers: {},
      body,
      signal: expect.any(AbortSignal),
    }));
  });

  it('should handle different BodyInit types', async () => {
    // Test with Buffer
    const bufferBody = Buffer.from('test data');
    await makeRequest(mockFetch, mockUrl, 'POST', {}, bufferBody);

    expect(mockFetch).toHaveBeenCalledWith(mockUrl, expect.objectContaining({
      method: 'POST',
      headers: {},
      body: bufferBody,
      signal: expect.any(AbortSignal),
    }));

    // Test with Uint8Array
    mockFetch.mockClear();
    const uint8ArrayBody = new Uint8Array([1, 2, 3]);
    await makeRequest(mockFetch, mockUrl, 'POST', {}, uint8ArrayBody);

    expect(mockFetch).toHaveBeenCalledWith(mockUrl, expect.objectContaining({
      method: 'POST',
      headers: {},
      body: uint8ArrayBody,
      signal: expect.any(AbortSignal),
    }));
  });

  it('should handle timeout', async () => {
    const timeoutMs = 1000;
    await makeRequest(mockFetch, mockUrl, 'GET', {}, undefined, timeoutMs);

    expect(mockFetch).toHaveBeenCalledWith(mockUrl, expect.objectContaining({
      method: 'GET',
      headers: {},
      body: undefined,
      signal: expect.any(AbortSignal),
    }));
  });

  it('should handle abort signal', async () => {
    const controller = new AbortController();
    await makeRequest(mockFetch, mockUrl, 'GET', {}, undefined, undefined, controller.signal);

    expect(mockFetch).toHaveBeenCalledWith(mockUrl, expect.objectContaining({
      method: 'GET',
      headers: {},
      body: undefined,
      signal: expect.any(AbortSignal),
    }));
  });
});
