# Browser Cookies And State

Browser state is often the most important part of browser automation. AIO Sandbox provides APIs for cookie management and full browser state save/load.

## Set Cookies

```bash
curl -X POST "http://localhost:8080/v1/browser/cookies" \
  -H "Content-Type: application/json" \
  -d '{
    "cookies": [
      {
        "name": "session",
        "value": "example",
        "domain": ".example.com",
        "path": "/",
        "secure": true,
        "httpOnly": true
      }
    ]
  }'
```

## Read Or Clear Cookies

Use the browser cookies API to inspect or clear cookies for automation setup and cleanup. Prefer API calls over direct access to browser profile files.

## Save Browser State

```bash
curl -X POST "http://localhost:8080/v1/browser/state/save" \
  -H "Content-Type: application/json" \
  -d '{"path": "/home/gem/browser-state.json"}'
```

## Load Browser State

```bash
curl -X POST "http://localhost:8080/v1/browser/state/load" \
  -H "Content-Type: application/json" \
  -d '{"path": "/home/gem/browser-state.json"}'
```

## Best Practices

- Navigate to the target domain before validating cookie behavior.
- Prefer state save/load when you need more than cookies.
- Avoid storing real credentials in committed files.
- Keep state files inside the workspace when they need to be shared with file APIs.

