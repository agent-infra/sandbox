import { SandboxClient, providers } from '@agent-infra/sandbox';

/**
 * Advanced usage examples demonstrating:
 * - File operations (read, write, list, search, find)
 * - Code execution (Python, JavaScript, Node.js)
 * - Shell commands
 * - Volcengine provider integration
 */

const client = new SandboxClient({
  environment: process.env.SANDBOX_API_URL || 'http://localhost:8080',
});

const volcengine = new providers.VolcengineProvider({
  accessKey: process.env.VOLCENGINE_ACCESS_KEY || 'your-access-key',
  secretKey: process.env.VOLCENGINE_SECRET_KEY || 'your-secret-key',
  region: 'cn-beijing',
});

/**
 * File operations example
 */
async function fileOperations() {
  console.log('=== File Operations ===\n');

  // Write a file
  console.log('1. Writing a file...');
  const writeResponse = await client.file.writeFile({
    file: '/tmp/test.txt',
    content: 'Hello from TypeScript SDK!',
  });

  if (writeResponse.ok) {
    console.log('✓ File written');
  }

  // Read the file
  console.log('\n2. Reading the file...');
  const readResponse = await client.file.readFile({ file: '/tmp/test.txt' });

  if (readResponse.ok) {
    console.log('✓ File content:', readResponse.body);
  }

  // List directory
  console.log('\n3. Listing /tmp directory...');
  const listResponse = await client.file.listPath({ path: '/tmp' });

  if (listResponse.ok) {
    console.log('✓ Directory contents:', listResponse.body);
  }

  // Search in file (regex pattern)
  console.log('\n4. Searching in file...');
  const searchResponse = await client.file.searchInFile({
    file: '/tmp/test.txt',
    regex: 'TypeScript',
  });

  if (searchResponse.ok) {
    console.log('✓ Search results:', searchResponse.body);
  }

  // Find files (glob pattern)
  console.log('\n5. Finding files...');
  const findResponse = await client.file.findFiles({
    path: '/tmp',
    glob: '*.txt',
  });

  if (findResponse.ok) {
    console.log('✓ Found files:', findResponse.body, '\n');
  }
}

/**
 * Code execution examples
 */
async function codeExecution() {
  console.log('=== Code Execution ===\n');

  // Execute Python code
  console.log('1. Executing Python code...');
  const pythonResponse = await client.code.executeCode({
    language: 'python',
    code: `
import sys
import json

result = {
    "python_version": sys.version.split()[0],
    "sum": sum(range(100)),
    "squares": [i**2 for i in range(5)]
}

print(json.dumps(result, indent=2))
    `.trim(),
  });

  if (pythonResponse.ok) {
    console.log('✓ Python output:', pythonResponse.body);
  }

  // Execute JavaScript code
  console.log('\n2. Executing JavaScript code...');
  const jsResponse = await client.code.executeCode({
    language: 'javascript',
    code: `
const data = Array.from({ length: 5 }, (_, i) => ({
  index: i,
  value: i * 10
}));

console.log(JSON.stringify(data, null, 2));
    `.trim(),
  });

  if (jsResponse.ok) {
    console.log('✓ JavaScript output:', jsResponse.body);
  }

  // Execute Node.js code
  console.log('\n3. Executing Node.js code...');
  const nodeResponse = await client.nodejs.executeCode({
    code: `
const os = require('os');

console.log('Platform:', os.platform());
console.log('Node version:', process.version);
console.log('Architecture:', os.arch());
    `.trim(),
  });

  if (nodeResponse.ok) {
    console.log('✓ Node.js output:', nodeResponse.body, '\n');
  }
}

/**
 * Shell command execution
 */
async function shellCommands() {
  console.log('=== Shell Commands ===\n');

  // Execute simple command
  console.log('1. Running ls command...');
  const lsResponse = await client.shell.execCommand({
    command: 'ls -la /tmp | head -5',
  });

  if (lsResponse.ok) {
    console.log('✓ Output:', lsResponse.body);
  }

  // Execute command with pipes
  console.log('\n2. Running piped command...');
  const pipeResponse = await client.shell.execCommand({
    command: 'echo "Hello World" | tr "a-z" "A-Z"',
  });

  if (pipeResponse.ok) {
    console.log('✓ Output:', pipeResponse.body, '\n');
  }
}

/**
 * Utility operations
 */
async function utilityOperations() {
  console.log('=== Utility Operations ===\n');

  // Get code info
  console.log('1. Getting code information...');
  const infoResponse = await client.code.getInfo();

  if (infoResponse.ok) {
    console.log('✓ Code info:', infoResponse.body, '\n');
  }
}

/**
 * Combined workflow: Volcengine + SandboxClient
 */
async function combinedWorkflow() {
  console.log('=== Combined Workflow (Volcengine + SandboxClient) ===\n');

  let sandboxId: string | undefined;

  try {
    // Create sandbox with Volcengine
    console.log('1. Creating sandbox with Volcengine...');
    sandboxId = await volcengine.createSandbox('demo-function', 60);
    console.log(`✓ Sandbox created: ${sandboxId}`);

    // Get sandbox info
    if (sandboxId) {
      console.log('\n2. Getting sandbox info...');
      const sandboxInfo = await volcengine.getSandbox('demo-function', sandboxId);
      console.log('✓ Sandbox info:', sandboxInfo);
    }

    // List all sandboxes
    console.log('\n3. Listing all sandboxes...');
    const sandboxes = await volcengine.listSandboxes('demo-function');
    console.log('✓ Total sandboxes:', sandboxes.length);

  } catch (error) {
    console.error('❌ Workflow error:', error);
  } finally {
    // Cleanup
    if (sandboxId) {
      try {
        console.log('\n4. Cleaning up sandbox...');
        await volcengine.deleteSandbox('demo-function', sandboxId);
        console.log('✓ Sandbox deleted\n');
      } catch (cleanupError) {
        console.error('⚠️  Cleanup failed:', cleanupError);
      }
    }
  }
}

async function main() {
  try {
    await fileOperations();
    await codeExecution();
    await shellCommands();
    await utilityOperations();

    // Only run Volcengine workflow if credentials are provided
    if (process.env.VOLCENGINE_ACCESS_KEY && process.env.VOLCENGINE_SECRET_KEY) {
      await combinedWorkflow();
    } else {
      console.log('=== Skipping Volcengine Workflow ===');
      console.log('Set VOLCENGINE_ACCESS_KEY and VOLCENGINE_SECRET_KEY to run\n');
    }

  } catch (error) {
    console.error('❌ Error:', error instanceof Error ? error.message : error);
    process.exit(1);
  }
}

main();
