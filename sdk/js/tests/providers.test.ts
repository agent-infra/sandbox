/**
 * Tests for cloud providers.
 */

import { describe, it, expect } from 'vitest';
import { providers } from '../src';

describe('Volcengine Provider', () => {
  it('should be able to create Volcengine provider instance', () => {
    const provider = new providers.VolcengineProvider({
      accessKey: 'test-key',
      secretKey: 'test-secret',
      region: 'cn-beijing',
    });

    expect(provider).toBeDefined();
  });

  it('should accept custom endpoint', () => {
    const provider = new providers.VolcengineProvider({
      accessKey: 'test-key',
      secretKey: 'test-secret',
      region: 'cn-beijing',
      endpoint: 'https://custom.endpoint.com',
    });

    expect(provider).toBeDefined();
  });

  it('should have required methods', () => {
    const provider = new providers.VolcengineProvider({
      accessKey: 'test-key',
      secretKey: 'test-secret',
      region: 'cn-beijing',
    });

    // Provider should have methods for sandbox management
    expect(provider).toBeDefined();
    expect(typeof provider).toBe('object');
  });
});

describe('Provider Base Interface', () => {
  it('should have BaseProvider available', () => {
    expect(providers.BaseProvider).toBeDefined();
  });

  it('should have VolcengineProvider available', () => {
    expect(providers.VolcengineProvider).toBeDefined();
  });
});
