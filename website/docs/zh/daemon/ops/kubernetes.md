# Kubernetes

`aiod` 按普通容器设计：一个进程、一个端口。

Kubernetes 使用两个探针：liveness 检查进程是否存活，readiness 检查能力是否就绪。将 aiod 作为 pod 中的一个容器运行即可。

只有当 Pod 中还运行桌面或供 daemon 控制的 Chromium 时，才需要额外的安全上下文。

下面的 `{base_url}` 表示集群内部的 Service 地址，或集群外部的 ingress 地址。

## Deployment + Service

下面的清单将 aiod 配置为监听 `8091` 端口。

下面的清单包含一个 Deployment 和一个 Service，并配置了两个探针：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aiod
spec:
  replicas: 1
  selector:
    matchLabels: { app: aiod }
  template:
    metadata:
      labels: { app: aiod }
    spec:
      containers:
        - name: aiod
          image: your-registry/your-image:tag   # your image with the aiod binary copied in
          command: ["aiod", "start"]
          ports:
            - containerPort: 8091
          env:
            - name: AIO_PORT
              value: "8091"
            - name: AIO_API_KEY
              valueFrom:
                secretKeyRef: { name: aiod-key, key: api-key }
          livenessProbe:
            httpGet: { path: /health, port: 8091 }
            initialDelaySeconds: 5
          readinessProbe:
            httpGet:
              path: /v1/capabilities
              port: 8091
              httpHeaders:
                - { name: Authorization, value: "Bearer my-secret-key" }
            periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: aiod
spec:
  selector: { app: aiod }
  ports:
    - port: 80
      targetPort: 8091
```

如果要开放访问，删除 `AIO_API_KEY` 的 env 块、对应的 secret，以及 readiness 探针中的 `httpHeaders`。

仅当 `Service` 无法从集群外访问时，这样配置才安全。

先创建 secret，再应用清单：

```bash
kubectl create secret generic aiod-key --from-literal=api-key=my-secret-key
kubectl apply -f aiod.yaml
```

## 为桌面场景添加 computer-use

如果 pod 要暴露桌面，请在同一个 pod 中再运行一个 `computer-use` 容器。

`aiod` 通过 `AIO_COMPUTER_USE_URL`（默认 `http://127.0.0.1:18100`）连接该容器，并将 `/v2/computer/*` 转发给它。

同一个 pod 中的容器共享网络命名空间，因此默认地址可以直接访问。
worker 不存在或未运行时，这些路由返回 `503`。

## Chromium 的 seccomp 与 `/dev/shm`

aiod 是 CDP 客户端，不是浏览器。它连接已经在 `BROWSER_REMOTE_DEBUGGING_HOST:PORT`（默认 `127.0.0.1:9222`）上监听的 Chromium，不会自行启动 Chromium。

运行 Chromium 的容器需要以下配置：

- 通过 `securityContext.seccompProfile` 配置 seccomp：使用节点上安装的 `Localhost` profile，或使用 `Unconfined`。
- 为 `/dev/shm` 分配约 4 GiB。可以将 `medium: Memory`、`sizeLimit: 4Gi` 的 `emptyDir` 卷挂载到 `/dev/shm`。

## 探针

| 探针 | 路径 | 语义 |
| --- | --- | --- |
| Liveness | `GET /health` | 进程是否在运行（公开，无需 key） |
| Readiness | `GET /v1/capabilities` | 部署所需的能力是否就绪；设置 key 时需要带上 key |

`/v1/capabilities` 缓存 5 秒，这对 kubelet 的定期探测已经足够。
只有手动检查时才需要加 `?refresh=true`。

## 重启后的状态

会话、保留的命令输出、文件 watcher 和编辑器撤销历史都保存在 daemon 内存中。

pod 重启会清空这些状态，客户端重连后需要重新开始。
已经写入容器磁盘的文件不受影响。

## 验证

在集群内通过 Service 地址访问：

```bash
BASE_URL=http://<service-host>
curl -fsS "$BASE_URL/health"
curl -fsS "$BASE_URL/v1/capabilities" -H "Authorization: Bearer my-secret-key"
```

完整的运行模式、环境变量与排障见 [部署指南](/zh/daemon/ops/deployment)。
