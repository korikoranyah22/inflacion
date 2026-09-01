from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = '<script src="assets/epica-super-tabs.js"></script>'
STAGE2_MARKER = '<script src="assets/epica-stage2-tabs.js"></script>'

text = INDEX.read_text(encoding="utf-8")

if MARKER not in text:
    anchor = "\n<script>\nconst DASHBOARD_SNAPSHOT_CUTOFF = '2026-08-21';"
    replacement = f"\n{MARKER}\n\n<script>\nconst DASHBOARD_SNAPSHOT_CUTOFF = '2026-08-21';"
    assert text.count(anchor) == 1, "No se encontró el inicio del script principal"
    text = text.replace(anchor, replacement, 1)

if STAGE2_MARKER not in text:
    assert text.count(MARKER) == 1, "No se encontró el asset base de la épica"
    text = text.replace(MARKER, f"{MARKER}\n{STAGE2_MARKER}", 1)

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
if "'tab-epica-incidence'" not in text:
    for old, new in replacements.items():
        if new not in text:
            assert text.count(old) == 1, f"No se encontró ancla única: {old}"
            text = text.replace(old, new, 1)

stage2_replacements = {
    "featured:['tab-story','tab-epica-households','tab-epica-dollars','tab-epica-caputo-colchon',": "featured:['tab-story','tab-epica-households','tab-epica-dollars','tab-epica-incidence','tab-epica-development','tab-epica-narratives','tab-epica-caputo-colchon',",
    "households:['tab-epica-households','tab-epica-caputo-colchon',": "households:['tab-epica-households','tab-epica-incidence','tab-epica-narratives','tab-epica-caputo-colchon',",
    "prices:['tab-epica-dollars','tab-epica-caputo-colchon',": "prices:['tab-epica-dollars','tab-epica-narratives','tab-epica-caputo-colchon',",
    "activity:['tab-consumption',": "activity:['tab-epica-development','tab-epica-narratives','tab-consumption',",
    "state:['tab-epica-dollars','tab-epica-caputo-colchon',": "state:['tab-epica-dollars','tab-epica-incidence','tab-epica-development','tab-epica-narratives','tab-epica-caputo-colchon',",
    "power:['tab-pendulo',": "power:['tab-epica-incidence','tab-epica-narratives','tab-pendulo',",
}
for old, new in stage2_replacements.items():
    if new not in text:
        assert text.count(old) == 1, f"No se encontró ancla de etapa 2: {old}"
        text = text.replace(old, new, 1)

duplicate_sequences = {
    "'tab-epica-incidence','tab-epica-development','tab-epica-narratives','tab-epica-caputo-colchon','tab-epica-incidence','tab-epica-development','tab-epica-narratives','tab-epica-caputo-colchon'": "'tab-epica-incidence','tab-epica-development','tab-epica-narratives','tab-epica-caputo-colchon'",
    "'tab-epica-incidence','tab-epica-narratives','tab-epica-caputo-colchon','tab-epica-incidence','tab-epica-narratives','tab-epica-caputo-colchon'": "'tab-epica-incidence','tab-epica-narratives','tab-epica-caputo-colchon'",
    "'tab-epica-narratives','tab-epica-caputo-colchon','tab-epica-narratives','tab-epica-caputo-colchon'": "'tab-epica-narratives','tab-epica-caputo-colchon'",
}
for duplicate, normalized in duplicate_sequences.items():
    text = text.replace(duplicate, normalized)

# El menú completo es el estado inicial. Los grupos temáticos quedan como filtros
# opcionales y nunca deben hacer que los tabs parezcan eliminados al abrir la página.
menu_default_replacements = {
    '<button class="dash-topic-btn active" type="button" data-dash-group="featured" aria-pressed="true">Destacados</button>': '<button class="dash-topic-btn" type="button" data-dash-group="featured" aria-pressed="false">Destacados</button>',
    '<button class="dash-topic-btn" type="button" data-dash-group="all" aria-pressed="false">Ver todo</button>': '<button class="dash-topic-btn active" type="button" data-dash-group="all" aria-pressed="true">Ver todo</button>',
    'Mostramos menos accesos a la vez para que la portada respire. La pestaña que ya abriste queda siempre visible.': 'Todos los tabs aparecen al abrir el dashboard. Los filtros temáticos permiten reducir el menú cuando lo necesites.',
    "let dashNavGroup='featured';": "let dashNavGroup='all';",
    "dashNavGroup=btn.dataset.dashGroup||'featured';": "dashNavGroup=btn.dataset.dashGroup||'all';",
}
for old, new in menu_default_replacements.items():
    if old in text:
        assert text.count(old) == 1, f"Ancla ambigua al restaurar el menú: {old}"
        text = text.replace(old, new, 1)
    else:
        assert new in text, f"No se encontró el estado anterior ni el nuevo: {old}"

INDEX.write_text(text, encoding="utf-8", newline="\n")
print("OK: super-tabs inyectados en index.html")
