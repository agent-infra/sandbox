import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock the sign module before importing VolcengineProvider
vi.mock('../../src/providers/sign', () => ({
  request: vi.fn(),
}));

import { VolcengineProvider } from '../../src/providers/volcengine.js';
import { request } from '../../src/providers/sign';

const mockedRequest = vi.mocked(request);

describe('VolcengineProvider error handling', () => {
  let provider: VolcengineProvider;

  beforeEach(() => {
    vi.clearAllMocks();
    provider = new VolcengineProvider({
      accessKey: 'test-access-key',
      secretKey: 'test-secret-key',
    });
  });

  it('createSandbox should throw errors instead of returning them', async () => {
    const testError = new Error('API connection failed');
    mockedRequest.mockRejectedValue(testError);

    await expect(provider.createSandbox('func-123', 60)).rejects.toThrow('API connection failed');
  });

  it('deleteSandbox should throw errors instead of returning them', async () => {
    const testError = new Error('Sandbox not found');
    mockedRequest.mockRejectedValue(testError);

    await expect(provider.deleteSandbox('func-123', 'sb-123')).rejects.toThrow('Sandbox not found');
  });

  it('getSandbox should throw errors instead of returning them', async () => {
    const testError = new Error('Network error');
    mockedRequest.mockRejectedValue(testError);

    await expect(provider.getSandbox('func-123', 'sb-123')).rejects.toThrow('Network error');
  });

  it('setSandboxTimeout should throw errors instead of returning them', async () => {
    const testError = new Error('Invalid timeout');
    mockedRequest.mockRejectedValue(testError);

    await expect(provider.setSandboxTimeout('func-123', 'sb-123', 120)).rejects.toThrow('Invalid timeout');
  });

  it('listSandboxes should throw errors instead of returning them', async () => {
    const testError = new Error('Permission denied');
    mockedRequest.mockRejectedValue(testError);

    await expect(provider.listSandboxes('func-123')).rejects.toThrow('Permission denied');
  });
});
