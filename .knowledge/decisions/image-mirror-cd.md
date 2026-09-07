---
type: decision
---

# Image Mirroring CI (GHCR distribution)

## Context

The runtime image is built upstream on Volcengine infrastructure, but the
project's public distribution channel is GHCR under the `agent-infra` org.
Users in mainland China need a registry reachable without GHCR.

## Current decision

`.github/workflows/push-to-ghcr.yml` **mirrors** the upstream multi-arch
image rather than rebuilding it:

- Trigger: GitHub release published (or manual `workflow_dispatch`).
- On release, the tag is derived by stripping the leading `v` from the
  release tag (e.g. `v1.0.0.1` → `1.0.0.1`) and that version is pulled from
  the upstream Volcengine registry; manual runs use `latest`.
- `docker buildx imagetools create` copies the **existing multi-arch
  manifest** from the source image directly to
  `ghcr.io/<repo>:<version>` and `ghcr.io/<repo>:latest`. No build, no
  Dockerfile, no rebuild-from-source path exists.
- Permissions include `attestations: write` and `id-token: write` (image
  attestations are enabled on the mirror).
- The workflow also does a plain `docker pull` first — effectively a
  pre-flight existence/availability check that also pins the tag logic in
  one place.

## Consequences

- GHCR availability is strictly downstream of upstream registry
  availability; a missing upstream tag breaks the release pipeline with no
  local fallback.
- Image content is never reproducible from this repo — supply-chain trust
  flows from Volcengine's registry; only the *manifest copy* is attested.
- Anyone changing release tag conventions must keep the `v`-stripping logic
  in this workflow in sync (it appears in both the pull and mirror steps).

## Related knowledge

- [Runtime distribution model](runtime-distribution-model.md)
- [Runtime and deployment](../architecture/runtime-and-deployment.md)
