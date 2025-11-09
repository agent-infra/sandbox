import { SandboxClient } from '@agent-infra/sandbox';

/**
 * Simple, working examples that demonstrate the actual SDK API
 */

const client = new SandboxClient({
  environment: process.env.SANDBOX_API_URL || 'http://localhost:8080',
});

async function main() {
  console.log('=== Sandbox SDK Examples ===\n');

  // 1. Get sandbox context
  console.log('1. Getting sandbox context...');
  const context = await client.sandbox.getContext();
  if (context.ok) {
    console.log('✓ Context:', context.body);
  }

  // 2. Execute shell command
  console.log('\n2. Executing shell command...');
  const shell = await client.shell.execCommand({
    command: 'echo "Hello from sandbox!"',
  });
  if (shell.ok) {
    console.log('✓ Shell:', shell.body);
  }

  // 3. Execute Python code
  console.log('\n3. Executing Python code...');
  const python = await client.code.executeCode({
    language: 'python',
    code: 'print("Hello from Python!"); print(2 + 2)',
  });
  if (python.ok) {
    console.log('✓ Python:', python.body);
  }

  // 4. Write and read a file
  console.log('\n4. File operations...');
  const write = await client.file.writeFile({
    file: '/tmp/test.txt',
    content: 'Hello from SDK!',
  });
  if (write.ok) {
    console.log('✓ File written');

    const read = await client.file.readFile({ file: '/tmp/test.txt' });
    if (read.ok) {
      console.log('✓ File content:', read.body);
    }
  }

  // 5. List directory
  console.log('\n5. Listing directory...');
  const list = await client.file.listPath({ path: '/tmp' });
  if (list.ok) {
    console.log('✓ Directory:', list.body);
  }

  // 6. Find files
  console.log('\n6. Finding files...');
  const find = await client.file.findFiles({
    path: '/tmp',
    glob: '*.txt',
  });
  if (find.ok) {
    console.log('✓ Found files:', find.body);
  }

  // 7. Search in file
  console.log('\n7. Searching in file...');
  const search = await client.file.searchInFile({
    file: '/tmp/test.txt',
    regex: 'SDK',
  });
  if (search.ok) {
    console.log('✓ Search results:', search.body);
  }

  console.log('\n✅ All examples completed!\n');
}

main().catch((error) => {
  console.error('❌ Error:', error);
  process.exit(1);
});
