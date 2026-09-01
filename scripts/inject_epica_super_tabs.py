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

# El tab histórico del BCRA conserva su snapshot original y suma un corte
# complementario que separa brutas, netas FMI y el residual del super-tab.
bcra_reserve_definitions = '''    <section id="bcraReserveDefinitions" class="card" style="margin-top:16px">
      <div class="card-head">
        <div class="card-title">Antes de graficar · Brutas, netas y residual <span>♡</span></div>
        <div class="kicker">corte complementario · fórmulas y fechas explícitas</div>
      </div>
      <div class="dp-kpi-grid bcra-debt-kpis">
        <div class="dp-kpi"><div class="tag">Reservas brutas · último dato público</div><div class="big">USD 50.861 M</div><div class="mini">27/08/2026 · stock oficial diario. No equivale a dólares libres.</div></div>
        <div class="dp-kpi"><div class="tag">Reservas netas FMI · última estimación pública</div><div class="big">≈−USD 6.500 M</div><div class="mini">Informe de mayo de 2026. No está sincronizada con la foto bruta de agosto.</div></div>
        <div class="dp-kpi"><div class="tag">Reservas netas FMI · corte diario</div><div class="big">N/D público</div><div class="mini">El BCRA reporta NIR al Fondo semanalmente; no localizamos una serie pública equivalente.</div></div>
        <div class="dp-kpi"><div class="tag">Residual estático · 31/07</div><div class="big">10.471 / 5.820</div><div class="mini">USD M hasta 1 mes / 1 año. Es una sensibilidad mecánica, no reservas netas.</div></div>
      </div>
      <div class="bcra-apb">
        <div><b>Definición del programa:</b> NIR = reservas oficiales brutas menos pasivos oficiales de reserva, valuados a tipos de cambio del programa. Entre los pasivos incluye swaps, encajes bancarios en moneda extranjera, SEDESA y otros depósitos definidos por el FMI.</div>
        <div><b>Por qué no actualizamos por resta simple:</b> el stock bruto diario no publica en esa misma fecha todo el perímetro necesario. Una cifra cercana a USD 10.000 M necesita fórmula, fecha y fuente antes de llamarse “reservas netas”.</div>
      </div>
      <div class="bcra-controls controls"><button class="subbtn" type="button" onclick="activateTab('tab-epica-dollars')">Abrir puente de liquidez →</button></div>
    </section>'''
if 'id="bcraReserveDefinitions"' not in text:
    bcra_chart_anchor = '''    <section class="card" style="margin-top:16px">
      <div class="card-head">
        <div class="card-title">① Reservas internacionales brutas <span>♡</span></div>'''
    assert text.count(bcra_chart_anchor) == 1, "No se encontró el bloque histórico de reservas BCRA"
    text = text.replace(bcra_chart_anchor, f"{bcra_reserve_definitions}\n\n{bcra_chart_anchor}", 1)
else:
    text = text.replace(
        '① bis · Brutas, netas y residual <span>♡</span>',
        'Antes de graficar · Brutas, netas y residual <span>♡</span>',
        1,
    )

bcra_measure_download = '        <a class="download-link" download href="research/epica_dashito_2026/deep_dive_2026-08-31/derived/reserve_measure_definitions_2026-09-01.csv">⬇ CSV · brutas, netas y residual</a>\n'
if bcra_measure_download not in text:
    bcra_download_anchor = "        <button class=\"download-link\" onclick=\"downloadBcraCsv('monthly')\">⬇ CSV · mensual consolidado</button>"
    assert text.count(bcra_download_anchor) == 1, "No se encontró el ancla de descargas BCRA"
    text = text.replace(bcra_download_anchor, bcra_measure_download + bcra_download_anchor, 1)

bcra_nir_sources = '''        <a class="source-link" target="_blank" rel="noopener" href="https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/reservas1.pdf">🏦 BCRA · reservas brutas diarias</a>
        <a class="source-link" target="_blank" rel="noopener" href="https://www.bcra.gob.ar/normas-especiales-para-la-divulgacion-de-datos-fmi/">🏦 BCRA · planilla SDDS</a>
        <a class="source-link" target="_blank" rel="noopener" href="https://www.imf.org/-/media/files/publications/cr/2026/english/1argea2026001.pdf">📄 FMI · definición y estimación NIR</a>
'''
if "📄 FMI · definición y estimación NIR" not in text:
    bcra_source_anchor = '        <a class="source-link" target="_blank" rel="noopener" href="https://www.bcra.gob.ar/reservas-internacionales-y-base-monetaria/">🏦 BCRA · reservas internacionales y base monetaria</a>'
    assert text.count(bcra_source_anchor) == 1, "No se encontró el ancla de fuentes BCRA"
    text = text.replace(bcra_source_anchor, bcra_nir_sources + bcra_source_anchor, 1)

bcra_old_cutoff_note = '<div class="sources-note"><b>Corte estático:</b> los archivos oficiales fueron descargados para esta edición y quedaron embebidos en el HTML. El último dato no coincide necesariamente entre variables: reservas/compra diaria llegan al 13/08/2026 en el libro descargado; tasas al 18/08/2026; A3500 al 19/08/2026. Los gráficos históricos usan sólo meses cerrados hasta julio de 2026, salvo la foto superior.</div>'
bcra_new_cutoff_note = '<div class="sources-note"><b>Cortes estáticos:</b> el snapshot superior conserva el libro descargado hasta el 13/08/2026; el comparador de medidas agrega reservas brutas al 27/08 y la última estimación pública de netas FMI de mayo. Tasas llegan al 18/08 y A3500 al 19/08. Los gráficos históricos usan sólo meses cerrados hasta julio de 2026.</div>'
if bcra_old_cutoff_note in text:
    assert text.count(bcra_old_cutoff_note) == 1, "Nota de corte BCRA ambigua"
    text = text.replace(bcra_old_cutoff_note, bcra_new_cutoff_note, 1)
else:
    assert bcra_new_cutoff_note in text, "No se encontró la nota de corte BCRA"

INDEX.write_text(text, encoding="utf-8", newline="\n")
print("OK: super-tabs inyectados en index.html")
