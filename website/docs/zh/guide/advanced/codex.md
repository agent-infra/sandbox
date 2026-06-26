# Codex 集成

AIO Sandbox 内置 [OpenAI Codex](https://github.com/openai/codex) CLI。Codex 是面向终端的 AI coding agent，可以在沙盒里直接使用，也可以通过内置终端页面打开。

## 访问方式

- 浏览器：访问 `http://localhost:8080/codex`，会跳转到内置终端并启动 `codex`
- 终端：在容器内直接运行 `codex`

## 环境变量

启动容器时可以通过环境变量生成 Codex 配置：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `CODEX_API_KEY` | 无 | 通用 API key，推荐用于 Responses 兼容网关 |
| `ARK_API_KEY` | 无 | 兼容已有的方舟 API key 配置 |
| `OPENAI_API_KEY` | 无 | 官方 OpenAI API key |
| `CODEX_MODEL` | `deepseek-v4-flash-260425` | 自定义 provider 模式下写入的模型 ID |
| `CODEX_BASE_URL` | `https://ark.cn-beijing.volces.com/api/v3` | 自定义 provider 模式下的 Responses API endpoint |
| `CODEX_CONFIG_TOML` | 无 | 完整自定义 `config.toml` 内容，优先级最高 |
| `CODEX_MODEL_CATALOG_JSON` | 无 | 可选模型目录 JSON 内容，写入 `~/.codex/model-catalog.json` |

常规场景优先使用 `CODEX_API_KEY`。

## 配置示例

官方 OpenAI API：

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 127.0.0.1:8080:8080 \
  -e OPENAI_API_KEY="sk-xxx" \
  ghcr.io/agent-infra/sandbox:latest
```

其他 Responses 兼容 endpoint：

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 127.0.0.1:8080:8080 \
  -e CODEX_API_KEY="your-api-key" \
  -e CODEX_MODEL="your-model-id" \
  -e CODEX_BASE_URL="https://example.com/api/v3" \
  ghcr.io/agent-infra/sandbox:latest
```

完全自定义 Codex 配置：

如果需要配置 Codex 支持的任意 `config.toml` 字段，可以使用 `CODEX_CONFIG_TOML` 传入完整 TOML。建议在配置中使用 `env_key` 引用 API key 环境变量，不要把密钥值直接写入 TOML。

```bash
export CODEX_CONFIG_TOML='model = "custom-model"
model_provider = "custom"
model_catalog_json = "model-catalog.json"
approval_policy = "never"
sandbox_mode = "danger-full-access"

[model_providers.custom]
name = "custom"
base_url = "https://example.com/api/v3"
wire_api = "responses"
env_key = "CUSTOM_API_KEY"
'

export CODEX_MODEL_CATALOG_JSON='{"models":[{"id":"custom-model","name":"Custom Model"}]}'

docker run --security-opt seccomp=unconfined --rm -it \
  -p 127.0.0.1:8080:8080 \
  -e CUSTOM_API_KEY="your-api-key" \
  -e CODEX_CONFIG_TOML \
  -e CODEX_MODEL_CATALOG_JSON \
  ghcr.io/agent-infra/sandbox:latest
```

## 配置优先级

启动时按以下顺序生成 `config.toml`：

1. `CODEX_CONFIG_TOML`
2. `CODEX_API_KEY` / `ARK_API_KEY` / `OPENAI_API_KEY` 自动生成配置
3. 不生成配置

使用自动生成配置时，按以下顺序选择 API key：

1. `CODEX_API_KEY`
2. `ARK_API_KEY`
3. `OPENAI_API_KEY`

如果没有可用的 API key，容器启动时不会生成或覆盖 Codex 配置。

`CODEX_CONFIG_TOML` 会做 TOML 语法校验，`CODEX_MODEL_CATALOG_JSON` 会做 JSON 语法校验；校验失败时启动脚本会报错退出，不会静默 fallback 到其他配置。

## 用户自定义

启动后可以直接编辑 `~/.codex/config.toml`。如果容器重启时仍然传入了 `CODEX_CONFIG_TOML` 或上述 API key 环境变量，启动脚本会重新生成配置；如果希望保留手工修改，重启时不要传入这些环境变量。

## 相关文档

- [WebTerminal 集成](/zh/guide/advanced/web-terminal)
- [环境变量配置](/zh/guide/advanced/env-config)
- [生命周期 Hook](/zh/guide/advanced/lifecycle)
