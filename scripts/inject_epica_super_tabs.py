from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = '<script src="assets/epica-super-tabs.js"></script>'

text = INDEX.read_text(encoding="utf-8")

if MARKER not in text:
    anchor = "\n<script>\nconst DASHBOARD_SNAPSHOT_CUTOFF = '2026-08-21';"
    replacement = f"\n{MARKER}\n\n<script>\nconst DASHBOARD_SNAPSHOT_CUTOFF = '2026-08-21';"
    assert text.count(anchor) == 1, "No se encontró el inicio del script principal"
    text = text.replace(anchor, replacement, 1)

old_badge = "📌 cierre editorial · 25 ago 2026 · sin actualización automática"
new_badge = "📌 base histórica · 25 ago 2026 · super-tabs auditados al 31 ago"
if old_badge in text:
    text = text.replace(old_badge, new_badge, 1)

text = text.replace(
    "· todo en un solo HTML",
    "· todo en un dashboard auditable",
    1,
)
text = text.replace(
    "<b>📌 Snapshot editorial:</b> esta versión queda cerrada al <b>21/08/2026</b>.",
    "<b>📌 Cortes visibles:</b> núcleo histórico al <b>21/08/2026</b> y super-tabs auditados al <b>31/08/2026</b>.",
    1,
)
text = text.replace(
    "Las fuentes remotas que el archivo consulta para dibujar algunas series están limitadas por fecha y <b>no incorporarán publicaciones posteriores a este corte</b>.",
    "Las fuentes remotas del núcleo histórico están limitadas por fecha y <b>no incorporarán publicaciones posteriores al 21/08/2026</b>; los super-tabs usan copias locales cerradas al 31/08/2026.",
    1,
)

replacements = {
    "featured:['tab-story','tab-epica-households','tab-epica-dollars',": "featured:['tab-story','tab-epica-households','tab-epica-dollars','tab-epica-caputo-colchon',",
    "households:['tab-epica-households',": "households:['tab-epica-households','tab-epica-caputo-colchon',",
    "prices:['tab-epica-dollars',": "prices:['tab-epica-dollars','tab-epica-caputo-colchon',",
    "state:['tab-epica-dollars',": "state:['tab-epica-dollars','tab-epica-caputo-colchon',",
}
for old, new in replacements.items():
    if new not in text:
        assert text.count(old) == 1, f"No se encontró ancla única: {old}"
        text = text.replace(old, new, 1)

INDEX.write_text(text, encoding="utf-8", newline="\n")
print("OK: super-tabs inyectados en index.html")
