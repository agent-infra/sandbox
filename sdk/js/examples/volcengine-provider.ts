import { providers } from '@agent-infra/sandbox';

// Initialize Volcengine provider with credentials from environment
const volcengine = new providers.VolcengineProvider({
  accessKey: process.env.VOLCENGINE_ACCESS_KEY || 'your-access-key',
  secretKey: process.env.VOLCENGINE_SECRET_KEY || 'your-secret-key',
  region: 'cn-beijing',
});

async function main() {
  const functionId = 'demo-function';
  let sandboxId: string | undefined;

  try {
    console.log('=== Volcengine Provider Example ===\n');

    // Step 1: Create sandbox with configuration
    console.log('1. Creating sandbox...');
    sandboxId = await volcengine.createSandbox(
      functionId,
      60, // 60 seconds timeout
      {
        region: 'cn-beijing',
        memory: 1024, // 1GB
        cpu: 2,
      },
    );

    console.log(`✓ Sandbox created with ID: ${sandboxId}\n`);

    // Step 2: Get sandbox information
    if (sandboxId) {
      console.log('2. Getting sandbox information...');
      const sandboxInfo = await volcengine.getSandbox(functionId, sandboxId);
      console.log('✓ Sandbox info:', sandboxInfo);
    }

    // Step 3: List all sandboxes for this function
    console.log('\n3. Listing all sandboxes...');
    const allSandboxes = await volcengine.listSandboxes(functionId);
    console.log(`✓ Found ${allSandboxes.length} sandbox(es) for ${functionId}`);

  } catch (error) {
    console.error(
      '❌ Error:',
      error instanceof Error ? error.message : error,
    );
    process.exit(1);
  } finally {
    // Cleanup: Delete the sandbox
    if (sandboxId) {
      try {
        console.log('\n4. Deleting sandbox...');
        await volcengine.deleteSandbox(functionId, sandboxId);
        console.log('✓ Sandbox deleted successfully');
      } catch (cleanupError) {
        console.error('⚠️  Cleanup failed:', cleanupError);
      }
    }
  }
}

main();
