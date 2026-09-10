#!/usr/bin/env python3
"""Generate the aiod dependency/capability list figure.

Writes docs/public/architecture/aiod-capabilities.svg.
"""
from pathlib import Path

INK = "#2d3142"
MUTED = "#4f5d75"
ACCENT = "#eb6c36"

W = 640
CAPTION_Y = 14
LIST_TOP = 32
ROW_H = 48

# column offsets, relative to the content block; gaps are a uniform 32px
# measured against the widest cell in each column
DOT_DX = 4
NAME_DX = 22
PROBE_DX = 198
ROUTE_DX = 337
CONTENT_W = 475
LEFT = round((W - CONTENT_W) / 2)      # 74
RAIL_R = LEFT + CONTENT_W              # 565

DOT_CX = LEFT + DOT_DX
NAME_X = LEFT + NAME_DX
PROBE_X = LEFT + PROBE_DX
ROUTE_X = LEFT + ROUTE_DX

ROWS = [
    dict(name="Shell", probe="bash · PowerShell", route="/v2/commands · /v2/pty", ok=True),
    dict(name="Interpreters", probe="python3 · node", route="/v2/code", ok=True),
    dict(name="Chromium", probe="CDP :9222", route="/v2/browser", ok=True),
    dict(name="computer-use worker", probe="127.0.0.1:18100", route="/v2/computer", ok=False),
]

H = LIST_TOP + ROW_H * len(ROWS)

out = []
out.append('<?xml version="1.0" encoding="UTF-8"?>')
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'width="{W}" height="{H}" role="img" '
           f'aria-label="aiod dependency probes and the v2 routes they enable">')
out.append('''<defs><style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&amp;family=Geist+Mono:wght@400;500;600&amp;display=swap');
.s { font-family: Geist, "Helvetica Neue", Arial, sans-serif; }
.m { font-family: "Geist Mono", ui-monospace, "SF Mono", Menlo, monospace; }
</style></defs>''')

# caption
out.append(f'<text class="m" x="{LEFT}" y="{CAPTION_Y}" font-size="10.5" '
           f'fill="{MUTED}"><tspan fill="{INK}" fill-opacity="0.55">GET </tspan>'
           f'/v1/capabilities</text>')

for i, r in enumerate(ROWS):
    top = LIST_TOP + i * ROW_H
    cy = top + ROW_H / 2
    base = cy + 4.5
    if i:
        out.append(f'<path d="M{LEFT} {top}.5H{RAIL_R}" stroke="{INK}" stroke-opacity="0.1"/>')

    if r["ok"]:
        out.append(f'<circle cx="{DOT_CX}" cy="{cy}" r="3.5" fill="{INK}" fill-opacity="0.85"/>')
        name_op, text_op = 1, 0.6
    else:
        out.append(f'<circle cx="{DOT_CX}" cy="{cy}" r="3.4" fill="none" '
                   f'stroke="{ACCENT}" stroke-width="1.4"/>')
        name_op, text_op = 0.5, 0.38

    out.append(f'<text class="s" x="{NAME_X}" y="{base}" font-size="14" font-weight="600" '
               f'fill="{INK}" fill-opacity="{name_op}">{r["name"]}</text>')
    out.append(f'<text class="m" x="{PROBE_X}" y="{base}" font-size="10.5" '
               f'fill="{INK}" fill-opacity="{text_op}">{r["probe"]}</text>')
    out.append(f'<text class="m" x="{ROUTE_X}" y="{base}" font-size="10.5" '
               f'fill="{INK}" fill-opacity="{text_op}">{r["route"]}</text>')

    if not r["ok"]:
        cw, ch = 32, 15
        cx = ROUTE_X + round(len(r["route"]) * 6.3) + 10
        out.append(f'<rect x="{cx}" y="{cy-ch/2}" width="{cw}" height="{ch}" rx="3" '
                   f'fill="{ACCENT}" fill-opacity="0.1" stroke="{ACCENT}" stroke-opacity="0.4"/>')
        out.append(f'<text class="m" x="{cx+cw/2}" y="{cy+3.4}" font-size="9.5" '
                   f'font-weight="500" text-anchor="middle" fill="{ACCENT}">503</text>')

out.append('</svg>')

dest = Path(__file__).resolve().parents[1] / "docs/public/architecture/aiod-capabilities.svg"
dest.write_text("\n".join(out) + "\n", encoding="utf-8")
print(dest, f"viewBox 0 0 {W} {H}")
