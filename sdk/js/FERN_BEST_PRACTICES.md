# Fern TypeScript SDK 最佳实践

基于官方文档：
- https://buildwithfern.com/learn/sdks/generators/typescript/custom-code
- https://buildwithfern.com/learn/sdks/generators/typescript/configuration

## ✅ 我们当前的实现（符合最佳实践）

### 1. 使用 .fernignore 保护自定义代码

**官方推荐方式：**
> Simply add your custom files to the SDK repository and list them out in .fernignore.
> Fern won't override any files that you add in .fernignore.

**我们的实现：**
```
# sdk/js/src/.fernignore
providers/
```

✅ **正确** - `providers/` 目录完全受保护

### 2. 自定义代码目录结构

**官方推荐方式：**
- 将自定义代码放在独立目录
- 在 .fernignore 中列出
- 从主 index.ts 导出

**我们的实现：**
```
src/
├── providers/           ← 自定义代码
│   ├── base.ts
│   ├── sign.ts
│   ├── volcengine.ts
│   └── index.ts
├── .fernignore          ← providers/ 被保护
└── index.ts             ← 导出 providers
```

✅ **正确** - 完全符合官方推荐结构

### 3. 导出自定义代码

**我们的实现：**
```typescript
// src/index.ts
export * from "./providers";
```

⚠️ **需要改进** - 这个导出会被 Fern 覆盖

**推荐改进方式：**
有两种选择：

#### 选项 A: 使用 post-generate 脚本（当前方案）
```bash
npm run postgenerate  # 自动恢复导出
```

✅ 简单有效，已实现

#### 选项 B: 扩展生成的客户端（官方推荐）
```typescript
// src/wrapper/Client.ts (添加到 .fernignore)
import { SandboxClient as FernClient } from '../Client';
import { VolcengineProvider } from '../providers';

export class SandboxClient extends FernClient {
    public readonly volcengine: VolcengineProvider;

    constructor(options) {
        super(options);
        // 初始化 volcengine provider
        this.volcengine = new VolcengineProvider(
            options.volcengineAccessKey,
            options.volcengineSecretKey
        );
    }
}

// src/index.ts (手动管理，添加到 .fernignore)
export { SandboxClient } from './wrapper/Client';
export * from './providers';
```

## 🔧 可用的配置选项

### 当前配置
```yaml
config:
  namespaceExport: Sandbox
  treatUnknownAsAny: true
```

### 可以添加的选项

#### 1. outputEsm
```yaml
config:
  outputEsm: true  # 输出 ESM 而不是 CommonJS
```

**用途：**
- 生成现代 ES 模块代码
- 更好的 tree-shaking
- 可选，不影响类型错误

#### 2. extraDependencies
```yaml
config:
  extraDependencies:
    "@volcengine/openapi": "^1.0.0"  # 如果需要
```

**用途：**
- 为自定义代码添加额外依赖
- 自动添加到生成的 package.json
- 目前我们不需要（直接实现 API 调用）

#### 3. bundle
```yaml
config:
  bundle: true
```

**用途：**
- 打包所有依赖
- 生成单文件 SDK
- 可选，不影响类型错误

## 🎯 关键发现：类型错误仍然无法避免

即使按照官方最佳实践：

1. ❌ **HeadersIterator bug** - Fern 生成器问题，无法配置避免
2. ❌ **Buffer/BlobPart 冲突** - TypeScript 严格模式问题，无法配置避免

**结论：** post-generate 脚本仍然是必需的！

## 🚀 推荐的改进方案

### 选项 1: 保持当前方案（简单）

**优点：**
- ✅ 已经工作正常
- ✅ 简单易维护
- ✅ 一个命令修复所有问题

**缺点：**
- ⚠️ 每次生成后需要运行 postgenerate
- ⚠️ index.ts 会被覆盖

**适合：** 当前项目（已实现自动化）

### 选项 2: 扩展客户端（官方推荐）

**结构：**
```
src/
├── wrapper/
│   └── Client.ts      (extends FernClient)
├── providers/
│   └── ...
├── .fernignore
│   wrapper/
│   providers/
│   index.ts           (手动管理)
```

**优点：**
- ✅ 更符合 Fern 官方模式
- ✅ index.ts 不会被覆盖
- ✅ 客户端扩展更优雅

**缺点：**
- ⚠️ 仍然需要 post-generate 修复类型
- ⚠️ 需要重构现有代码

**适合：** 未来重构时考虑

## 📋 可选的配置增强

如果需要添加更多功能：

```yaml
js-sdk:
  generators:
    - name: fernapi/fern-typescript-sdk
      version: 3.28.4
      output:
        location: local-file-system
        path: ../js/src
      config:
        namespaceExport: Sandbox
        treatUnknownAsAny: true
        outputEsm: false           # CommonJS (默认)
        bundle: false              # 不打包 (默认)
        # extraDependencies:       # 如需要额外依赖
        #   "some-package": "^1.0.0"
```

## 🎓 最佳实践总结

1. ✅ 使用 `.fernignore` 保护自定义代码
2. ✅ 将自定义代码放在独立目录 (`providers/`)
3. ✅ 使用 post-generate 脚本自动修复
4. ✅ 文档化工作流程
5. ⚠️ 考虑未来使用客户端扩展模式
6. ✅ 保持配置简单（除非需要特殊功能）

## 结论

我们当前的实现**已经符合 Fern 官方推荐的最佳实践**：

- ✅ .fernignore 保护自定义代码
- ✅ 独立的 providers 目录
- ✅ 自动化修复流程

**类型错误是 Fern 生成器 bug，无法通过配置避免。**
**post-generate 脚本是必需且合理的解决方案。**
