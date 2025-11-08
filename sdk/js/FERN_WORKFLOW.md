# Fern SDK Generation Workflow

本文档说明如何使用 Fern 生成 Node.js SDK 并保留自定义的 Volcengine Provider。

## 🔄 完整工作流程

### 1. 生成 SDK

```bash
# 在 sdk/fern 目录下执行
cd sdk/fern
fern generate --group js-sdk --local
```

### 2. 自动修复类型错误并恢复 Providers

```bash
# 在 sdk/js 目录下执行
cd ../js
npm run postgenerate
```

这个脚本会自动：
- ✅ 修复 `Headers.ts` 中的 `HeadersIterator` 类型错误
- ✅ 修复 `FormDataWrapper.ts` 中的 `Buffer/BlobPart` 类型错误
- ✅ 恢复 `index.ts` 中的 providers 导出

### 3. 构建

```bash
npm run build
```

## 📁 受保护的文件

以下文件/目录不会被 Fern 覆盖（通过 `.fernignore`）：

```
providers/
```

## 🛠 手动修复（仅供参考）

如果需要手动修复，以下是需要的更改：

### Headers.ts

```typescript
// 将所有 HeadersIterator 替换为 IterableIterator
*entries(): IterableIterator<[string, string]> { ... }
*keys(): IterableIterator<string> { ... }
*values(): IterableIterator<string> { ... }
[Symbol.iterator](): IterableIterator<[string, string]> { ... }
```

### FormDataWrapper.ts

```typescript
// 添加类型断言
return new Blob([buffer as BlobPart], { type: contentType });
return new Blob([value as BlobPart], { type: contentType });
```

### index.ts

```typescript
// 在文件末尾添加
// Volcengine Provider
export * from "./providers";
```

## 🎯 Volcengine Provider

Provider 位于 `src/providers/` 目录，包含：

- **base.ts** - 抽象基类
- **sign.ts** - Volcengine API 签名
- **volcengine.ts** - 完整的 Provider 实现
  - `createSandbox()` ⭐
  - `deleteSandbox()`
  - `getSandbox()`
  - `listSandboxes()`
  - `createApplication()`
  - `getApplicationReadiness()`
  - `getApigDomains()`
- **index.ts** - 导出
- **README.md** - API 文档

## 📦 使用示例

### 使用 Fern 生成的客户端

```typescript
import { SandboxClient } from '@agent-infra/sandbox';

const client = new SandboxClient({
    baseUrl: 'https://your-sandbox-url',
});

await client.sandbox.create({ ... });
```

### 使用 Volcengine Provider

```typescript
import { VolcengineProvider } from '@agent-infra/sandbox';

const provider = new VolcengineProvider(
    process.env.VOLCENGINE_ACCESS_KEY!,
    process.env.VOLCENGINE_SECRET_KEY!
);

const sandboxId = await provider.createSandbox('function-id', {
    timeout: 30
});
```

## 🔧 故障排除

### 问题：构建失败，提示 HeadersIterator 未定义

**解决方案：** 运行 `npm run postgenerate`

### 问题：构建失败，提示 Buffer/BlobPart 类型不匹配

**解决方案：** 运行 `npm run postgenerate`

### 问题：找不到 VolcengineProvider

**解决方案：**
1. 检查 `src/providers/` 目录是否存在
2. 运行 `npm run postgenerate` 恢复 providers 导出
3. 运行 `npm run build`

## 📝 CI/CD 集成

在 CI/CD 流程中，可以这样配置：

```yaml
# GitHub Actions 示例
- name: Generate Fern SDK
  run: |
    cd sdk/fern
    fern generate --group js-sdk --local

- name: Fix type errors
  run: |
    cd sdk/js
    npm run postgenerate

- name: Build
  run: |
    cd sdk/js
    npm run build
```

## ✅ 验证

运行测试确保一切正常：

```bash
cd sdk/js
npm run build
npx tsx test/providers.test.ts
```

应该看到：

```
✅ All required methods are present and callable
✅ Volcengine Provider API is complete
```
