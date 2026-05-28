# Browser Downloads

Files downloaded by Chromium are stored inside the sandbox filesystem, so they can be inspected with shell commands or retrieved with the file API.

## Default Download Location

Chromium normally downloads files to the runtime user's downloads directory:

```text
/home/gem/Downloads
```

You can list it with the file API:

```bash
curl -X POST "http://localhost:8080/v1/file/list" \
  -H "Content-Type: application/json" \
  -d '{"path": "/home/gem/Downloads"}'
```

## Configure Downloads With CDP

When using Playwright or another CDP client, set the download behavior before triggering downloads:

```python
from agent_sandbox import Sandbox
from playwright.sync_api import sync_playwright

client = Sandbox(base_url="http://localhost:8080")
cdp_url = client.browser.get_info().cdp_url

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(cdp_url)
    page = browser.new_page()
    page.context.set_default_timeout(30_000)
```

If you use Chrome DevTools Protocol directly, call `Browser.setDownloadBehavior` on the browser-level CDP connection:

```json
{
  "method": "Browser.setDownloadBehavior",
  "params": {
    "behavior": "allow",
    "downloadPath": "/home/gem/Downloads",
    "eventsEnabled": true
  }
}
```

After triggering the download, either listen for `Browser.downloadWillBegin` and `Browser.downloadProgress`, or inspect the download directory with the file API.

## Retrieve A Downloaded File

```bash
curl -L \
  "http://localhost:8080/v1/file/download?path=/home/gem/Downloads/report.pdf" \
  --output report.pdf
```

If the downloaded artifact may still be changing, append `change_policy=abort` so the server aborts when it detects source-file changes.

## Security Notes

- Treat downloaded files as untrusted input.
- Keep downloads in the sandbox unless the user explicitly needs them.
- Avoid enabling broad local file access unless a task requires it.
