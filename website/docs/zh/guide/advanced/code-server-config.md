# Code Server 配置

AIO Sandbox 内置 code-server，可以在浏览器中打开沙盒内的 VS Code 环境。

## 访问地址

```text
http://localhost:8080/code-server/
```

编辑器与 Shell、浏览器下载、Jupyter 和文件 API 共享同一套文件系统。

## 环境变量

| 变量 | 默认值 | 用途 |
| --- | --- | --- |
| `CODE_SERVER_PORT` | `8200` | code-server 内部端口 |
| `DISABLE_CODE_SERVER` | `false` | truthy 时关闭 code-server |
| `WORKSPACE` | `/home/gem` | code-server 默认打开的目录 |

## 启动时安装扩展

轻量定制可以使用生命周期 Hook：

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 127.0.0.1:8080:8080 \
  -e RUN_HOOK_PRE_SERVICES="code-server --install-extension ms-python.python" \
  ghcr.io/agent-infra/sandbox:latest
```

如果团队需要稳定可复现环境，建议构建预装扩展的自定义镜像。

## 建议

- 将项目代码挂载到 `WORKSPACE`。
- 编辑器终端里启动的应用，可通过 [预览代理](/zh/guide/advanced/proxy-network) 查看。
- 纯 API 部署可以关闭 code-server 来降低资源占用。

