import { describe, it, expect } from 'vitest';

describe('ESModule Import', () => {
  it('should import SandboxClient correctly', async () => {
    const { SandboxClient } = await import('../dist/esm/index.mjs');
    expect(SandboxClient).toBeDefined();
    expect(typeof SandboxClient).toBe('function');
  });

  it('should import SandboxApi correctly', async () => {
    const { SandboxApi } = await import('../dist/esm/index.mjs');
    expect(SandboxApi).toBeDefined();
    expect(typeof SandboxApi).toBe('object');
  });

  it('should import providers correctly', async () => {
    const { providers } = await import('../dist/esm/index.mjs');
    expect(providers).toBeDefined();
    expect(typeof providers).toBe('object');
  });

  it('should be able to instantiate SandboxClient', async () => {
    const { SandboxClient } = await import('../dist/esm/index.mjs');
    const client = new SandboxClient({ baseUrl: 'http://localhost:8080' });
    expect(client).toBeInstanceOf(SandboxClient);
  });
});
