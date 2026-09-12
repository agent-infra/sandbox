---
okf_version: "0.2"
type: index
---

# Project Knowledge

This is the **agent-infra/sandbox** monorepo (AIO Sandbox). Important: this
repository does **not** contain the sandbox runtime itself — the runtime ships
as a prebuilt Docker image. This repo owns the SDKs, API contract,
documentation, examples, and the evaluation harness. Start with the
[system overview](architecture/system-overview.md) to understand this split
before anything else.

## Start here

- [System overview](architecture/system-overview.md) — purpose, repo/runtime split, major components
- [Component model](architecture/component-model.md) — SDKs, website, examples, evaluation, CI
- [Runtime and deployment](architecture/runtime-and-deployment.md) — how the sandbox container is configured and delivered

## Core decisions

- [Runtime distribution model](decisions/runtime-distribution-model.md) — the runtime lives in a Docker image built outside this repo
- [SDK generation from OpenAPI](decisions/sdk-generation-from-openapi.md) — Fern codegen; the OpenAPI spec is the single source of truth
- [Cloud provider abstraction](decisions/cloud-provider-abstraction.md) — hand-written provider layer (Volcengine VEFAAS) on top of generated SDKs
- [Image mirroring CI](decisions/image-mirror-cd.md) — GHCR images are mirrored, not built, from the upstream registry

## Constraints

- [API contract and version alignment](constraints/api-contract-and-versions.md) — OpenAPI spec, SDK versions, and image version drift

## Operations

- [Development and verification](runbooks/development-and-verification.md) — how to build, test, and verify changes in this repo
