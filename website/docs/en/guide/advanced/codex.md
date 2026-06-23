# Codex Integration

AIO Sandbox includes the [OpenAI Codex](https://github.com/openai/codex) CLI. Codex is a terminal-first AI coding agent, so you can run it directly inside the sandbox or launch it through the built-in terminal page.

## Access

- Browser: open `http://localhost:8080/codex` to redirect to the built-in terminal and start `codex`
- Terminal: run `codex` inside the container

## Environment Variables

You can generate the Codex configuration at container startup with environment variables:

| Variable | Default | Description |
| --- | --- | --- |
| `CODEX_API_KEY` | None | General API key, recommended for Responses-compatible gateways |
| `ARK_API_KEY` | None | Compatible with existing Volcengine Ark API key setups |
| `OPENAI_API_KEY` | None | Official OpenAI API key |
| `CODEX_MODEL` | `deepseek-v4-flash-260425` | Model ID written in custom provider mode |
| `CODEX_BASE_URL` | `https://ark.cn-beijing.volces.com/api/v3` | Responses API endpoint written in custom provider mode |
| `CODEX_CONFIG_TOML` | None | Full custom `config.toml` content; highest priority |
| `CODEX_MODEL_CATALOG_JSON` | None | Optional model catalog JSON written to `~/.codex/model-catalog.json` |

For most setups, prefer `CODEX_API_KEY`.

## Examples

Official OpenAI API:

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 8080:8080 \
  -e OPENAI_API_KEY="sk-xxx" \
  ghcr.io/agent-infra/sandbox:latest
```

Other Responses-compatible endpoint:

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 8080:8080 \
  -e CODEX_API_KEY="your-api-key" \
  -e CODEX_MODEL="your-model-id" \
  -e CODEX_BASE_URL="https://example.com/api/v3" \
  ghcr.io/agent-infra/sandbox:latest
```

Fully custom Codex configuration:

Use `CODEX_CONFIG_TOML` when you need to provide any Codex-supported `config.toml` fields. Prefer referencing the API key through `env_key` instead of writing the secret value directly into TOML.

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
  -p 8080:8080 \
  -e CUSTOM_API_KEY="your-api-key" \
  -e CODEX_CONFIG_TOML \
  -e CODEX_MODEL_CATALOG_JSON \
  ghcr.io/agent-infra/sandbox:latest
```

## Configuration Priority

At startup, AIO Sandbox generates `config.toml` in this order:

1. `CODEX_CONFIG_TOML`
2. Auto-generated config from `CODEX_API_KEY` / `ARK_API_KEY` / `OPENAI_API_KEY`
3. No generated config

When auto-generating the config, AIO Sandbox selects the API key in this order:

1. `CODEX_API_KEY`
2. `ARK_API_KEY`
3. `OPENAI_API_KEY`

If no API key is available, AIO Sandbox does not generate or overwrite Codex configuration.

`CODEX_CONFIG_TOML` is validated as TOML, and `CODEX_MODEL_CATALOG_JSON` is validated as JSON. If validation fails, startup exits with an explicit error instead of silently falling back to another configuration.

## User Customization

After startup, you can edit `~/.codex/config.toml` directly. If the container is restarted with `CODEX_CONFIG_TOML` or one of the API key environment variables above, the startup script regenerates the configuration. To keep manual edits, restart without those environment variables.

## Related Docs

- [WebTerminal Integration](/guide/advanced/web-terminal)
- [Environment Configuration](/guide/advanced/env-config)
- [Lifecycle Hooks](/guide/advanced/lifecycle)
