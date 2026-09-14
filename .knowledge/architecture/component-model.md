---
type: architecture
---

# Component Model

Detailed responsibilities and dependency direction between the repo's
components. The overall shape is described in
[system overview](system-overview.md).

## OpenAPI contract (`website/docs/public/v1/openapi.json`)

The single source of truth for the HTTP API. Exported from the (external)
FastAPI runtime service. Path tags define SDK namespaces: `sandbox` (14
endpoints), `shell` (12), `bash` (7), `file` (11 + 6 file-watch), `jupyter`
(6), `nodejs` (7), `mcp` (3), `browser` family (52 across browser, page,
tabs, cookies, state, network, captcha), `code` (2), `util` (1), `skills`
(5), `proxy` (11), `display` (1), `auth` (2). Fern-specific extensions
(`x-fern-sdk-group-name`, `x-fern-sdk-method-name`) are already embedded in
the spec, so SDK naming is controlled at the spec level.

Fern config (`sdk/fern/generators.yml`) points at this spec and defines
three generator groups (python-sdk, js-sdk, sdk-go) writing into
`sdk/python/agent_sandbox`, `sdk/js/src`, and an **external** Go repo path.

## Python SDK (`sdk/python`)

- Package `agent_sandbox` (PyPI). httpx + pydantic based, sync and async
  variants of every domain client.
- `client.py` exposes the root `Sandbox` class whose domain sub-clients
  (`.sandbox`, `.bash`, `.file`, `.browser`, `.mcp`, …) are lazily
  instantiated properties over a shared `ClientWrapper`.
- Requires `volcengine-python-sdk` at runtime — the Volcengine cloud provider
  integration is bundled here, not a separate package.
- Build: setuptools (`setup.py`/`pyproject.toml`), published via
  `sdk/python/publish.sh` (build + twine) or the `sdk-publish.yml` workflow.

## JS SDK (`sdk/js`)

- Package `@agent-infra/sandbox` (npm). ESM + CJS dual output via rslib,
  types via tsc; Vitest test suite in `sdk/js/__test__/`.
- Layout: `src/api/**` is Fern-generated; `src/core/**` is the generated
  runtime (fetcher, headers, form-data, URL building); `src/Client.ts` and
  `src/BaseClient.ts` assemble domain resource clients.
- **Hand-written layer**: `src/providers/**` defines `BaseProvider`
  (abstract createSandbox/deleteSandbox/getSandbox/listSandboxes) and
  `VolcengineProvider` (VEFAAS API with request signing in `sign.ts`).
  Tests in `__test__/providers/volcengine.test.ts` and a `.e2e.test.ts`
  file indicate the signing logic is the main hand-tested surface.
- `src/index.ts` exports the generated API surface as `SandboxApi`, the
  `SandboxClient`, and `providers`.

## Website (`website/`)

Rspress static site (en/zh via `i18n.json`), docs root at `website/docs`.
Guides cover every API domain (basic/) plus advanced topics (security,
proxy, lifecycle, browser cookies, workspace, cloud deployment) and
integration docs for Codex/OpenCode/AIO-CLI. The OpenAPI spec is served
from `docs/public/v1/` and rendered with Scalar in the API reference page.
Build output goes to `doc_build/` (gitignored).

## Examples (`examples/`)

Twelve self-contained projects, each with its own `pyproject.toml` +
`uv.lock`, all following the `examples/_template` convention: start the
sandbox container locally, then `uv run main.py`. They cover SDK basics
(files, code execution), framework integrations (OpenAI, browser-use,
Playwright, LangGraph deepagents, AG2, MiniMax), Volcengine provider usage,
and site-to-markdown / OSS upload utilities. Examples depend on the Python
SDK from PyPI, not on the repo workspace.

## Evaluation harness (`evaluation/`)

Standalone uv-managed Python project (requires Python 3.13). Key modules:

- `agent_loop.py` — strategy-pattern agent loops over an MCP `ClientSession`:
  `AzureOpenAIAgentLoop` (default), `OpenAIAgentLoop` (any OpenAI-compatible
  base_url, e.g. MiniMax, with model-specific quirks: MiniMax needs
  temperature > 0; MiniMax-M2 thinking tags are stripped), and an
  unimplemented `LangGraphAgentLoop` placeholder. Loops force retries when
  the model omits the required `<response>/<summary>/<feedback>` tags.
- `dataset_parser.py` — parses XML task files; prefers `<response>` over
  `<response_pattern>` (regex).
- `main.py` — orchestrates serial evaluation, maintains a global MCP
  session to the sandbox's streamable-HTTP endpoint, uploads fixture files
  (e.g. `/tmp/main.py`, `evaluation.xml`) into the sandbox via
  `sandbox_file_operations`, scores with `re.search` against the expected
  pattern, and emits per-category Markdown reports (including a tool-call
  timeline reconstructed from timestamps).
- `dataset/*.xml` — categories: ping, basic, browser, browser_advanced,
  code_advanced, collaboration, editor, packages, error, util, workflow,
  nextjs.
- `result/20251112/` — last recorded results (100% pass) plus
  `improvement_suggestions.md`, a detailed Linus-flavored analysis of tool
  ergonomics issues found during evaluation (undo_edit semantics,
  execute_code return inconsistency, browser_evaluate wrapping, unstructured
  get_packages output, etc.). This file is the de-facto backlog for runtime
  improvements.
- `tests/` — unit tests for max-iteration fallback (mocked OpenAI) and
  MiniMax integration tests (skipped without `MINIMAX_API_KEY`).

## CI/CD (`.github/workflows/`)

- `sdk-ci.yml` — builds/tests the JS SDK on pushes touching `sdk/js` or
  `sdk/fern`.
- `sdk-publish.yml` — manual dispatch; bumps versions, publishes to
  npm/PyPI, commits the version bump back to the branch (Python job runs
  after JS, tolerating `skipped`).
- `push-to-ghcr.yml` — release-triggered image mirroring (see
  [image mirroring CI](../decisions/image-mirror-cd.md)).

## Dependency direction

```
OpenAPI spec (website/docs/public/v1/openapi.json)
    ↓ Fern codegen
Python SDK ←── examples (PyPI dependency)
JS SDK
    ↓ hand-written extension
providers (Volcengine) — inside each SDK, not shared

evaluation/ — depends on a running sandbox over MCP (not on the SDKs)
website/ — depends on the spec it hosts; SDKs depend on nothing in the repo
```

Nothing in this repo depends on the runtime source; all consumers depend on
the published image and the published contract.

## Anomalies and unknowns

- `cli/` and `docker/` are empty placeholders (`.gitkeep` only). The website
  documents an "AIO CLI" (`guide/basic/aio-cli.md`), suggesting the CLI
  lives elsewhere or is planned; **unknown** whether these directories are
  future homes or leftovers.
- `sdk/go/` contains only a README pointing to `agent-infra/sandbox-sdk-go`;
  the Fern Go generator likewise outputs to a path outside this repo
  (`../../sandbox-sdk-go`). The Go SDK is therefore not maintained here.
- `Downloads/` exists at the repo root and is empty — purpose unknown,
  likely a sandboxed-editor artifact.
- CONTRIBUTING.md references a different repo layout (`sdk/javascript`,
`sdk/python/src`, `website` inside `sdk/`) than what exists — it appears
stale/inherited from the predecessor `sandbox-sdk` repo.

## Related knowledge

- [System overview](system-overview.md)
- [SDK generation from OpenAPI](../decisions/sdk-generation-from-openapi.md)
- [Development and verification](../runbooks/development-and-verification.md)
