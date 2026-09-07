---
type: decision
---

# Cloud Provider Abstraction

## Context

The sandbox can run locally (plain `docker run`) or as managed instances on
a cloud platform. SDK consumers need a uniform way to create, inspect, and
destroy sandbox instances without binding SDKs to one vendor.

## Current decision

Each SDK ships a **hand-written provider layer** above the Fern-generated
API clients. The abstraction is an abstract class with four lifecycle
operations:

- `createSandbox(functionId, ...)`
- `deleteSandbox(functionId, sandboxId, ...)`
- `getSandbox(functionId, sandboxId, ...)` (optionally enriching
  provider-specific domain data)
- `listSandboxes(functionId, ...)`

The only implementation is `VolcengineProvider`, targeting Volcengine
VEFAAS (Function-as-a-Service):

- Auth via Volcengine access key / secret key; region defaults to
  `cn-beijing`.
- Request signing implemented in `sdk/js/src/providers/sign.ts` (JS) — the
  most delicate hand-written code, covered by unit tests and an e2e test
  (`volcengine.e2e.test.ts`).
- Python achieves the same via the `volcengine-python-sdk` dependency.
- `functionId` is the unit of sandbox grouping on the cloud side.

## Evidence

- `sdk/js/src/providers/base.ts` (BaseProvider contract), `volcengine.ts`,
  `sign.ts`; mirrored under `sdk/python/agent_sandbox/providers/`.
- `sdk/python/pyproject.toml` depends on `volcengine-python-sdk>=4.0.17`.
- `examples/volcengine-provider/` demonstrates usage.
- Cloud deployment docs: `website/docs/en/guide/start/cloud-deployment.mdx`.

## Consequences

- Adding a second cloud (AWS, GCP, …) means implementing `BaseProvider` per
  SDK; the interface is intentionally minimal and vendor-shaped
  (`functionId` is a VEFAAS concept), so a multi-cloud generalization would
  require revisiting the contract.
- The provider layer lives **inside** each SDK rather than in a shared
  package — the Python and JS implementations are parallel and must be kept
  in sync manually.
- Generated code never imports the provider layer; providers extend the SDK,
  not the reverse.

## Related knowledge

- [SDK generation from OpenAPI](sdk-generation-from-openapi.md)
- [Runtime and deployment](../architecture/runtime-and-deployment.md)
