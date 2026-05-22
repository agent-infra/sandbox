import { describe, expect, it } from 'vitest';
import { createRequestUrl } from '../../src/core/fetcher/createRequestUrl.js';

describe('createRequestUrl', () => {
  it('adds query parameters to URLs without existing query parameters', () => {
    expect(createRequestUrl('https://api.example.com/v1/items', { limit: 10 })).toBe(
      'https://api.example.com/v1/items?limit=10',
    );
  });

  it('appends query parameters to URLs with existing query parameters', () => {
    expect(createRequestUrl('https://api.example.com/v1/items?jwt=token', { limit: 10 })).toBe(
      'https://api.example.com/v1/items?jwt=token&limit=10',
    );
  });

  it('does not add an extra separator when the URL ends with one', () => {
    expect(createRequestUrl('https://api.example.com/v1/items?jwt=token&', { limit: 10 })).toBe(
      'https://api.example.com/v1/items?jwt=token&limit=10',
    );
  });

  it('places added query parameters before the URL fragment', () => {
    expect(createRequestUrl('https://api.example.com/v1/items?jwt=token#section', { limit: 10 })).toBe(
      'https://api.example.com/v1/items?jwt=token&limit=10#section',
    );
  });
});
