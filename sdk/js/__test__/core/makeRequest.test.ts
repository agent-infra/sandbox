import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { makeRequest } from '../../src/core/fetcher/makeRequest.js';

describe('makeRequest', () => {
  const mockFetch = vi.fn();
  const mockUrl = 'https://api.example.com/test';

  beforeEach(() => {
    mockFetch.mockClear();
    mockFetch.mockResolvedValue(new Response('{}', { status: 200 }));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it.each(['reject', 'throw'] as const)('clears the timeout when fetch fails by %s', async (failure) => {
    vi.useFakeTimers();
    const error = new TypeError('network failure');
    mockFetch.mockImplementationOnce(() => {
      if (failure === 'throw') throw error;
      return Promise.reject(error);
    });

    await expect(makeRequest(mockFetch, mockUrl, 'GET', {}, undefined, 60_000)).rejects.toBe(error);
    expect(vi.getTimerCount()).toBe(0);
  });

  it('clears the timeout when the caller aborts the request', async () => {
    vi.useFakeTimers();
    const controller = new AbortController();
    const reason = new Error('cancelled by caller');
    mockFetch.mockImplementationOnce((_url, init) => new Promise((_resolve, reject) => {
      init.signal.addEventListener('abort', () => reject(init.signal.reason), { once: true });
    }));

    const pending = makeRequest(mockFetch, mockUrl, 'GET', {}, undefined, 60_000, controller.signal);
    const rejection = expect(pending).rejects.toBe(reason);
    controller.abort(reason);

    await rejection;
    expect(vi.getTimerCount()).toBe(0);
  });

  it('clears the timeout after a successful response', async () => {
    vi.useFakeTimers();
    const response = new Response('{}', { status: 200 });
    mockFetch.mockResolvedValueOnce(response);

    await expect(makeRequest(mockFetch, mockUrl, 'GET', {}, undefined, 60_000)).resolves.toBe(response);
    expect(vi.getTimerCount()).toBe(0);
  });

  it('still aborts an in-flight request when its timeout expires', async () => {
    vi.useFakeTimers();
    mockFetch.mockImplementationOnce((_url, init) => new Promise((_resolve, reject) => {
      init.signal.addEventListener('abort', () => reject(init.signal.reason), { once: true });
    }));

    const pending = makeRequest(mockFetch, mockUrl, 'GET', {}, undefined, 1000);
    const rejection = expect(pending).rejects.toBe('timeout');
    await vi.advanceTimersByTimeAsync(1000);

    await rejection;
    expect(vi.getTimerCount()).toBe(0);
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
