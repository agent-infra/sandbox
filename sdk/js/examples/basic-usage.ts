import { SandboxClient } from '@agent-infra/sandbox';

// Initialize the client
const client = new SandboxClient({
  environment: process.env.SANDBOX_API_URL || 'http://localhost:8080',
});

async function main() {
  try {
    console.log('=== Basic Sandbox Operations ===\n');

    // Get sandbox context
    console.log('1. Getting sandbox context...');
    const contextResponse = await client.sandbox.getContext();

    if (contextResponse.ok) {
      console.log('✓ Sandbox context:', contextResponse.body);
    } else {
      console.log('✗ Failed to get context');
    }

    // Execute shell command
    console.log('\n2. Executing shell command...');
    const shellResponse = await client.shell.execCommand({
      command: 'echo "Hello from sandbox!"',
    });

    if (shellResponse.ok) {
      console.log('✓ Command executed:', shellResponse.body);
    }

    // Execute Python code
    console.log('\n3. Executing Python code...');
    const pythonResponse = await client.code.executeCode({
      language: 'python',
      code: 'print("Hello from Python!")\nprint(2 + 2)',
    });

    if (pythonResponse.ok) {
      console.log('✓ Python executed:', pythonResponse.body);
    }

    // Write and read a file
    console.log('\n4. File operations...');
    const writeResponse = await client.file.writeFile({
      file: '/tmp/example.txt',
      content: 'Hello from TypeScript SDK!',
    });

    if (writeResponse.ok) {
      console.log('✓ File written');

      const readResponse = await client.file.readFile({
        file: '/tmp/example.txt',
      });

      if (readResponse.ok) {
        console.log('✓ File content:', readResponse.body);
      }
    }

    // List directory
    console.log('\n5. Listing directory...');
    const listResponse = await client.file.listPath({
      path: '/tmp',
    });

    if (listResponse.ok) {
      console.log('✓ Directory listing:', listResponse.body);
    }

    // Get Python packages
    console.log('\n6. Getting Python packages...');
    const packagesResponse = await client.sandbox.getPythonPackages();

    if (packagesResponse.ok) {
      console.log('✓ Python packages available');
    }

  } catch (error) {
    console.error('❌ Error:', error instanceof Error ? error.message : error);
    process.exit(1);
  }
}

main();
