import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { VolcengineProvider } from './volcengine';

describe('VolcengineProvider E2E Tests - Sandbox Operations', () => {
  let provider: VolcengineProvider;
  let testFunctionId: string;
  let createdSandboxId: string;

  // Skip tests if required environment variables are not set
  const hasRequiredEnvVars =
    process.env.VOLCENGINE_ACCESS_KEY &&
    process.env.VOLCENGINE_SECRET_KEY &&
    process.env.VOLCENGINE_TEST_FUNCTION_ID;

  const describeE2E = hasRequiredEnvVars ? describe : describe.skip;

  beforeAll(() => {
    // Validate required environment variables
    if (hasRequiredEnvVars) {
      if (
        !process.env.VOLCENGINE_ACCESS_KEY ||
        !process.env.VOLCENGINE_SECRET_KEY
      ) {
        throw new Error(
          'VOLCENGINE_ACCESS_KEY and VOLCENGINE_SECRET_KEY environment variables are required for e2e tests',
        );
      }
      if (!process.env.VOLCENGINE_TEST_FUNCTION_ID) {
        throw new Error(
          'VOLCENGINE_TEST_FUNCTION_ID environment variable is required for e2e tests',
        );
      }
    }

    // Initialize provider with real credentials
    provider = new VolcengineProvider({
      accessKey: process.env.VOLCENGINE_ACCESS_KEY || '',
      secretKey: process.env.VOLCENGINE_SECRET_KEY || '',
      region: process.env.VOLCENGINE_REGION || 'cn-beijing',
    });

    testFunctionId = process.env.VOLCENGINE_TEST_FUNCTION_ID || '';
  });

  afterAll(async () => {
    // Cleanup: ensure sandbox is deleted if it was created
    if (createdSandboxId && hasRequiredEnvVars) {
      try {
        await provider.deleteSandbox(testFunctionId, createdSandboxId);
      } catch (error) {
        // Ignore cleanup errors
      }
    }
  });

  describeE2E('createSandbox', () => {
    it('should successfully create a sandbox with basic configuration', async () => {
      const result = await provider.createSandbox(testFunctionId, 60, {
        metadata: {
          test: 'e2e',
          timestamp: new Date().toISOString(),
        },
      });

      expect(result).toBeDefined();
      expect(result.ResponseMetadata).toBeDefined();
      expect(result.ResponseMetadata.Error).toBeUndefined();
      expect(result.Result).toBeDefined();
      expect(result.Result.SandboxId).toBeDefined();
      expect(typeof result.Result.SandboxId).toBe('string');

      // Save for cleanup and other tests
      createdSandboxId = result.Result.SandboxId;
    });

    it('should create sandbox with custom resources', async () => {
      const customConfig = {
        cpuMilli: 2000,
        memoryMB: 4096,
        metadata: {
          test: 'e2e-custom-resources',
        },
      };

      const result = await provider.createSandbox(
        testFunctionId,
        120,
        customConfig,
      );

      expect(result).toBeDefined();
      expect(result.Result).toBeDefined();
      expect(result.Result.SandboxId).toBeDefined();

      // Clean up this sandbox immediately
      if (result.Result?.SandboxId) {
        await provider.deleteSandbox(testFunctionId, result.Result.SandboxId);
      }
    });

    it('should handle invalid function ID gracefully', async () => {
      const invalidFunctionId = 'invalid-function-id';
      const result = await provider.createSandbox(invalidFunctionId, 60);

      expect(result).toBeDefined();
      // Expect an error response
      expect(result.ResponseMetadata?.Error).toBeDefined();
    });
  });

  describeE2E('getSandbox', () => {
    it('should retrieve sandbox details including domains', async () => {
      // Ensure sandbox is created first
      if (!createdSandboxId) {
        const createResult = await provider.createSandbox(testFunctionId, 60, {
          metadata: { test: 'e2e-get' },
        });
        createdSandboxId = createResult.Result?.SandboxId;
      }

      const result = await provider.getSandbox(
        testFunctionId,
        createdSandboxId,
      );

      expect(result).toBeDefined();
      expect(result.Result).toBeDefined();
      expect(result.Result.Id).toBe(createdSandboxId);
      expect(result.Result.Status).toBeDefined();
      expect(result.Result.domains).toBeDefined();
      expect(Array.isArray(result.Result.domains)).toBe(true);
      expect(result.Result.domains.length > 0).toBe(true);
    });

    it('should handle non-existent sandbox gracefully', async () => {
      const nonExistentId = 'non-existent-sandbox-id';
      const result = await provider.getSandbox(testFunctionId, nonExistentId);

      expect(result).toBeDefined();
      expect(result.ResponseMetadata?.Error).toBeDefined();
    });
  });

  describeE2E('listSandboxes', () => {
    it('should list all sandboxes for a function', async () => {
      const result = await provider.listSandboxes(testFunctionId);

      expect(result).toBeDefined();
      expect(result.sandboxes).toBeDefined();
      expect(Array.isArray(result.sandboxes)).toBe(true);
      expect(result.total).toBeDefined();
      expect(typeof result.total).toBe('number');
    });

    it('should support pagination parameters', async () => {
      const result = await provider.listSandboxes(testFunctionId, {
        pageNumber: 1,
        pageSize: 5,
      });

      expect(result).toBeDefined();
      expect(result.sandboxes).toBeDefined();
      expect(Array.isArray(result.sandboxes)).toBe(true);
      expect(result.sandboxes.length).toBeLessThanOrEqual(5);
    });

    it('should filter by metadata', async () => {
      const result = await provider.listSandboxes(testFunctionId, {
        metadata: { test: 'e2e' },
      });

      expect(result).toBeDefined();
      expect(result.sandboxes).toBeDefined();
      expect(Array.isArray(result.sandboxes)).toBe(true);
    });

    it('should include domains in sandbox list', async () => {
      const result = await provider.listSandboxes(testFunctionId);

      expect(result.sandboxes).toBeDefined();
      if (result.sandboxes.length > 0) {
        const firstSandbox = result.sandboxes[0];
        expect(firstSandbox.domains).toBeDefined();
        expect(Array.isArray(firstSandbox.domains)).toBe(true);
      }
    });
  });

  describeE2E('setSandboxTimeout', () => {
    it('should update sandbox timeout successfully', async () => {
      // Ensure sandbox is created first
      if (!createdSandboxId) {
        const createResult = await provider.createSandbox(testFunctionId, 60, {
          metadata: { test: 'e2e-timeout' },
        });
        createdSandboxId = createResult.Result?.SandboxId;
      }

      const newTimeout = 180; // 3 minutes
      const result = await provider.setSandboxTimeout(
        testFunctionId,
        createdSandboxId,
        newTimeout,
      );

      expect(result).toBeDefined();
      expect(result.ResponseMetadata).toBeDefined();
      expect(result.ResponseMetadata.Error).toBeUndefined();
    });

    it('should handle invalid timeout values', async () => {
      if (!createdSandboxId) {
        return; // Skip if no sandbox created
      }

      const invalidTimeout = -1;
      const result = await provider.setSandboxTimeout(
        testFunctionId,
        createdSandboxId,
        invalidTimeout,
      );

      expect(result).toBeDefined();
      // Might succeed or fail based on API validation
    });
  });

  describeE2E('deleteSandbox', () => {
    it('should successfully delete a sandbox', async () => {
      // Create a new sandbox specifically for deletion test
      const createResult = await provider.createSandbox(testFunctionId, 60, {
        metadata: { test: 'e2e-delete' },
      });
      const sandboxToDelete = createResult.Result?.SandboxId;

      expect(sandboxToDelete).toBeDefined();

      const deleteResult = await provider.deleteSandbox(
        testFunctionId,
        sandboxToDelete,
      );

      expect(deleteResult).toBeDefined();
      expect(deleteResult.ResponseMetadata).toBeDefined();
      expect(deleteResult.ResponseMetadata.Error).toBeUndefined();

      // Verify deletion by trying to get the sandbox
      const getResult = await provider.getSandbox(
        testFunctionId,
        sandboxToDelete,
      );
      expect(getResult.ResponseMetadata?.Error).toBeDefined();
    });

    it('should handle deletion of non-existent sandbox', async () => {
      const nonExistentId = 'non-existent-sandbox-id';
      const result = await provider.deleteSandbox(
        testFunctionId,
        nonExistentId,
      );

      expect(result).toBeDefined();
      // API might return success even for non-existent resources
    });
  });

  describeE2E('error handling', () => {
    it('should handle network errors gracefully', async () => {
      // Test with invalid credentials
      const invalidProvider = new VolcengineProvider({
        accessKey: 'invalid-access-key',
        secretKey: 'invalid-secret-key',
      });

      const result = await invalidProvider.createSandbox(testFunctionId, 60);
      expect(result).toBeDefined();
      expect(result.ResponseMetadata?.Error).toBeDefined();
    });

    it('should handle malformed request parameters', async () => {
      const result = await provider.createSandbox(testFunctionId, 60, {
        invalidField: 'should-be-ignored',
        metadata: 'invalid-metadata-type', // Should be object
      });

      expect(result).toBeDefined();
      // API should either ignore invalid fields or return error
    });
  });

  describeE2E('getApigDomains', () => {
    it('should retrieve APIG domains for a function', async () => {
      const domains = await provider.getApigDomains(testFunctionId);

      expect(domains).toBeDefined();
      expect(Array.isArray(domains)).toBe(true);

      if (domains.length > 0) {
        const firstDomain = domains[0];
        expect(firstDomain.domain).toBeDefined();
        expect(typeof firstDomain.domain).toBe('string');
      }
    });
  });
});
