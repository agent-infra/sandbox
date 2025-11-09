# @agent-infra/sandbox

Node.js/TypeScript SDK for AIO Sandbox integration, providing tools and interfaces for sandbox management and cloud provider integrations.

## Installation

```bash
npm install @agent-infra/sandbox
```

or with yarn:

```bash
yarn add @agent-infra/sandbox
```

or with pnpm:

```bash
pnpm add @agent-infra/sandbox
```

## Quick Start

### Basic Usage

```typescript
import { SandboxApiClient } from '@agent-infra/sandbox';

// Initialize the client
const client = new SandboxApiClient({
  environment: 'https://your-sandbox-api.com',
  // Add authentication if required
});

// Use the API
const result = await client.file.read({
  path: '/path/to/file',
});

console.log(result);
```

### Using Cloud Providers

The SDK includes provider implementations for managing sandboxes on different cloud platforms.

#### Volcengine Provider

```typescript
import { providers } from '@agent-infra/sandbox';

// Initialize Volcengine provider
const volcengineProvider = new providers.VolcengineProvider({
  accessKey: process.env.VOLCENGINE_ACCESS_KEY,
  secretKey: process.env.VOLCENGINE_SECRET_KEY,
  region: 'cn-beijing', // Optional, defaults to 'cn-beijing'
});

// Create a sandbox
const sandboxId = await volcengineProvider.createSandbox(
  'your-function-id',
  30 // timeout in minutes
);
console.log('Created sandbox:', sandboxId);

// Get sandbox details with APIG domains
const sandbox = await volcengineProvider.getSandbox(
  'your-function-id',
  sandboxId
);
console.log('Sandbox domains:', sandbox.domains);

// List all sandboxes for a function
const sandboxes = await volcengineProvider.listSandboxes('your-function-id');
console.log('Total sandboxes:', sandboxes.length);

// Delete a sandbox
await volcengineProvider.deleteSandbox('your-function-id', sandboxId);
console.log('Sandbox deleted');
```

#### Application Management

```typescript
// Create an application
const appId = await volcengineProvider.createApplication(
  'my-app',
  'my-gateway'
);

// Check application readiness
const [isReady, functionId] = await volcengineProvider.getApplicationReadiness(appId);
if (isReady) {
  console.log('Application is ready, function ID:', functionId);
}

// Get APIG domains for a function
const domains = await volcengineProvider.getApigDomains('your-function-id');
console.log('Available domains:', domains);
```

## Features

### Sandbox API Client

- **File Operations**: Read, write, search, and manage files
- **Shell Execution**: Execute shell commands and manage sessions
- **Browser Automation**: Control browser actions and retrieve information
- **Code Execution**: Execute code in various languages (Python, Node.js, Jupyter)
- **MCP Integration**: Execute MCP (Model Context Protocol) tools

### Cloud Providers

#### Volcengine Provider

- ✅ Sandbox lifecycle management (create, delete, get, list)
- ✅ Application deployment and monitoring
- ✅ APIG (API Gateway) domain management
- ✅ Automatic request signing with HMAC-SHA256
- ✅ Support for temporary credentials

#### Extensible Provider System

Create custom providers by extending the `BaseProvider` class:

```typescript
import { providers } from '@agent-infra/sandbox';

class MyCustomProvider extends providers.BaseProvider {
  async createSandbox(functionId: string, ...kwargs: any[]): Promise<any> {
    // Your implementation
  }

  async deleteSandbox(functionId: string, sandboxId: string, ...kwargs: any[]): Promise<any> {
    // Your implementation
  }

  async getSandbox(functionId: string, sandboxId: string, ...kwargs: any[]): Promise<any> {
    // Your implementation
  }

  async listSandboxes(functionId: string, ...kwargs: any[]): Promise<any> {
    // Your implementation
  }
}
```

## API Reference

### SandboxApiClient

The main client for interacting with the Sandbox API.

```typescript
const client = new SandboxApiClient({
  environment: string,          // API base URL
  timeout?: number,             // Request timeout in milliseconds
  headers?: Record<string, string>, // Custom headers
});
```

#### Available Modules

- `client.file` - File operations
- `client.shell` - Shell command execution
- `client.browser` - Browser automation
- `client.code` - Code execution
- `client.jupyter` - Jupyter notebook operations
- `client.nodejs` - Node.js specific operations
- `client.mcp` - MCP tool execution

### Providers

#### BaseProvider (Abstract)

Base class for all cloud provider implementations.

