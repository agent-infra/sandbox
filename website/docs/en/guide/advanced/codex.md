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

## Configuration Priority

At startup, AIO Sandbox selects the API key in this order:

1. `CODEX_API_KEY`
2. `ARK_API_KEY`
3. `OPENAI_API_KEY`

If no API key is available, AIO Sandbox does not generate or overwrite Codex configuration.

## User Customization

After startup, you can edit `~/.codex/config.toml` directly. If the container is restarted with one of the API key environment variables above, the startup script regenerates the configuration. To keep manual edits, restart without those API key environment variables.

## Related Docs

- [WebTerminal Integration](/guide/advanced/web-terminal)
- [Environment Configuration](/guide/advanced/env-config)
- [Lifecycle Hooks](/guide/advanced/lifecycle)
