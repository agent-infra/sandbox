# Diagram sources

Archify specs (skill `tt-a1i/archify`). Regenerate with
`node bin/archify.mjs deliver <type> <name>.<type>.json <name>.html --quality showcase`,
then export SVG from the delivered viewer into `docs/public/architecture/<name>.svg`:

- `aiod-overview.architecture.json` — the Introduction hero.
- `aiod-permission-model.architecture.json` — the permission model (Daemon → Architecture).
- `aiod-browser-cdp.architecture.json` — the two browser paths (Daemon → Browser API).
- `aiod-jupyter-kernel.architecture.json` — the kernels aiod spawns (Daemon → Jupyter).
- `aiod-human-in-loop.architecture.json` — agent and person on the same objects (Daemon → Computer Use).
- `aiod-mcp-flow.architecture.json` — one endpoint, one tool list (Daemon → examples → MCP).
- `aio-sandbox-overview.architecture.json` — the surfaces inside the container (Guide → Introduction).
- `aio-agent-calls-sandbox.architecture.json` — agent outside, capabilities inside (Guide → Agent Call Sandbox vs In Sandbox).
- `aio-agent-in-sandbox.architecture.json` — agent process inside the container (Guide → Agent Call Sandbox vs In Sandbox).
- `aiod-watch-flow.sequence.json` — watch, poll, stop (Daemon → Files, Daemon → examples → file ops).
- `aiod-code-execution-flow.sequence.json` — dataset in, chart out (Daemon → examples → code execution).
- `aiod-code-backends.sequence.json` — which backend runs the code (Daemon → Code).
- `aiod-browser-use-flow.sequence.json` — serve a page, then drive it (Daemon → examples → browser use).
- `aiod-terminal-flow.sequence.json` — create, attach, run (Daemon → examples → terminal).
- `aiod-terminal-reconnect.sequence.json` — reattach with and without durable (Daemon → examples → terminal).

`*.html` without a matching spec are hand-drawn SVG sources; the `<svg>` element is
extracted verbatim into `docs/public/architecture/<name>.svg`.

`aiod-capabilities.gen.py` writes the capability status board straight to `docs/public/architecture/aiod-capabilities.svg`.
