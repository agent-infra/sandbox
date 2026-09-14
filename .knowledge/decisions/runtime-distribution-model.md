---
type: decision
---

# Runtime Distribution Model

## Context

AIO Sandbox is a large runtime (Chrome + code-server + Jupyter + MCP hub +
proxy + auth backend in one container). This repository needs to deliver
SDKs, docs, and examples to users, but the runtime itself is built
elsewhere (internally at ByteDance, on Volcengine infrastructure, per the
upstream registry path and the Volcengine provider integration).

## Current decision

The sandbox runtime is **distributed as a prebuilt multi-arch Docker image**;
its source code is not part of this repository.

- Users consume `ghcr.io/agent-infra/sandbox:<version>` (or the Volcengine
  registry mirror for mainland China).
- The GitHub release workflow mirrors the image from the upstream Volcengine
  registry into GHCR; it never builds from source.
- `docker/` exists in the repo but is an empty placeholder.
- The OpenAPI spec in `website/docs/public/v1/openapi.json` is an export
  from the FastAPI service inside that image — the only artifact in this
  repo that describes the runtime's behavior.

## Evidence

- `README.md` quick start runs the prebuilt image; no Dockerfile for the
  runtime exists anywhere in the repo.
- `.github/workflows/push-to-ghcr.yml` uses
  `docker buildx imagetools create` on the upstream image (mirror, not
  build).
- `docker/` contains only `.gitkeep`.
- Spec `info.title` is "FastAPI" with version "1.9.4", while the current
  README offers image tag `1.11.0` — the spec lags the runtime.

## Consequences

- **Runtime bugs cannot be fixed in this repo.** The evaluation harness's
  `improvement_suggestions.md` documents runtime tool ergonomics issues
  (undo_edit semantics, execute_code return behavior, browser_evaluate
  wrapping) that this repo can only report upstream, not patch.
- **The OpenAPI spec is the only contract lever** this repo controls. New
  SDK surface must start as spec changes (regenerated from the runtime
  service), not as direct edits to generated SDK code.
- Version alignment between spec, SDKs, and image must be managed
  consciously (see [API contract and version alignment](../constraints/api-contract-and-versions.md)).
- Feature development in this repo is limited to: SDK ergonomics and
  providers, documentation, examples, and evaluation coverage.

## Related knowledge

- [System overview](../architecture/system-overview.md)
- [Runtime and deployment](../architecture/runtime-and-deployment.md)
- [SDK generation from OpenAPI](sdk-generation-from-openapi.md)
- [Image mirroring CI](image-mirror-cd.md)
