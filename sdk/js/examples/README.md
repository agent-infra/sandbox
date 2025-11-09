# Sandbox SDK Examples

TypeScript examples demonstrating usage of the `@agent-infra/sandbox` SDK.

## Examples

### 1. simple-examples.ts
Basic, straightforward examples covering core SDK functionality:
- Getting sandbox context
- Executing shell commands
- Running Python code
- File operations (write, read, list, find, search)

### 2. basic-usage.ts
Fundamental sandbox operations:
- Sandbox context retrieval
- Shell command execution
- Python code execution
- File read/write operations
- Directory listing
- Python package information

### 3. volcengine-provider.ts
Volcengine cloud provider integration:
- Creating sandboxes with configuration
- Getting sandbox information
- Listing sandboxes
- Deleting sandboxes

### 4. advanced-usage.ts
Comprehensive demonstration of SDK features:
- File operations (read, write, list, search, find)
- Code execution (Python, JavaScript, Node.js)
- Shell commands
- Volcengine provider workflow

### 5. error-handling.ts
Error handling patterns and resilience strategies:
- Error type detection and handling
- Retry logic with exponential backoff
- Circuit breaker pattern
- Graceful degradation

## Running Examples

Install dependencies first:
```bash
npm install
```

Run individual examples:
```bash
npm run simple      # Simple examples
npm run basic       # Basic usage
npm run volcengine  # Volcengine provider
npm run advanced    # Advanced usage
npm run error       # Error handling
```

Run all examples:
```bash
npm run all
```

## Environment Variables

For Volcengine examples:
```bash
export VOLCENGINE_ACCESS_KEY=your-access-key
export VOLCENGINE_SECRET_KEY=your-secret-key
```

For custom sandbox URL:
```bash
export SANDBOX_API_URL=http://your-sandbox:8080
```

## Type Checking

Check TypeScript types:
```bash
npm run build
```

### Known SDK Issues

The SDK source has several TypeScript compilation errors that prevent clean builds:

1. **Missing errors module** (`./errors/index.js`): The `SandboxError` and `SandboxTimeoutError` classes are exported but the module doesn't exist
2. **HeadersIterator type**: DOM type `HeadersIterator` is not found
3. **Buffer/Blob compatibility**: Type incompatibility between Node.js Buffer and DOM Blob
4. **APIResponse error property**: Many client methods try to access `.error` on wrong response type

**These are SDK build issues, not example code issues.** All example TypeScript code is syntactically correct and will run properly with `tsx` even though `tsc` reports errors from the SDK internals.

To run examples without type checking:
```bash
npx tsx simple-examples.ts
npx tsx basic-usage.ts
# etc.
```

## Example Code Patterns

### API Response Pattern
All SDK methods return `APIResponse<T, E>` with `.ok` discriminator:

```typescript
const response = await client.file.readFile({ file: '/tmp/test.txt' });

if (response.ok) {
  console.log('Success:', response.body);
} else {
  console.error('Error:', response.error);
}
```

### Error Handling
```typescript
try {
  const response = await client.shell.execCommand({
    command: 'echo "Hello"'
  });
  
  if (!response.ok) {
    console.error('Command failed');
  }
} catch (error) {
  if (error instanceof Error) {
    console.error('Error:', error.message);
  }
}
```

### File Operations
```typescript
// Write
await client.file.writeFile({
  file: '/tmp/test.txt',
  content: 'Hello World'
});

// Read
const read = await client.file.readFile({ 
  file: '/tmp/test.txt' 
});

// List
const list = await client.file.listPath({ 
  path: '/tmp' 
});

// Search
const search = await client.file.searchInFile({
  file: '/tmp/test.txt',
  regex: 'pattern'
});

// Find
const find = await client.file.findFiles({
  path: '/tmp',
  glob: '*.txt'
});
```

### Code Execution
```typescript
// Python
await client.code.executeCode({
  language: 'python',
  code: 'print("Hello from Python!")'
});

// JavaScript
await client.code.executeCode({
  language: 'javascript',
  code: 'console.log("Hello from JS!")'
});

// Node.js
await client.nodejs.executeCode({
  code: 'console.log(process.version)'
});
```
