# 环境变量配置

AIO Sandbox 通过环境变量在容器启动时配置各项服务。通过 Docker、Compose 或 SDK 配置传入时，建议把值都作为字符串处理。

## 工作目录

| 变量 | 默认值 | 用途 |
| --- | --- | --- |
| `WORKSPACE` | `/home/gem` | Shell、代码执行、Jupyter 和 code-server 的默认工作目录 |
| `USER` | `gem` | 容器内运行用户 |

## 网络与代理

| 变量 | 默认值 | 用途 |
| --- | --- | --- |
| `PROXY_SERVER` | 空 | 浏览器和网络流量使用的上游 HTTP/HTTPS 代理 |
| `PROXY_EXCLUDE` | 空 | 不经过上游代理的主机列表 |
| `PROXY_INCLUDE` | 空 | 白名单模式下需要经过上游代理的主机列表 |
| `PROXY_MAP` | 空 | 高级代理场景的静态主机映射规则 |

## 浏览器

| 变量 | 默认值 | 用途 |
| --- | --- | --- |
| `HOMEPAGE` | 空 | Chromium 启动时打开的页面 |
| `BROWSER_LANG` | `en-US` | 浏览器语言和 `Accept-Language` 偏好 |
| `CHROME_UI_LANG` | 空 | Chromium UI 语言 |
| `BROWSER_USER_AGENT` | 默认 Chromium UA | 自定义 User-Agent |
| `BROWSER_EXTRA_ARGS` | 空 | 追加 Chromium 启动参数 |

## 服务

| 变量 | 默认值 | 用途 |
| --- | --- | --- |
| `CODE_SERVER_PORT` | `8200` | code-server 内部端口 |
| `DISABLE_CODE_SERVER` | `false` | truthy 时关闭 code-server |
| `DISABLE_JUPYTER` | `false` | truthy 时关闭 JupyterLab |
| `SANDBOX_SRV_PORT` | `8080` | 容器内主 API 服务端口 |

## 安全

| 变量 | 默认值 | 用途 |
| --- | --- | --- |
| `JWT_PUBLIC_KEY` | 空 | 启用 API 和 Web 路由的 Bearer token 校验 |
| `AUTH_TOKEN` | 空 | 简单部署场景的共享 token，取决于运行镜像是否支持 |

## 生命周期 Hooks

| 变量 | 执行时机 |
| --- | --- |
| `RUN_HOOK_INIT` | 最早启动阶段 |
| `RUN_HOOK_PRE_SERVICES` | 托管服务启动前 |
| `RUN_HOOK_POST_READY` | 服务就绪后 |

示例见 [AIO Hooks](/zh/guide/advanced/lifecycle)。

