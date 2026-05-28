# AIO CLI

`aio` 命令行工具封装了常用 AIO Sandbox API，适合终端和 Agent 工作流使用。它在沙盒容器内可直接使用。

## 常用命令

```bash
# 浏览器导航
aio browser navigate https://example.com

# 截取页面截图
aio browser screenshot -o /home/gem/page.png

# 截取桌面截图（GUI 层）
aio gui screenshot -o /home/gem/desktop.png

# 查看 MCP server
aio mcp list

# 查看已注册 Skills
aio skills list

# 查看沙盒上下文
aio sandbox info
```

## 命令组

| 命令组 | 用途 |
| --- | --- |
| `browser` | 浏览器导航和页面自动化 |
| `gui` | 桌面级截图和交互 |
| `sandbox` | 环境信息 |
| `skills` | Skill 注册和查询 |
| `mcp` | MCP server 和工具调用 |

## 输出

CLI 同时面向人和 Agent：

- 在终端中输出便于阅读的文本。
- 在脚本或管道中输出结构化 JSON。
- 通过明确退出码表示失败。

## 配置

在容器内使用时，CLI 会自动指向本地沙盒服务。调用远端沙盒时，可通过 `--api-url` 传入 API URL。

## 相关内容

- [浏览器自动化](/zh/guide/basic/browser)
- [Skills](/zh/guide/basic/skills)
- [MCP](/zh/guide/basic/mcp)
