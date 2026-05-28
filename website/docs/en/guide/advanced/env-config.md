# Environment Configuration

AIO Sandbox uses environment variables to configure services at container startup. When values are provided through Docker, Compose, or SDK configuration, pass them as strings.

## Workspace

| Variable | Default | Purpose |
| --- | --- | --- |
| `WORKSPACE` | `/home/gem` | Default working directory for shell, code execution, Jupyter, and code-server |
| `USER` | `gem` | Runtime user inside the container |

## Network And Proxy

| Variable | Default | Purpose |
| --- | --- | --- |
| `PROXY_SERVER` | empty | Upstream HTTP/HTTPS proxy for browser and network traffic |
| `PROXY_EXCLUDE` | empty | Hosts that should bypass the upstream proxy |
| `PROXY_INCLUDE` | empty | Hosts that should use the upstream proxy in allow-list mode |
| `PROXY_MAP` | empty | Static host mapping rules for advanced proxy scenarios |

## Browser

| Variable | Default | Purpose |
| --- | --- | --- |
| `HOMEPAGE` | empty | Page opened when Chromium starts |
| `BROWSER_LANG` | `en-US` | Browser language and `Accept-Language` preference |
| `CHROME_UI_LANG` | empty | Chromium UI language |
| `BROWSER_USER_AGENT` | default Chromium UA | Custom user agent |
| `BROWSER_EXTRA_ARGS` | empty | Additional Chromium launch flags |

## Services

| Variable | Default | Purpose |
| --- | --- | --- |
| `CODE_SERVER_PORT` | `8200` | Internal code-server port |
| `DISABLE_CODE_SERVER` | `false` | Disable code-server when set to a truthy value |
| `DISABLE_JUPYTER` | `false` | Disable JupyterLab when set to a truthy value |
| `SANDBOX_SRV_PORT` | `8080` | Main API service port inside the container |

## Security

| Variable | Default | Purpose |
| --- | --- | --- |
| `JWT_PUBLIC_KEY` | empty | Enables Bearer token verification for API and web routes |
| `AUTH_TOKEN` | empty | Shared token for simple deployments, when supported by the running image |

## Lifecycle Hooks

| Variable | Timing |
| --- | --- |
| `RUN_HOOK_INIT` | Earliest startup hook |
| `RUN_HOOK_PRE_SERVICES` | Before managed services start |
| `RUN_HOOK_POST_READY` | After services are ready |

See [AIO Hooks](/guide/advanced/lifecycle) for examples.

