import { describe, it, expect } from 'vitest';
import type { BodyInit, HeadersInit } from '../../src/types/fetch.js';

describe('Fetch Types', () => {
  describe('BodyInit type', () => {
    it('should accept string as valid BodyInit', () => {
      const body: BodyInit = 'test string';
      expect(typeof body).toBe('string');
    });

    it('should accept Buffer as valid BodyInit', () => {
      const body: BodyInit = Buffer.from('test');
      expect(Buffer.isBuffer(body)).toBe(true);
    });

    it('should accept Uint8Array as valid BodyInit', () => {
      const body: BodyInit = new Uint8Array([1, 2, 3]);
      expect(body).toBeInstanceOf(Uint8Array);
    });

    it('should accept URLSearchParams as valid BodyInit', () => {
      const body: BodyInit = new URLSearchParams('param=value');
      expect(body).toBeInstanceOf(URLSearchParams);
    });

    it('should accept FormData as valid BodyInit', () => {
      const body: BodyInit = new FormData();
      expect(body).toBeInstanceOf(FormData);
    });
  });

  describe('HeadersInit type', () => {
    it('should accept string array tuples as valid HeadersInit', () => {
      const headers: HeadersInit = [['Content-Type', 'application/json']];
      expect(Array.isArray(headers)).toBe(true);
      expect(headers[0]).toEqual(['Content-Type', 'application/json']);
    });

    it('should accept Record<string, string> as valid HeadersInit', () => {
      const headers: HeadersInit = { 'Content-Type': 'application/json' };
      expect(typeof headers).toBe('object');
      expect(headers['Content-Type']).toBe('application/json');
    });

    it('should accept Headers instance as valid HeadersInit', () => {
      const headers: HeadersInit = new Headers({
        'Content-Type': 'application/json',
      });
      expect(headers).toBeInstanceOf(Headers);
    });
  });
});
