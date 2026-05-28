# Browser Configuration

AIO Sandbox runs Chromium inside the container. You can configure language, homepage, user agent, and launch flags through environment variables.

## Common Variables

| Variable | Purpose |
| --- | --- |
| `HOMEPAGE` | Default page opened when the browser starts |
| `BROWSER_LANG` | Browser language and `Accept-Language` |
| `CHROME_UI_LANG` | Chromium UI language |
| `BROWSER_USER_AGENT` | Custom user agent string |
| `BROWSER_EXTRA_ARGS` | Additional Chromium launch arguments |

## Language

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 8080:8080 \
  -e BROWSER_LANG=en-US \
  ghcr.io/agent-infra/sandbox:latest
```

## Homepage

```bash
-e HOMEPAGE=https://example.com
```

## User Agent

```bash
-e BROWSER_USER_AGENT="Mozilla/5.0 ..."
```

## Extra Arguments

Use `BROWSER_EXTRA_ARGS` for advanced Chromium flags:

```bash
-e BROWSER_EXTRA_ARGS="--disable-dev-shm-usage"
```

Be conservative with launch flags. Removing default security or process flags can make automation less stable.

## Runtime Configuration

Some browser settings can also be inspected or changed through API endpoints such as:

- `POST /v1/browser/config`
- `POST /v1/browser/restart`
- `GET /v1/browser/info`

Example:

```bash
curl -X POST http://127.0.0.1:8080/v1/browser/config \
  -H 'Content-Type: application/json' \
  -d '{"resolution":{"width":1280,"height":720}}'
```
