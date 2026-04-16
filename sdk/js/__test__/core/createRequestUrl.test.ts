import { describe, it, expect } from 'vitest';
import { createRequestUrl } from '../../src/core/fetcher/createRequestUrl.js';

describe('createRequestUrl', () => {
  it('should return baseUrl unchanged when no query parameters', () => {
    expect(createRequestUrl('https://api.example.com/v1')).toBe('https://api.example.com/v1');
  });

  it('should append query string with ? when baseUrl has no query params', () => {
    const result = createRequestUrl('https://api.example.com/v1', { key: 'value' });
    expect(result).toBe('https://api.example.com/v1?key=value');
  });

  it('should append query string with & when baseUrl already has query params', () => {
    const result = createRequestUrl('https://api.example.com/v1?token=abc', { key: 'value' });
    expect(result).toBe('https://api.example.com/v1?token=abc&key=value');
  });

  it('should handle empty query parameters', () => {
    const result = createRequestUrl('https://api.example.com/v1?token=abc', {});
    expect(result).toBe('https://api.example.com/v1?token=abc');
  });
});
