# OpenCode 集成

AIO Sandbox 内置 [OpenCode](https://opencode.ai/) CLI。OpenCode 是面向终端的开源 AI coding agent，可以在沙盒里直接使用，也可以通过内置终端页面打开。

## 访问方式

- 浏览器：访问 `http://localhost:8080/opencode`，会跳转到内置终端并启动 `opencode`
- 终端：在容器内直接运行 `opencode`

## 环境变量

启动容器时可以通过环境变量生成 OpenCode 配置：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `OPENCODE_API_KEY` | 必填 | Provider API key |
| `OPENCODE_MODEL` | 必填 | 模型 ID |
| `OPENCODE_PROVIDER` | `ark` | Provider ID |
| `OPENCODE_BASE_URL` | `https://ark.cn-beijing.volces.com/api/v3` | API endpoint |
| `OPENCODE_PROVIDER_NPM` | 自动推导 | Provider 使用的 AI SDK npm 包 |
| `OPENCODE_JSON` | 无 | 完整 OpenCode 配置 JSON，优先级最高 |

`OPENCODE_PROVIDER_NPM` 通常无需手动设置。当 `OPENCODE_BASE_URL` 包含 `anthropic` 时，会使用 `@ai-sdk/anthropic`；其他情况默认使用 `@ai-sdk/openai-compatible`。

## 配置示例

默认 provider 是 `ark`，通常只需要提供 API key 和模型 ID：

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 127.0.0.1:8080:8080 \
  -e OPENCODE_API_KEY="your-api-key" \
  -e OPENCODE_MODEL="your-model-id" \
  ghcr.io/agent-infra/sandbox:latest
```

Anthropic 兼容端点：

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 127.0.0.1:8080:8080 \
  -e OPENCODE_PROVIDER="custom-anthropic" \
  -e OPENCODE_BASE_URL="https://example.com/anthropic/v1" \
  -e OPENCODE_API_KEY="your-api-key" \
  -e OPENCODE_MODEL="your-model-id" \
  ghcr.io/agent-infra/sandbox:latest
```

OpenAI 兼容端点：

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 127.0.0.1:8080:8080 \
  -e OPENCODE_PROVIDER="openai" \
  -e OPENCODE_BASE_URL="https://api.openai.com/v1" \
  -e OPENCODE_API_KEY="your-api-key" \
  -e OPENCODE_MODEL="your-model-id" \
  ghcr.io/agent-infra/sandbox:latest
```

如果需要完全自定义，可以使用 `OPENCODE_JSON` 传入完整配置：

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 127.0.0.1:8080:8080 \
  -e OPENCODE_JSON='{"model":"my-provider/my-model","provider":{"my-provider":{"npm":"@ai-sdk/openai-compatible","options":{"baseURL":"https://example.com/v1","apiKey":"your-api-key"},"models":{"my-model":{}}}}}' \
  ghcr.io/agent-infra/sandbox:latest
```

## 配置优先级

1. `OPENCODE_JSON`
2. `OPENCODE_API_KEY` + `OPENCODE_MODEL` 以及其他 `OPENCODE_*` 环境变量
3. 用户手动维护的 `~/.config/opencode/config.json`

当设置了 `OPENCODE_JSON` 或 `OPENCODE_API_KEY` + `OPENCODE_MODEL` 时，容器启动时会写入 `~/.config/opencode/config.json`。如果希望长期维护自定义配置，建议使用 `OPENCODE_JSON` 固化完整配置，或在不设置 `OPENCODE_*` 环境变量的情况下手动编辑该文件。

## 相关文档

- [WebTerminal 集成](/zh/guide/advanced/web-terminal)
- [环境变量配置](/zh/guide/advanced/env-config)
- [生命周期 Hook](/zh/guide/advanced/lifecycle)
