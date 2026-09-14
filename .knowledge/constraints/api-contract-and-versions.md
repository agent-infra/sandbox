---
type: constraint
---

# API Contract and Version Alignment

## Constraint

The OpenAPI spec, the generated SDKs, the published npm/PyPI packages, the
Docker image tags, and the documentation must stay mutually aligned, but
they move at different cadences and are controlled by different processes.

## Observed state

| Artifact | Version marker | Notes |
|---|---|---|
| OpenAPI spec | `1.9.4` (info.version) | Exported from the FastAPI runtime service |
| Current image in README quick start | `1.11.0` | Spec lags the runtime |
| Python SDK | `0.0.31` (pyproject) | Independent semver track |
| JS SDK | `1.0.17` (package.json) | Independent semver track |
| Evaluation ping expectation | `v1.0.0.143` (dataset) | Hard-coded; stale relative to images |

Additional alignment couplings:

- Python SDK description states ">=1.9.4" runtime requirement — the
  minimum image version the SDK supports.
- Release tags use the image's four-part version (`v1.0.0.1`-style), while
  SDKs use independent semver; the mirror workflow maps between them.
- Documentation quick starts pin concrete image tags (e.g. `1.11.0`) and must
  be updated on each release.

## Why it matters

- New SDK surface cannot be generated until the runtime exports a newer
  spec; conversely, SDKs targeting older image versions will fail on newer
  endpoints only if they call them.
- The evaluation harness's `ping` dataset and `workflow` tasks hard-code
  expected version strings and file paths inside the sandbox (`/tmp/main.py`,
  `/tmp/evaluation.xml` uploaded by the harness) — running evaluations
  against a different image version can break expectations.
- The Go SDK is generated into an external repository
  (`agent-infra/sandbox-sdk-go`), so its version alignment is managed
  entirely outside this repo.

## Handling rules

- Treat `website/docs/public/v1/openapi.json` as the contract of record;
  when regenerating SDKs, note the spec version in the PR.
- Do not bump SDK versions without coordinating with the publish workflow
  (`sdk-publish.yml` owns version-bump commits on `main`).
- Do not edit Fern-generated files directly; regenerate instead.
- When updating README/docs image tags, remember the mirror workflow's
  `v`-stripping convention.

## Related knowledge

- [SDK generation from OpenAPI](../decisions/sdk-generation-from-openapi.md)
- [Runtime distribution model](../decisions/runtime-distribution-model.md)
