from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
ASSET = (ROOT / "assets" / "epica-super-tabs.js").read_text(encoding="utf-8")
DERIVED = ROOT / "research" / "epica_dashito_2026" / "deep_dive_2026-08-31" / "derived"


def rows(name: str) -> list[dict[str, str]]:
    with (DERIVED / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


assert INDEX.count('<script src="assets/epica-super-tabs.js?v=20260902-1"></script>') == 1
assert "touch-action:pan-y pinch-zoom!important" in ASSET
assert "scroll-snap-type:x proximity" in ASSET
assert "scheduleEpicaResponsiveRefresh" in ASSET
assert "orientationchange" in ASSET
assert "Plotly.Plots.resize(chart)" in ASSET
assert ".milei-cost-table-wrap, .epica-toolbar'" in INDEX
assert ".epica-toolbar, .pw-controls" not in INDEX
for tab in ("tab-epica-households", "tab-epica-dollars"):
    assert tab in INDEX, f"{tab} no está conectado a la navegación temática"
    assert ASSET.count(f'id="{tab}"') == 1, f"{tab} debe tener un único panel"
    assert ASSET.count(f'data-tab="{tab}"') >= 1, f"{tab} debe tener botón"

for group_fragment in (
    "featured:['tab-story','tab-epica-households','tab-epica-dollars'",
    "households:['tab-epica-households'",
    "prices:['tab-epica-dollars'",
    "state:['tab-epica-dollars'",
):
    assert group_fragment in INDEX, f"Falta navegación: {group_fragment}"

assert 'data-dash-group="featured" aria-pressed="false">Destacados</button>' in INDEX
assert 'data-dash-group="all" aria-pressed="true">Ver todo</button>' in INDEX
assert "let dashNavGroup='all';" in INDEX
assert "dashNavGroup=btn.dataset.dashGroup||'all';" in INDEX
assert "Todos los tabs aparecen al abrir el dashboard" in INDEX

summary = rows("eph_strategy_summary.csv")
exclusive = rows("eph_exclusive_profiles.csv")
for period in ("2025-S1", "2025-S2", "2026-Q1"):
    period_profiles = [
        row for row in exclusive
        if row["periodo"] == period and row["estrato_ipcf"] == "total"
    ]
    assert len(period_profiles) == 6
    assert abs(sum(float(row["porcentaje_ponderado"]) for row in period_profiles) - 100) < 0.01

latest_any = next(
    float(row["porcentaje_ponderado"])
    for row in summary
    if row["periodo"] == "2026-Q1"
    and row["estrato_ipcf"] == "total"
    and row["metrica"] == "cualquier_estrategia_v13_v17"
)
assert abs(latest_any - 71.778) < 0.001
assert "any:71.778" in ASSET

debt = [row for row in rows("debt_service_2026_2031.csv") if 2027 <= int(row["anio"]) <= 2031]
assert abs(sum(float(row["servicios_usd_m"]) for row in debt) - 243187.688) < 0.01
assert "USD 243.188 M" in ASSET

bridge = rows("bcra_reserve_liquidity_bridge.csv")
one_year = next(row for row in bridge if row["horizonte"] == "hasta_1_anio")
assert abs(float(one_year["residual_bruto_menos_flujos_usd_m"]) - 5819.75) < 0.001
assert "no es “reservas netas”" in ASSET

reserve_measures = rows("reserve_measure_definitions_2026-09-01.csv")
by_measure = {row["medida"]: row for row in reserve_measures}
assert float(by_measure["reservas_brutas_diarias"]["valor_usd_m"]) == 50861
assert float(by_measure["reservas_netas_fmi"]["valor_usd_m"]) == -6500
assert "Reservas netas FMI" in ASSET
assert "≈−USD 6.500 M" in ASSET
assert "netas diarias N/D público" in ASSET
assert 'id="bcraReserveDefinitions"' in INDEX
assert "Reservas netas FMI · última estimación pública" in INDEX
assert "Antes de graficar · Brutas, netas y residual" in INDEX
assert "snapshot superior conserva el libro descargado hasta el 13/08/2026" in INDEX

for relative in (
    "research/epica_dashito_2026/deep_dive_2026-08-31/derived/eph_exclusive_profiles.csv",
    "research/epica_dashito_2026/deep_dive_2026-08-31/derived/eph_strategy_summary.csv",
    "research/epica_dashito_2026/deep_dive_2026-08-31/derived/bcra_reserve_liquidity_bridge.csv",
    "research/epica_dashito_2026/deep_dive_2026-08-31/derived/reserve_measure_definitions_2026-09-01.csv",
    "research/epica_dashito_2026/deep_dive_2026-08-31/derived/debt_service_2026_2031.csv",
):
    assert (ROOT / relative).is_file(), f"Descarga inexistente: {relative}"
    assert f'href="{relative}"' in ASSET

print("OK: super-tabs Hogares y Dólares conectados y consistentes con los CSV auditados")
