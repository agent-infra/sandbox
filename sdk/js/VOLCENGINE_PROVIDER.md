# Volcengine Provider - Node.js SDK

## 快速开始

### 安装

```bash
npm install @agent-infra/sandbox
```

### 基本使用

```typescript
import { VolcengineProvider } from '@agent-infra/sandbox';

// 初始化 provider
const provider = new VolcengineProvider(
    process.env.VOLCENGINE_ACCESS_KEY!,
    process.env.VOLCENGINE_SECRET_KEY!,
    'cn-beijing'  // 可选，默认为 cn-beijing
);

// 创建沙箱
const sandboxId = await provider.createSandbox('your-function-id', {
    timeout: 30  // 超时时间（分钟）
});

console.log('Created sandbox:', sandboxId);
```

## API 参考

### createSandbox

创建新的沙箱实例。

```typescript
async createSandbox(
    functionId: string,
    kwargs?: {
        timeout?: number;  // 默认 30 分钟
        [key: string]: any;
    }
): Promise<string | Error>
```

**示例：**

```typescript
// 基本用法
const sandboxId = await provider.createSandbox('func-123');

// 自定义超时
const sandboxId = await provider.createSandbox('func-123', {
    timeout: 60
});

// 带额外参数
const sandboxId = await provider.createSandbox('func-123', {
    timeout: 30,
    customParam: 'value'
});
```

### deleteSandbox

删除现有沙箱实例。

```typescript
async deleteSandbox(
    functionId: string,
    sandboxId: string,
    kwargs?: Record<string, any>
): Promise<SandboxResponse>
```

**示例：**

```typescript
await provider.deleteSandbox('func-123', 'sandbox-456');
```

### getSandbox

获取沙箱详细信息，包括域名。

```typescript
async getSandbox(
    functionId: string,
    sandboxId: string,
    kwargs?: Record<string, any>
): Promise<SandboxResponse>
```

**示例：**

```typescript
const sandbox = await provider.getSandbox('func-123', 'sandbox-456');
console.log('Sandbox domains:', sandbox.domains);
```

### listSandboxes

列出函数的所有沙箱实例。

```typescript
async listSandboxes(
    functionId: string,
    kwargs?: Record<string, any>
): Promise<SandboxResponse>
```

**示例：**

```typescript
const sandboxes = await provider.listSandboxes('func-123');
sandboxes.forEach(sb => {
    console.log(`Sandbox ${sb.id}:`, sb.domains);
});
```

### createApplication

创建 VEFAAS 应用。

```typescript
async createApplication(
    name: string,
    gatewayName: string,
    kwargs?: Record<string, any>
): Promise<string | null>
```

**示例：**

```typescript
const appId = await provider.createApplication(
    'my-app',
    'my-gateway'
);
```

### getApplicationReadiness

检查应用部署状态。

```typescript
async getApplicationReadiness(
    id: string,
    kwargs?: Record<string, any>
): Promise<[boolean, string | null]>
```

**返回：** `[isReady, functionId]`

**示例：**

```typescript
const [isReady, functionId] = await provider.getApplicationReadiness('app-123');
if (isReady) {
    console.log('Application is ready, function ID:', functionId);
}
```

### getApigDomains

获取函数的 APIG 域名。

```typescript
async getApigDomains(
    functionId: string
): Promise<Array<{ domain: string; type?: string }>>
```

**示例：**

```typescript
const domains = await provider.getApigDomains('func-123');
domains.forEach(d => {
    console.log(`${d.type}: ${d.domain}`);
});
```

## 环境变量

支持以下环境变量配置：

```bash
# 方式 1
export VOLCENGINE_ACCESS_KEY=your-access-key
export VOLCENGINE_SECRET_KEY=your-secret-key

# 方式 2（备用）
export VOLC_ACCESSKEY=your-access-key
export VOLC_SECRETKEY=your-secret-key
```

## 完整示例

查看完整示例代码：
- [examples/volcengine-provider.ts](./examples/volcengine-provider.ts)

## 与 Python SDK 对比

| 功能 | Python SDK | Node.js SDK | 状态 |
|------|-----------|-------------|------|
| createSandbox | ✅ | ✅ | ✅ 完全一致 |
| deleteSandbox | ✅ | ✅ | ✅ 完全一致 |
| getSandbox | ✅ | ✅ | ✅ 完全一致 |
| listSandboxes | ✅ | ✅ | ✅ 完全一致 |
| createApplication | ✅ | ✅ | ✅ 完全一致 |
| getApplicationReadiness | ✅ | ✅ | ✅ 完全一致 |
| getApigDomains | ✅ | ✅ | ✅ 完全一致 |

## 实现说明

- **Python SDK**: 使用官方 `volcenginesdkvefaas` SDK
- **Node.js SDK**: 直接实现 API 调用（因 Volcengine Node.js SDK 暂无 VEFAAS 客户端）
- 两者提供相同的功能接口和行为

## License

Apache-2.0
