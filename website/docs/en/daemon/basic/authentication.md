# Authentication

aiod supports one optional startup key.

When no key is configured, every route is open and aiod is fully exposed. Bind it to `127.0.0.1`, or put a gateway with its own authentication in front.

## Starting with an API key

The flag and the environment variable set the same key:

```bash
aiod start --api-key my-secret-key
# equivalently
AIO_API_KEY=my-secret-key aiod start
```

## Sending the API key

Three equivalent forms:

```bash
curl "$BASE_URL/v1/sandbox" -H "Authorization: Bearer my-secret-key"
curl "$BASE_URL/v1/sandbox" -H "x-api-key: my-secret-key"
curl "$BASE_URL/v1/sandbox?api_key=my-secret-key"
```

| Channel | When to use it | Notes |
| --- | --- | --- |
| `Authorization: Bearer` | The default for an HTTP client | A standard bearer token |
| `x-api-key` | A client that already speaks this header | The prebuilt images' gateway also accepts `X-AIO-API-Key` |
| `?api_key=` | Only where headers are impossible | Deprecated; percent-decoded before the compare |

Every channel is compared in constant time, so neither the key's length nor how far a guess matched shows up in response timing.

A credential in a URL can leak into access logs, browser history, and the `Referer` of a later request.

Use the query form only when a request header is not possible, such as with a browser-native WebSocket or a VNC page:

```text
{ws_base_url}/v1/shell/ws?session_id=SESSION_ID&api_key=my-secret-key
```

A WebSocket is authenticated before the upgrade. Without a valid key, the handshake answers `401` instead of opening and closing.

Except on the public routes below, every request without a valid key answers `401` with the standard envelope:

```json
{
  "success": false,
  "message": "Unauthorized",
  "data": null,
  "hint": null
}
```

## Public routes

These skip the key check:

- `/`
- `/health`
- `/v1/ping`
- `/v1/openapi.json`
- `/v2/openapi.json`
- `/internal/auth`

Public paths match by prefix. For example, `/health` also covers `/health/details`, while `/` covers only itself and cannot exempt the whole API.

Public does not mean that a route has content: the daemon serves nothing at `/`, which is normally where a gateway puts its landing page.

Everything else requires the key when one is set, including `/metrics` — a scrape surface exposes route names and traffic shape, so there is no exemption for ops endpoints.

## Behind a gateway

`/internal/auth` is the subrequest endpoint used by nginx `auth_request`. It reads the original request path from `X-Original-URI` and applies the same key check:

- It answers `204` when the request is authorized, the target is public, or no key is configured.
- It answers `401` otherwise.
- It never returns a body.

One `auth_request` can therefore gate everything the gateway fronts, including the VNC stream that never reaches aiod's middleware. When called directly, with no `X-Original-URI`, it checks the current request's own credentials.

## CORS

CORS is open by design. aiod does not enforce an origin policy; the gateway in front of it does. Never expose the CDP port (default `9222`) outside a trusted network — it has no authentication of its own.

## Identity: execution vs. ownership

`user` on a request means two different things, depending on the API. `AIO_DEFAULT_USER` sets the same default:

> On commands, PTY, and code, `user` decides which account runs the process; on files, it only decides who owns new objects.

On files, the daemon still reads and writes with its own privileges; `user` does not change the execution identity.

This only applies on Linux. Windows answers `400` for an explicit `user`, and `503` when `AIO_DEFAULT_USER` would apply — see [Windows](/daemon/basic/windows).

## Related

- [Error Handling](/daemon/basic/error-handling) — what `401` looks like next to the other statuses
- [Observability](/daemon/basic/observability) — the key is redacted out of the request log
- [File (FS)](/daemon/basic/file#ownership-identity) — ownership identity on the file plane
