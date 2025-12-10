import { describe, it, expect, vi } from 'vitest';
import { fetcherImpl, type FetchFunction } from '../../src/core/fetcher/Fetcher.js';

// Mock the getFetchFn function
vi.mock('../../src/core/fetcher/getFetchFn.js', () => ({
  getFetchFn: () => vi.fn().mockResolvedValue(new Response('{}', { status: 200 }))
}));

describe('Fetcher', () => {
  describe('fetcherImpl', () => {
    it('should be a function', () => {
      expect(typeof fetcherImpl).toBe('function');
    });

    it('should accept Fetcher.Args and return Promise<APIResponse>', async () => {
      const args = {
        url: 'https://api.example.com/test',
        method: 'GET'
      };

      const result = await fetcherImpl(args);
      expect(result).toBeDefined();
      expect(result.ok).toBeDefined();
    });
  });

  describe('FetchFunction type', () => {
    it('should be defined as a type', () => {
      const fetchFn: FetchFunction = fetcherImpl;
      expect(typeof fetchFn).toBe('function');
    });
  });
});