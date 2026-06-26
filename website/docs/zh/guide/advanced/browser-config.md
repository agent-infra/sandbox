# 浏览器配置

AIO Sandbox 在容器内运行 Chromium。可以通过环境变量配置语言、首页、User-Agent 和启动参数。

## 常用变量

| 变量 | 用途 |
| --- | --- |
| `HOMEPAGE` | 浏览器启动时打开的默认页面 |
| `BROWSER_LANG` | 浏览器语言和 `Accept-Language` |
| `CHROME_UI_LANG` | Chromium UI 语言 |
| `BROWSER_USER_AGENT` | 自定义 User-Agent |
| `BROWSER_EXTRA_ARGS` | 追加 Chromium 启动参数 |
| `BROWSER_ALLOW_FILE_SELECTION_DIALOGS` | 控制网页是否可以打开文件选择弹窗 |

## 语言

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 127.0.0.1:8080:8080 \
  -e BROWSER_LANG=en-US \
  ghcr.io/agent-infra/sandbox:latest
```

## 首页

```bash
-e HOMEPAGE=https://example.com
```

## User-Agent

```bash
-e BROWSER_USER_AGENT="Mozilla/5.0 ..."
```

## 额外启动参数

高级 Chromium flag 可以通过 `BROWSER_EXTRA_ARGS` 传入：

```bash
-e BROWSER_EXTRA_ARGS="--disable-dev-shm-usage"
```

建议谨慎修改启动参数。删除默认安全或进程相关参数可能影响自动化稳定性。

## 文件选择弹窗策略

AIO Sandbox 支持通过 `BROWSER_ALLOW_FILE_SELECTION_DIALOGS` 控制网页是否可以打开文件选择弹窗。设为 `false` 后，网页中的文件上传入口无法唤起系统文件选择器：

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 127.0.0.1:8080:8080 \
  -e BROWSER_ALLOW_FILE_SELECTION_DIALOGS=false \
  ghcr.io/agent-infra/sandbox:latest
```

未设置或留空时，浏览器沿用默认行为。


## 运行时配置

部分浏览器设置也可以通过以下 API 查看或更新：

- `POST /v1/browser/config`
- `POST /v1/browser/restart`
- `GET /v1/browser/info`

示例：

```bash
curl -X POST http://127.0.0.1:8080/v1/browser/config \
  -H 'Content-Type: application/json' \
  -d '{"resolution":{"width":1280,"height":720}}'
```
