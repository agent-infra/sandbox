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

## 2026-01 (Node toolchain upgrade to 24)

- Upgraded the JS toolchain from Node 20 to supporting the last three LTS
  lines (20, 22, 24):
  - `sdk-ci.yml` now runs the JS SDK build/tests on a Node `[20, 24]`
    matrix with `fail-fast: false` (backward-compat checks per maintainer
    decision).
  - `sdk-publish.yml` builds/publishes on Node 24.
  - `engines.node` raised from `>=18.0.0` to `>=20.0.0` in the JS SDK —
    a semver-major narrowing of the published package's supported range,
    coordinated with the LTS support window.
  - `@types/node` bumped to `^24` in root/website/sdk-js/examples
    manifests (dev-only).
- Upgraded Vitest 1 → 3 (`^3.2.4`, resolves to 3.2.7) in `sdk/js` because
  Vitest 1.x does not support Node 24. Verified: 66 tests pass, 16 skipped,
  on both Node 20 (vitest 1.6.1 baseline) and Node 24 (vitest 3.2.7);
  d.ts output diff vs. baseline is empty.
- Updated the development runbook with the Node toolchain policy and a
  workspace line-ending gotcha (CRLF working copies vs LF in HEAD) that
  makes the whole tree appear modified; real diffs must be checked with
  `--ignore-cr-at-eol`.
- Rationale recorded: adopting the Eve Framework's minimal Node 24
  requirement while keeping Node 20/22 consumers working.
