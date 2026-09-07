# Knowledge Maintenance Log

## 2025-09 (initialization)

- Initialized project knowledge from a brownfield repository review.
- Established the central finding: this repo is the SDK/docs/examples/evaluation
  monorepo for AIO Sandbox; the sandbox runtime is distributed as a prebuilt
  Docker image and its source is not in this repository.
- Added architecture overview, component model, and runtime/deployment concepts.
- Recorded core decisions: runtime distribution model, SDK generation via Fern
  from the OpenAPI spec, hand-written cloud provider layer, GHCR image
  mirroring via CI.
- Recorded the API-contract/version-alignment constraint (spec version 1.9.4
  vs. current image 1.11.0, Go SDK output pointing to a separate repo,
  `cli/` and `docker/` being empty placeholders).
- Added the development-and-verification runbook.
