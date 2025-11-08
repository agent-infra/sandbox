# Providers

This directory contains cloud provider implementations for sandbox management.

## Available Providers

### Volcengine Provider

The `VolcengineProvider` class provides integration with Volcengine VEFAAS (Volcengine Function as a Service) for managing sandbox instances.

#### Installation

```bash
npm install @agent-infra/sandbox
```

#### Usage

```typescript
import { VolcengineProvider } from '@agent-infra/sandbox';

// Initialize the provider
const provider = new VolcengineProvider(
    'your-access-key',
    'your-secret-key',
    'cn-beijing',  // region (optional, defaults to 'cn-beijing')
    true           // client-side validation (optional, defaults to true)
);

// Create a sandbox
const sandboxId = await provider.createSandbox('function-id', {
    timeout: 30  // timeout in minutes
});

// Get sandbox details
const sandbox = await provider.getSandbox('function-id', sandboxId);

// List all sandboxes
const sandboxes = await provider.listSandboxes('function-id');

// Delete a sandbox
await provider.deleteSandbox('function-id', sandboxId);
```

#### Environment Variables

You can set credentials via environment variables:

```bash
export VOLCENGINE_ACCESS_KEY=your-access-key
export VOLCENGINE_SECRET_KEY=your-secret-key
# Or alternatively:
export VOLC_ACCESSKEY=your-access-key
export VOLC_SECRETKEY=your-secret-key
```

#### API Reference

##### Constructor

```typescript
constructor(
    accessKey: string,
    secretKey: string,
    region?: string,
    clientSideValidation?: boolean
)
```

##### Methods

- **`createSandbox(functionId: string, kwargs?: Record<string, any>): Promise<SandboxResponse>`**

  Create a new sandbox instance.

  Parameters:
  - `functionId`: The function ID for the sandbox
  - `kwargs.timeout`: Timeout in minutes (default: 30)

  Returns: Sandbox ID or error

- **`deleteSandbox(functionId: string, sandboxId: string, kwargs?: Record<string, any>): Promise<SandboxResponse>`**

  Delete an existing sandbox instance.

- **`getSandbox(functionId: string, sandboxId: string, kwargs?: Record<string, any>): Promise<SandboxResponse>`**

  Get details of an existing sandbox instance including domains.

- **`listSandboxes(functionId: string, kwargs?: Record<string, any>): Promise<SandboxResponse>`**

  List all sandbox instances for a function.

- **`createApplication(name: string, gatewayName: string, kwargs?: Record<string, any>): Promise<string | null>`**

  Create a VEFAAS application.

- **`getApplicationReadiness(id: string, kwargs?: Record<string, any>): Promise<[boolean, string | null]>`**

  Check if an application is ready and get its function ID.

- **`getApigDomains(functionId: string): Promise<Array<{ domain: string; type?: string }>>`**

  Get APIG domains for a function.

## Implementation Details

### API Signing

The Volcengine provider uses HMAC-SHA256 signature authentication. The signing process is implemented in `sign.ts` and follows the Volcengine API v4 signing protocol.

### Comparison with Python SDK

This Node.js implementation provides feature parity with the Python SDK (`sdk/python/agent_sandbox/providers/volcengine.py`). The main difference is that:

- **Python**: Uses the official `volcenginesdkvefaas` SDK
- **Node.js**: Implements direct API calls as the Volcengine Node.js SDK doesn't include a VEFAAS client

Both implementations provide the same functionality and API interface.

## Creating Custom Providers

To create a custom provider, extend the `BaseProvider` class:

```typescript
import { BaseProvider, SandboxResponse } from './base';

export class CustomProvider extends BaseProvider {
    async createSandbox(functionId: string, kwargs?: Record<string, any>): Promise<SandboxResponse> {
        // Your implementation
    }

    async deleteSandbox(functionId: string, sandboxId: string, kwargs?: Record<string, any>): Promise<SandboxResponse> {
        // Your implementation
    }

    async getSandbox(functionId: string, sandboxId: string, kwargs?: Record<string, any>): Promise<SandboxResponse> {
        // Your implementation
    }

    async listSandboxes(functionId: string, kwargs?: Record<string, any>): Promise<SandboxResponse> {
        // Your implementation
    }
}
```

## License

Apache-2.0
