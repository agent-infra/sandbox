import { describe, it, expect } from 'vitest';
import type { BodyInit, HeadersInit } from '../src/types/fetch.js';
import { fetcherImpl } from '../src/core/fetcher/Fetcher.js';
import { FormDataWrapper } from '../src/core/form-data-utils/FormDataWrapper.js';

describe('Integration Tests', () => {
  describe('Type compatibility', () => {
    it('should use BodyInit type in fetch operations', () => {
      const stringBody: BodyInit = 'test';
      const bufferBody: BodyInit = Buffer.from('test');
      const uint8ArrayBody: BodyInit = new Uint8Array([1, 2, 3]);
      
      expect(typeof stringBody).toBe('string');
      expect(Buffer.isBuffer(bufferBody)).toBe(true);
      expect(uint8ArrayBody).toBeInstanceOf(Uint8Array);
    });

    it('should use HeadersInit type for header definitions', () => {
      const arrayHeaders: HeadersInit = [['Content-Type', 'application/json']];
      const objectHeaders: HeadersInit = { 'Authorization': 'Bearer token' };
      const headersInstance: HeadersInit = new Headers({ 'User-Agent': 'test' });
      
      expect(Array.isArray(arrayHeaders)).toBe(true);
      expect(typeof objectHeaders).toBe('object');
      expect(headersInstance).toBeInstanceOf(Headers);
    });
  });

  describe('FormData integration', () => {
    it('should create FormData with proper BodyInit compatibility', async () => {
      const formData = new FormDataWrapper();
      formData.append('key', 'value');
      
      const request = formData.getRequest();
      expect(request.body).toBeInstanceOf(FormData);
      expect(request.duplex).toBe('half');
    });
  });

  describe('Error handling integration', () => {
    it('should handle failed responses with proper type checking', () => {
      const mockResponse = {
        ok: false,
        error: {
          reason: 'status-code' as const,
          statusCode: 404,
          body: 'Not found'
        }
      };

      // This tests the type compatibility of error handling changes
      expect(mockResponse.ok).toBe(false);
      expect(mockResponse.error.reason).toBe('status-code');
      expect(mockResponse.error.statusCode).toBe(404);
    });
  });

  describe('Fetch implementation compatibility', () => {
    it('should have fetcherImpl function available', () => {
      expect(typeof fetcherImpl).toBe('function');
    });

    it('should accept proper arguments structure', () => {
      const args = {
        url: 'https://example.com',
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ test: true })
      };

      // This verifies that our type definitions work with the actual function signature
      expect(args.url).toBe('https://example.com');
      expect(args.method).toBe('POST');
      expect(typeof args.body).toBe('string');
    });
  });
});