**Methods:**
- `createSandbox(functionId: string, ...kwargs: any[]): Promise<any>`
- `deleteSandbox(functionId: string, sandboxId: string, ...kwargs: any[]): Promise<any>`
- `getSandbox(functionId: string, sandboxId: string, ...kwargs: any[]): Promise<any>`
- `listSandboxes(functionId: string, ...kwargs: any[]): Promise<any>`

#### VolcengineProvider

Volcengine VEFAAS implementation.

**Constructor Options:**
```typescript
{
  accessKey: string;              // Volcengine access key ID
  secretKey: string;              // Volcengine secret access key
  region?: string;                // Region (default: 'cn-beijing')
  clientSideValidation?: boolean; // Enable validation (default: true)
}
```

**Additional Methods:**
- `createApplication(name: string, gatewayName: string): Promise<string | null>`
- `getApplicationReadiness(id: string): Promise<[boolean, string | null]>`
- `getApigDomains(functionId: string): Promise<DomainInfo[]>`

## Environment Variables

Configure Volcengine credentials using environment variables:

```bash
# Volcengine credentials (option 1)
VOLCENGINE_ACCESS_KEY=your-access-key
VOLCENGINE_SECRET_KEY=your-secret-key

# Volcengine credentials (option 2)
VOLC_ACCESSKEY=your-access-key
VOLC_SECRETKEY=your-secret-key
```

## TypeScript Support

This package is written in TypeScript and includes full type definitions. TypeScript 5.0+ is recommended.

```typescript
import type {
  SandboxApi,
  BaseClientOptions,
  BaseRequestOptions
} from '@agent-infra/sandbox';
```

## Examples

### Execute Shell Command

```typescript
const result = await client.shell.exec({
  command: 'ls -la',
  timeout: 5000,
});
console.log(result.stdout);
```

### Read File

```typescript
const fileContent = await client.file.read({
  path: '/path/to/file.txt',
});
console.log(fileContent.content);
```

### Browser Automation

```typescript
const browserInfo = await client.browser.info();
console.log('Browser:', browserInfo);

await client.browser.config({
  action: {
    type: 'click',
    selector: '#button',
  },
});
```

### Execute Python Code

```typescript
const result = await client.code.execute({
  code: 'print("Hello from sandbox!")',
  language: 'python',
});
console.log(result.output);
```

## Error Handling

```typescript
import { SandboxApiError, SandboxApiTimeoutError } from '@agent-infra/sandbox';

try {
  const result = await client.file.read({ path: '/nonexistent' });
} catch (error) {
  if (error instanceof SandboxApiTimeoutError) {
    console.error('Request timed out');
  } else if (error instanceof SandboxApiError) {
    console.error('API error:', error.statusCode, error.message);
  } else {
    console.error('Unexpected error:', error);
  }
}
```

## Development

### Project Structure

```
sdk/js/
├── src/              # TypeScript source code
│   ├── api/          # Generated API modules
│   ├── core/         # Core utilities
│   ├── errors/       # Error classes
│   ├── providers/    # Cloud provider implementations (custom code)
│   │   ├── base.ts       # Base provider interface
│   │   ├── volcengine.ts # Volcengine implementation
│   │   ├── sign.ts       # Request signing utilities
│   │   └── README.md     # Provider documentation
│   ├── BaseClient.ts # Base client implementation
│   ├── Client.ts     # Main API client
│   └── index.ts      # Package entry point
├── dist/             # Compiled JavaScript output (generated by build)
├── package.json      # Package configuration
└── tsconfig.json     # TypeScript configuration
```

### Building

The SDK uses TypeScript and compiles source code from `src/` to `dist/`:

```bash
npm run build
```

This will:
1. Compile TypeScript files from `src/` to JavaScript in `dist/`
2. Generate `.d.ts` type definition files
3. Generate source maps for debugging

### Testing

```bash
npm test

# With coverage
npm run test:coverage

# With UI
npm run test:ui
```

### Development Mode

```bash
npm run dev  # Watch mode with auto-rebuild
```

### Generating SDK

The base SDK code is generated using [Fern](https://buildwithfern.com/):

```bash
cd sdk/fern
fern generate --group nodejs-sdk --local
```

This generates TypeScript code from the OpenAPI specification into `src/`.
Custom providers in `src/providers/` are preserved via `.fernignore`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Adding Custom Providers

See [providers/README.md](./providers/README.md) for detailed information on implementing custom cloud providers.

## License

ISC

## Links

- [Repository](https://github.com/agent-infra/sandbox-sdk)
- [Issues](https://github.com/agent-infra/sandbox-sdk/issues)
- [Volcengine Documentation](https://www.volcengine.com/docs/)

## Support

For questions and support, please open an issue on GitHub.

---

**Version**: 1.0.0
**Node.js**: >=18.0.0
**TypeScript**: >=5.0.0
