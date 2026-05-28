# 浏览器下载

Chromium 下载的文件会保存在沙盒文件系统中，因此可以通过 Shell 查看，也可以通过文件 API 下载出来。

## 默认下载目录

Chromium 通常会把文件下载到运行用户的下载目录：

```text
/home/gem/Downloads
```

可以通过文件 API 列出目录：

```bash
curl -X POST "http://localhost:8080/v1/file/list" \
  -H "Content-Type: application/json" \
  -d '{"path": "/home/gem/Downloads"}'
```

## 通过 CDP 配置下载

使用 Playwright 或其他 CDP 客户端时，可以在触发下载前配置下载行为：

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

如果你直接使用 Chrome DevTools Protocol，可以在浏览器级 CDP 连接上调用 `Browser.setDownloadBehavior`：

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

触发下载后，可以监听 `Browser.downloadWillBegin` 与 `Browser.downloadProgress`，或直接通过文件 API 检查下载目录。

## 下载文件到宿主机

```bash
curl -L \
  "http://localhost:8080/v1/file/download?path=/home/gem/Downloads/report.pdf" \
  --output report.pdf
```

如果下载产物仍可能被后台进程写入，可以追加 `change_policy=abort`，让服务端在检测到文件变化时中断本次下载。

## 安全建议

- 将下载文件视为不可信输入。
- 除非用户明确需要，否则文件应保留在沙盒内处理。
- 不要开启过宽的本地文件访问能力，除非任务确实需要。
