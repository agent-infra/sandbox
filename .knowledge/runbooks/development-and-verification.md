---
type: runbook
---

# Development and Verification

## Repository layout expectations

- pnpm workspace: `website` and `sdk/js` are the JS packages. Root
  `package.json` is a shell holding only shared dev tooling (Biome,
  Prettier, TypeScript types).
- Python projects are independent, uv-managed: `sdk/python`,
  `evaluation`, and each `examples/*`.
- The sandbox runtime itself is **not buildable from this repo** — start it
  from the published image (see below).

## Common commands

### JS SDK (`sdk/js`)

```bash
cd sdk/js
pnpm install
pnpm build          # rslib build && tsc  (ESM + CJS + types)
pnpm test           # vitest (unit tests incl. providers/signing)
pnpm test:coverage
```

### Website (`website`)

```bash
cd website
pnpm install
pnpm dev            # Rspress dev server
pnpm build          # output in doc_build/ (gitignored)
pnpm check          # biome check --write
```

Lint/format at repo root: Biome (see `biome.json`) and Prettier
(`.prettierrc` — single quotes; lock files are prettier-ignored).

### Python SDK (`sdk/python`)

```bash
cd sdk/python
python -m build     # build package into dist/
# publish: ./publish.sh  (twine upload) — normally done via sdk-publish.yml
```

### Evaluation harness (`evaluation`)

Requires Python >= 3.13 and uv.

```bash
cd evaluation
uv sync
cp .env.example .env   # set AZURE_OPENAI_* or OPENAI_*, and MCP_SERVER_URL

uv run main.py                       # all categories, serially
uv run main.py --eval basic           # single category
uv run main.py --agent openai \
    --openai-base-url https://api.minimax.io/v1 \
    --openai-model MiniMax-M2.7      # OpenAI-compatible backend
```

Unit tests (no live sandbox or LLM needed for the mocked ones):

```bash
uv run python -m unittest discover -s tests
# MiniMax live tests require MINIMAX_API_KEY and are auto-skipped otherwise
```

Reports land in `evaluation/result/<YYYYMMDD>/<category>.md` (UTC+8 dates).

## Local sandbox prerequisite

Most examples and the evaluation harness need a running sandbox:

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -e SANDBOX_API_KEY=your-secret-key \
  -p 127.0.0.1:8080:8080 ghcr.io/agent-infra/sandbox:latest
```

- `seccomp:unconfined` is mandatory (Chrome in container).
- Bind the host port to 127.0.0.1 only — the sandbox listens on 0.0.0.0
  inside the container.
- The evaluation harness talks to `http://localhost:8080/mcp` (MCP
  streamable HTTP) by default (`MCP_SERVER_URL`).
- Examples read `SANDBOX_BASE_URL` (default `http://localhost:8080`) and may
  need provider credentials (e.g. Volcengine AK/SK for
  `examples/volcengine-provider`).

## Environment variables that matter

| Where | Variable | Purpose |
|---|---|---|
| evaluation | `AZURE_OPENAI_*` / `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL` | LLM backend |
| evaluation | `MCP_SERVER_URL` | Sandbox MCP endpoint |
| examples | `SANDBOX_BASE_URL` | Sandbox REST endpoint |
| examples | Volcengine AK/SK vars | Cloud provider examples |

Secrets are loaded via `.env` files (never committed; see `.gitignore`).

## Verification checklist before proposing changes

1. JS changes: `pnpm build && pnpm test` in `sdk/js` (CI `sdk-ci.yml` runs
   the same on `sdk/js/**` or `sdk/fern/**` touches).
2. Never hand-edit Fern-generated files — regenerate via `sdk/fern`
   generators and keep `fern-customizations.test.ts` green.
3. Docs changes: build the website (`pnpm build` in `website/`); dead-link
   checking is disabled (`checkDeadLinks: false`), so verify links manually.
4. Evaluation dataset changes: prompts, `<response>`/`<response_pattern>`
   values, and harness-uploaded fixtures (`/tmp/main.py`,
   `/tmp/evaluation.xml`) must stay consistent.
5. Publishing is **not** done locally in the normal flow — use the
   `sdk-publish.yml` workflow (supports dry runs) so version-bump commits
   land on the branch consistently.

## Related knowledge

- [System overview](../architecture/system-overview.md)
- [Component model](../architecture/component-model.md)
- [API contract and version alignment](../constraints/api-contract-and-versions.md)
