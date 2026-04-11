import { describe, it, expect } from 'vitest';
import { createRequestUrl } from '../../src/core/fetcher/createRequestUrl.js';

describe('createRequestUrl', () => {
  it('should append query string with ? when baseUrl has no query params', () => {
    const result = createRequestUrl('https://api.example.com/v1', { key: 'value' });
    expect(result).toBe('https://api.example.com/v1?key=value');
  });

  it('should append query string with & when baseUrl already has query params', () => {
    const result = createRequestUrl('https://api.example.com/v1?existing=param', { key: 'value' });
    expect(result).toBe('https://api.example.com/v1?existing=param&key=value');
  });

  it('should return baseUrl unchanged when no query parameters provided', () => {
    const result = createRequestUrl('https://api.example.com/v1');
    expect(result).toBe('https://api.example.com/v1');
  });

  it('should return baseUrl unchanged when query parameters are empty', () => {
    const result = createRequestUrl('https://api.example.com/v1', {});
    expect(result).toBe('https://api.example.com/v1');
  });

  it('should handle baseUrl with existing ? but no additional params', () => {
    const result = createRequestUrl('https://api.example.com/v1?existing=param');
    expect(result).toBe('https://api.example.com/v1?existing=param');
  });

  it('should not produce double ? when baseUrl has query params', () => {
    const result = createRequestUrl('https://api.example.com/v1?a=1', { b: '2' });
    expect(result).not.toContain('??');
    expect(result).toBe('https://api.example.com/v1?a=1&b=2');
  });

  it('should handle multiple query parameters', () => {
    const result = createRequestUrl('https://api.example.com/v1', { a: '1', b: '2' });
    expect(result).toContain('a=1');
    expect(result).toContain('b=2');
    expect(result.indexOf('?')).toBe(result.lastIndexOf('?'));
  });
});
