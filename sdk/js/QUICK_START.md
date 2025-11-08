# Quick Start Guide

## 🚀 快速开始（3 步）

### 重新生成 SDK 时

```bash
# 步骤 1: 生成
cd sdk/fern && fern generate --group js-sdk --local

# 步骤 2: 修复
cd ../js && npm run postgenerate

# 步骤 3: 构建
npm run build
```

就这么简单！✨

## 📝 重要提示

- ✅ `providers/` 目录受保护，不会被覆盖
- ✅ `createSandbox` 等方法始终保留
- ✅ 每次生成后运行 `npm run postgenerate` 即可

## 🎯 验证一切正常

```bash
npm run build && npx tsx test/providers.test.ts
```

## 📖 需要更多帮助？

查看 [FERN_WORKFLOW.md](./FERN_WORKFLOW.md) 获取完整文档。

## 💡 使用示例

```typescript
// 使用 Volcengine Provider
import { VolcengineProvider } from '@agent-infra/sandbox';

const provider = new VolcengineProvider(
    process.env.VOLCENGINE_ACCESS_KEY!,
    process.env.VOLCENGINE_SECRET_KEY!
);

// createSandbox 始终可用
const sandboxId = await provider.createSandbox('function-id', {
    timeout: 30
});
```
