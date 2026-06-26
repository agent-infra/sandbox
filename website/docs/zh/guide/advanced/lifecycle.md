# AIO Hooks

AIO Hooks 可以在容器生命周期的固定阶段执行启动命令，适合安装轻量依赖、准备文件或启动辅助进程。

## 启动顺序

```text
容器启动
  -> RUN_HOOK_INIT
  -> 准备运行用户和工作目录
  -> RUN_HOOK_PRE_SERVICES
  -> 托管服务启动
  -> 就绪检查通过
  -> RUN_HOOK_POST_READY
```

## Hooks

| Hook | 适合用途 |
| --- | --- |
| `RUN_HOOK_INIT` | 最早初始化，适合必须在服务准备前执行的逻辑 |
| `RUN_HOOK_PRE_SERVICES` | 服务启动前安装工具或写入配置 |
| `RUN_HOOK_POST_READY` | 需要 API、浏览器或 code-server 可用后的预热任务 |

## 示例

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 127.0.0.1:8080:8080 \
  -e RUN_HOOK_PRE_SERVICES="python -m pip install requests" \
  ghcr.io/agent-infra/sandbox:latest
```

如果需要较重的定制，建议使用自定义 Docker 镜像，让启动更快且更可复现。

## 运行时 Shutdown Hooks

沙箱运行中也可以通过 API 注册 shutdown hook，用于退出前刷新状态或写入标记文件。运行时 API 当前支持 `shutdown` 事件。

```bash
curl -X POST "http://localhost:8080/v1/sandbox/hooks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "write-shutdown-marker",
    "event": "shutdown",
    "command": "printf stopped > /home/gem/workspace/shutdown.txt",
    "timeout": 10,
    "priority": 100
  }'
```

查看已注册 hook：

```bash
curl "http://localhost:8080/v1/sandbox/hooks?event=shutdown"
```

删除通过 API 注册的 hook：

```bash
curl -X DELETE "http://localhost:8080/v1/sandbox/hooks/write-shutdown-marker"
```

## 建议

- Hook 命令保持幂等。
- 不要把密钥写入 Hook 值或镜像层。
- 大依赖使用自定义镜像预装。
- 挂载项目文件时配合 [工作目录](/zh/guide/advanced/workspace)。
