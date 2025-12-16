# Sandbox Providers

This directory contains custom cloud provider implementations for sandbox management.

## Volcengine Provider

The Volcengine provider integrates with Volcengine VEFAAS (Volcengine Function as a Service) API to manage sandbox instances.

### Installation

The provider is included in the `@agent-infra/sandbox` package. Install it via npm:

```bash
npm install @agent-infra/sandbox
```

### Usage

```typescript
import { providers } from '@agent-infra/sandbox';

// Initialize the Volcengine provider
const provider = new providers.VolcengineProvider({
  accessKey: 'your-access-key',
  secretKey: 'your-secret-key',
  region: 'cn-beijing', // Optional, defaults to 'cn-beijing'
  clientSideValidation: true, // Optional, defaults to true
});

// Create a sandbox
const sandboxId = await provider.createSandbox('function-id', 30);

// Get sandbox details
const sandbox = await provider.getSandbox('function-id', sandboxId);

// List all sandboxes
const sandboxes = await provider.listSandboxes('function-id');

// Delete a sandbox
await provider.deleteSandbox('function-id', sandboxId);

// Set sandbox timeout
await provider.setSandboxTimeout('function-id', sandboxId, 120);
```

### Application Management

The provider also supports application lifecycle management:

```typescript
// Create an application
const applicationId = await provider.createApplication('app-name', 'gateway-name');

// Check application readiness
const [isReady, functionId] = await provider.getApplicationReadiness(applicationId);

// Get APIG domains for a function
const domains = await provider.getApigDomains('function-id');
```

## Custom Providers

To create a custom provider, extend the `BaseProvider` class:

```typescript
import { providers } from '@agent-infra/sandbox';

class MyCustomProvider extends providers.BaseProvider {
  async createSandbox(functionId: string, ...kwargs: any[]): Promise<any> {
    // Implementation
  }

  async deleteSandbox(functionId: string, sandboxId: string, ...kwargs: any[]): Promise<any> {
    // Implementation
  }

  async getSandbox(functionId: string, sandboxId: string, ...kwargs: any[]): Promise<any> {
    // Implementation
  }

  async listSandboxes(functionId: string, ...kwargs: any[]): Promise<any> {
    // Implementation
  }
}
```

## API Reference

### BaseProvider (Abstract)

Base class for all cloud provider implementations.

#### Methods

- `createSandbox(functionId: string, ...kwargs: any[]): Promise<any>`
- `deleteSandbox(functionId: string, sandboxId: string, ...kwargs: any[]): Promise<any>`
- `getSandbox(functionId: string, sandboxId: string, ...kwargs: any[]): Promise<any>`
- `listSandboxes(functionId: string, ...kwargs: any[]): Promise<any>`

### VolcengineProvider

Volcengine VEFAAS implementation of the BaseProvider.

#### Constructor Options

- `accessKey` (string): Volcengine access key ID
- `secretKey` (string): Volcengine secret access key
- `region` (string, optional): Volcengine region, defaults to 'cn-beijing'
- `clientSideValidation` (boolean, optional): Enable client-side validation, defaults to true

#### Additional Methods

- `createApplication(name: string, gatewayName: string, ...kwargs: any[]): Promise<string | null>`
- `getApplicationReadiness(id: string, ...kwargs: any[]): Promise<[boolean, string | null]>`
- `getApigDomains(functionId: string): Promise<DomainInfo[]>`
- `setSandboxTimeout(functionId: string, sandboxId: string, timeout: number): Promise<any>`

## Environment Variables

For the Volcengine provider, you can also configure credentials using environment variables:

- `VOLCENGINE_ACCESS_KEY`
- `VOLCENGINE_SECRET_KEY`

## License

Apache License 2.0
