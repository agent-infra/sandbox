---
type: architecture
---

# System Overview

## Purpose

AIO Sandbox is an all-in-one agent sandbox environment combining Browser
(headless + VNC-viewable Chrome), Shell/Terminal, File operations, VSCode
Server (code-server), JupyterLab, and MCP services in a single Docker
container. It targets AI agents and developers who need a unified, secure
execution environment with a shared filesystem across all those capabilities.

## The critical repo/runtime split (read this first)

This repository — `agent-infra/sandbox` — is **not** the source of the sandbox
runtime. Evidence:

- The quick start in `README.md` runs a prebuilt image
  (`ghcr.io/agent-infra/sandbox:latest`); nothing in this repo builds it.
- `.github/workflows/push-to-ghcr.yml` **pulls** an already-built multi-arch
  image from an upstream Volcengine registry
  (`enterprise-public-cn-beijing.cr.volces.com/vefaas-public/all-in-one-sandbox`)
  and re-tags/mirrors it into GHCR via `docker buildx imagetools create`. It
  never builds from a Dockerfile in this repo.
- `docker/` and `cli/` exist but contain only `.gitkeep` placeholders.
- The OpenAPI spec (`website/docs/public/v1/openapi.json`) describes a FastAPI
  service (`info.title: "FastAPI"`) that is not implemented anywhere here.

Therefore this repo's actual deliverables are:

1. **SDKs** (Python `agent-sandbox` on PyPI, JS `@agent-infra/sandbox` on npm,
   Go in a separate repo) — generated from the OpenAPI contract.
2. **The API contract itself** — the OpenAPI spec under
   `website/docs/public/v1/`, which is the source of truth for SDK generation.
3. **Documentation website** — Rspress-based, bilingual (en/zh), deployed at
   sandbox.agent-infra.com.
4. **Examples** — runnable integration examples against a locally started
   sandbox container.
5. **Evaluation harness** — LLM-driven MCP tool evaluation framework
   (`evaluation/`).

## System shape

Monorepo (pnpm workspace + per-package Python projects) containing libraries
and docs, plus an evaluation harness. No backend service code is present.

## Major components

| Component | Location | Nature |
|---|---|---|
| OpenAPI contract | `website/docs/public/v1/openapi.json` | Hand/fastAPI-exported spec; 123 paths, 255 schemas, tagged by API domain (sandbox, shell, bash, file, jupyter, nodejs, mcp, browser*, code, util, skills, proxy, display, auth) |
| Python SDK | `sdk/python/agent_sandbox` | Fern-generated (httpx + pydantic), sync & async clients, lazy sub-client properties per domain |
| JS SDK | `sdk/js/src` | Fern-generated core + hand-written providers; published as `@agent-infra/sandbox` |
| Go SDK | `sdk/go` | Placeholder pointing to separate repo `agent-infra/sandbox-sdk-go` (the generator output path also targets that external location) |
| Website | `website/` | Rspress docs (en/zh), hosts the OpenAPI spec publicly |
| Examples | `examples/` | Self-contained `uv run main.py` projects per integration |
| Evaluation | `evaluation/` | Async Python framework: agent loops (Azure OpenAI, OpenAI-compatible), XML task datasets, MCP streamable-HTTP client, Markdown reports |

## Runtime flow (representative: agent using the Python SDK)

```
Agent code
→ agent_sandbox.Sandbox(base_url=...)            # generated SDK
→ domain sub-client (file, bash, browser, …)
→ REST call against the running sandbox container's FastAPI service
  (single public port 8080; internal services on dedicated ports
   proxied through it)
→ sandbox executes in Docker (seccomp:unconfined) and returns JSON
```

The alternative integration path used by the evaluation harness is MCP:

```
Evaluation harness (evaluation/main.py)
→ MCP streamable HTTP client → http://<sandbox>:8080/mcp
→ MCP Hub aggregates browser / file / terminal / markitdown /
  chrome-devtools MCP servers inside the container
→ LLM agent loop (Azure OpenAI or OpenAI-compatible) calls tools
→ results scored against regex/response patterns from XML datasets
```

## External boundaries

- **Upstream image registry** (Volcengine CR) — source of the runtime image;
  GHCR is a mirror.
- **Volcengine VEFAAS** — cloud provider API for creating/deleting sandbox
  instances (hand-written `VolcengineProvider` in both SDKs).
- **Package registries** — PyPI (`agent-sandbox`), npm (`@agent-infra/sandbox`).
- **LLM providers** — Azure OpenAI and OpenAI-compatible endpoints
  (evaluation only).
- **GitHub Actions** — SDK CI, SDK publish (with version-bump commits), image
  mirroring on release.

## State ownership

This repo owns no persistent state. The sandbox container owns all execution
state (ephemeral by design; `restart: unless-stopped` in docker-compose).
Evaluation results are written to `evaluation/result/<YYYYMMDD>/` in UTC+8
date-bucketed directories. The OpenAPI spec is the authoritative contract
artifact.

## Auth model (runtime, documented but not implemented here)

The sandbox container supports optional API-key auth (`SANDBOX_API_KEY`,
three injection methods), JWT auth via `JWT_PUBLIC_KEY`, and one-time
short-lived tickets (`?ticket=`) for header-less clients like VNC. See
`website/docs/en/guide/basic/authentication.md` and
`docker-compose.yaml` env vars.

## Build and deployment

- JS/website tooling: pnpm workspace (`website`, `sdk/js`), Biome + Prettier.
- SDKs: Fern generates from the OpenAPI spec into `sdk/python` and `sdk/js`;
  publishing flows through GitHub Actions (`sdk-publish.yml`) with version
  bumping and dry-run support.
- See [runtime and deployment](runtime-and-deployment.md) for the container
  topology and [development and verification](../runbooks/development-and-verification.md)
  for commands.

## Related knowledge

- [Component model](component-model.md)
- [Runtime distribution model](../decisions/runtime-distribution-model.md)
- [SDK generation from OpenAPI](../decisions/sdk-generation-from-openapi.md)
- [API contract and version alignment](../constraints/api-contract-and-versions.md)
