# Kubernetes

`aiod` is built to run as an ordinary container: one process, one port. It uses the same `/health` / `/v1/capabilities` split any Kubernetes probe expects. Run it as one container in a pod, with liveness on `/health` and readiness on `/v1/capabilities`.

Add the extra security context only when the pod also runs a desktop or a Chromium the daemon controls.

`{base_url}` below is the Service's address from inside the cluster, or the ingress address from outside it.

## Deployment + Service

The manifest below configures aiod to listen on port `8091`.

One Deployment, one Service, both probes wired up:

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

Drop the `AIO_API_KEY` env block, its secret, and the readiness probe's `httpHeaders` to run open. This is only safe when the `Service` is not reachable outside the cluster.

Create the secret, then apply the manifest:

```bash
kubectl create secret generic aiod-key --from-literal=api-key=my-secret-key
kubectl apply -f aiod.yaml
```

## Add computer-use for a desktop

If the pod exposes a desktop, run `computer-use` as a second container in the same pod. `aiod` reaches it over `AIO_COMPUTER_USE_URL` (default `http://127.0.0.1:18100`) and proxies `/v2/computer/*` to it.

This default already works between two containers sharing a pod's network namespace. When the worker is missing or not running, those routes answer `503`.

## Chromium seccomp and `/dev/shm`

aiod is a CDP client, not a browser. It connects to a Chromium already reachable at `BROWSER_REMOTE_DEBUGGING_HOST:PORT` (default `127.0.0.1:9222`) and does not start Chromium itself. The Chromium container in this pod needs:

- A seccomp allowance on the Chromium container via `securityContext.seccompProfile`: a `Localhost` profile installed on the node, or `Unconfined`.
- A sized `/dev/shm`, around 4 GiB: for example, an `emptyDir` volume with `medium: Memory` and `sizeLimit: 4Gi` mounted at `/dev/shm`.

## Probes

| Probe | Path | Semantics |
| --- | --- | --- |
| Liveness | `GET /health` | The process is up (public, no key) |
| Readiness | `GET /v1/capabilities` | The domains the deployment needs report ready; needs the key when one is set |

`/v1/capabilities` is cached for 5 seconds. That is fine for a periodic kubelet probe. Add `?refresh=true` only when checking by hand.

## State after restarts

Sessions, retained command output, file watchers, and editor undo history live in the daemon's memory. A pod restart clears them, and reconnecting clients start fresh. Files already on disk in the container are unaffected.

## Verify

From inside the cluster, against the Service address:

```bash
BASE_URL=http://<service-host>
curl -fsS "$BASE_URL/health"
curl -fsS "$BASE_URL/v1/capabilities" -H "Authorization: Bearer my-secret-key"
```

Full run modes, environment variables, and troubleshooting are in the [Deployment guide](/daemon/ops/deployment).
