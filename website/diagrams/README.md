# Diagram sources

Archify specs (skill `tt-a1i/archify`). Regenerate with
`node bin/archify.mjs deliver architecture <name>.architecture.json <name>.html --quality showcase`,
then export SVG from the delivered viewer into `docs/public/architecture/<name>.svg`:

- `aiod-overview.architecture.json` — the Introduction hero.
- `aiod-permission-model.architecture.json` — the permission model (Daemon → Architecture).
- `aiod-browser-cdp.architecture.json` — the two browser paths (Daemon → Browser API).
- `aiod-jupyter-kernel.architecture.json` — the kernels aiod spawns (Daemon → Jupyter).

`*.html` without a matching `.architecture.json` are hand-drawn SVG sources; the `<svg>` element is
extracted verbatim into `docs/public/architecture/<name>.svg`.

`aiod-capabilities.gen.py` writes the capability status board straight to `docs/public/architecture/aiod-capabilities.svg`.
