# 工作目录

`WORKSPACE` 控制 AIO Sandbox 各服务使用的默认工作目录。

## 基本用法

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 8080:8080 \
  -e WORKSPACE=/workspace \
  -v "$PWD:/workspace" \
  ghcr.io/agent-infra/sandbox:latest
```

容器启动时会按需创建工作目录，并为运行用户准备权限。

## 各服务行为

| 服务 | 默认目录 | 请求级覆盖 |
| --- | --- | --- |
| Shell | `$WORKSPACE` | `exec_dir` |
| Bash | `$WORKSPACE` | `exec_dir` |
| Jupyter | `$WORKSPACE` | 请求参数 |
| Node.js | `$WORKSPACE` | 请求参数 |
| code-server | `$WORKSPACE` | 打开目录 |

## 建议

- Coding Agent 任务建议把项目代码挂载到工作目录。
- 生成产物建议写入工作目录，方便浏览器、Shell、文件和代码执行 API 共享。
- 除非马上下载，否则不要把长期文件写入临时目录。

