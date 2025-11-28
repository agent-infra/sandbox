import { describe, it, expect } from 'vitest';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);

describe('CommonJS Import', () => {
  it('should import SandboxClient correctly', () => {
    const { SandboxClient } = require('../dist/cjs/index.js');
    expect(SandboxClient).toBeDefined();
    expect(typeof SandboxClient).toBe('function');
  });

  it('should import SandboxApi correctly', () => {
    const { SandboxApi } = require('../dist/cjs/index.js');
    expect(SandboxApi).toBeDefined();
    expect(typeof SandboxApi).toBe('object');
  });

  it('should import providers correctly', () => {
    const { providers } = require('../dist/cjs/index.js');
    expect(providers).toBeDefined();
    expect(typeof providers).toBe('object');
  });

  it('should be able to instantiate SandboxClient', () => {
    const { SandboxClient } = require('../dist/cjs/index.js');
    const client = new SandboxClient({ baseUrl: 'http://localhost:8080' });
    expect(client).toBeInstanceOf(SandboxClient);
  });
});
