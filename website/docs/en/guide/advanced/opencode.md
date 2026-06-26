# OpenCode Integration

AIO Sandbox includes the [OpenCode](https://opencode.ai/) CLI. OpenCode is an open-source terminal coding agent, so you can run it directly inside the sandbox or launch it through the built-in terminal page.

## Access

- Browser: open `http://localhost:8080/opencode` to redirect to the built-in terminal and start `opencode`
- Terminal: run `opencode` inside the container

## Environment Variables

You can generate the OpenCode configuration at container startup with environment variables:

| Variable | Default | Description |
| --- | --- | --- |
| `OPENCODE_API_KEY` | Required | Provider API key |
| `OPENCODE_MODEL` | Required | Model ID |
| `OPENCODE_PROVIDER` | `ark` | Provider ID |
| `OPENCODE_BASE_URL` | `https://ark.cn-beijing.volces.com/api/v3` | API endpoint |
| `OPENCODE_PROVIDER_NPM` | Auto-detected | AI SDK npm package for the provider |
| `OPENCODE_JSON` | None | Full OpenCode config JSON; highest priority |

`OPENCODE_PROVIDER_NPM` usually does not need to be set manually. If `OPENCODE_BASE_URL` contains `anthropic`, AIO Sandbox uses `@ai-sdk/anthropic`; otherwise it defaults to `@ai-sdk/openai-compatible`.

## Examples

The default provider is `ark`, so most setups only need an API key and model ID:

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 127.0.0.1:8080:8080 \
  -e OPENCODE_API_KEY="your-api-key" \
  -e OPENCODE_MODEL="your-model-id" \
  ghcr.io/agent-infra/sandbox:latest
```

Anthropic-compatible endpoint:

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 127.0.0.1:8080:8080 \
  -e OPENCODE_PROVIDER="custom-anthropic" \
  -e OPENCODE_BASE_URL="https://example.com/anthropic/v1" \
  -e OPENCODE_API_KEY="your-api-key" \
  -e OPENCODE_MODEL="your-model-id" \
  ghcr.io/agent-infra/sandbox:latest
```

OpenAI-compatible endpoint:

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 127.0.0.1:8080:8080 \
  -e OPENCODE_PROVIDER="openai" \
  -e OPENCODE_BASE_URL="https://api.openai.com/v1" \
  -e OPENCODE_API_KEY="your-api-key" \
  -e OPENCODE_MODEL="your-model-id" \
  ghcr.io/agent-infra/sandbox:latest
```

For full customization, pass an OpenCode config JSON with `OPENCODE_JSON`:

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 127.0.0.1:8080:8080 \
  -e OPENCODE_JSON='{"model":"my-provider/my-model","provider":{"my-provider":{"npm":"@ai-sdk/openai-compatible","options":{"baseURL":"https://example.com/v1","apiKey":"your-api-key"},"models":{"my-model":{}}}}}' \
  ghcr.io/agent-infra/sandbox:latest
```

## Configuration Priority

1. `OPENCODE_JSON`
2. `OPENCODE_API_KEY` + `OPENCODE_MODEL` and other `OPENCODE_*` environment variables
3. A user-managed `~/.config/opencode/config.json`

When `OPENCODE_JSON` or `OPENCODE_API_KEY` + `OPENCODE_MODEL` is set, AIO Sandbox writes `~/.config/opencode/config.json` during container startup. For long-lived custom configuration, either pin the full configuration with `OPENCODE_JSON` or edit the file while not setting `OPENCODE_*` environment variables.

## Related Docs

- [WebTerminal Integration](/guide/advanced/web-terminal)
- [Environment Configuration](/guide/advanced/env-config)
- [Lifecycle Hooks](/guide/advanced/lifecycle)
