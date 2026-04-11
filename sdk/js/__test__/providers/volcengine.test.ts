import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock the sign module before importing VolcengineProvider
vi.mock('../../src/providers/sign', () => ({
  request: vi.fn(),
}));

import { VolcengineProvider } from '../../src/providers/volcengine.js';
import { request } from '../../src/providers/sign';

const mockedRequest = vi.mocked(request);

describe('VolcengineProvider', () => {
  let provider: VolcengineProvider;

  beforeEach(() => {
    vi.clearAllMocks();
    provider = new VolcengineProvider({
      accessKey: 'test-access-key',
      secretKey: 'test-secret-key',
    });
  });

  describe('createSandbox - no duplicate keys from spread (Bug #3)', () => {
    it('should not include camelCase duplicates of PascalCase fields', async () => {
      mockedRequest.mockResolvedValue({ Result: { SandboxId: 'sb-123' } });

      await provider.createSandbox('func-123', 60, {
        metadata: { key: 'val' },
        cpuMilli: 1000,
        memoryMB: 512,
      });

      expect(mockedRequest).toHaveBeenCalledTimes(1);
      const bodyStr = mockedRequest.mock.calls[0][8] as string;
      const body = JSON.parse(bodyStr);

      // Should have PascalCase keys from explicit mapping
      expect(body.FunctionId).toBe('func-123');
      expect(body.CpuMilli).toBe(1000);
      expect(body.MemoryMB).toBe(512);

      // Should NOT have camelCase duplicates from spread
      expect(body.cpuMilli).toBeUndefined();
      expect(body.memoryMB).toBeUndefined();
      expect(body.metadata).toBeUndefined();
    });
  });

  describe('listSandboxes - no duplicate keys from spread (Bug #3)', () => {
    it('should not include camelCase duplicates of PascalCase fields', async () => {
      // First call is listSandboxes, second is getApigDomains (ListTriggers)
      mockedRequest
        .mockResolvedValueOnce({ Result: { Sandboxes: [], Total: 0 } })
        .mockResolvedValueOnce({ Result: { Items: [] } });

      await provider.listSandboxes('func-123', {
        sandboxId: 'sb-456',
        pageNumber: 2,
        pageSize: 20,
        status: 'running',
      });

      // First call is the actual listSandboxes request
      const bodyStr = mockedRequest.mock.calls[0][8] as string;
      const body = JSON.parse(bodyStr);

      // Should have PascalCase keys from explicit mapping
      expect(body.FunctionId).toBe('func-123');
      expect(body.SandboxId).toBe('sb-456');
      expect(body.PageNumber).toBe(2);
      expect(body.PageSize).toBe(20);
      expect(body.Status).toBe('running');

      // Should NOT have camelCase duplicates from spread
      expect(body.sandboxId).toBeUndefined();
      expect(body.pageNumber).toBeUndefined();
      expect(body.pageSize).toBeUndefined();
      expect(body.status).toBeUndefined();
    });
  });

  describe('error handling - rethrow instead of swallow (Bug #4)', () => {
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
});
