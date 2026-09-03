from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
ASSET = (ROOT / "assets" / "epica-stage2-tabs.js").read_text(encoding="utf-8")


def csv_rows(relative: str) -> list[dict[str, str]]:
    with (ROOT / relative).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


for tab_id in ("tab-epica-incidence", "tab-epica-development", "tab-epica-narratives"):
    assert ASSET.count(f'id="{tab_id}"') == 1
    assert ASSET.count(f'data-tab="{tab_id}"') >= 1
    assert tab_id in INDEX

assert '<script src="assets/epica-stage2-tabs.js?v=20260902-1"></script>' in INDEX
assert ".epica-actor-grid{display:grid;min-width:0;max-width:100%" in ASSET
assert ".epica-narrative-card{display:grid;min-width:0" in ASSET
assert "min-height:42px" in ASSET
assert "window.addEventListener('resize'" not in ASSET
assert "¿Qué cambió para cada actor?" in ASSET
assert "¿Cuándo la inversión se convierte en trabajo y capacidad?" in ASSET
assert "¿Qué pregunta abre cada frase?" in ASSET
assert "27 frases de origen" in ASSET and "40 preguntas" in ASSET

for forbidden in ("hipótesis que sobrevive", "veredicto", "falsifica", "refuta"):
    assert forbidden not in ASSET.lower()

downloads = (
    "research/epica_dashito_2026/fiscal_desarrollo/matriz_incidencia.csv",
    "research/epica_dashito_2026/fiscal_desarrollo/hallazgos_cuantitativos.csv",
    "research/epica_dashito_2026/hogares_credito/matriz_evidencia.csv",
    "research/epica_dashito_2026/deep_dive_2026-08-31/derived/rigi_summary.csv",
    "research/epica_dashito_2026/deep_dive_2026-08-31/derived/rigi_investment_schedule.csv",
    "research/epica_dashito_2026/deep_dive_2026-08-31/derived/public_capital_accounting_inventory.csv",
    "research/epica_dashito_2026/claims_registry.csv",
    "research/epica_dashito_2026/execution_matrix.csv",
    "research/epica_dashito_2026/deep_dive_2026-08-31/gap_resolution_matrix.csv",
)
for relative in downloads:
    assert (ROOT / relative).is_file(), f"Falta descarga: {relative}"
    assert f'href="{relative}"' in ASSET, f"Descarga no enlazada: {relative}"

claims = csv_rows("research/epica_dashito_2026/claims_registry.csv")
assert len(claims) == 27
assert all(row["logical_reading"] and row["evidence_status"] for row in claims)
assert not any(row["logical_reading"].startswith("false") for row in claims)

incidence = csv_rows("research/epica_dashito_2026/fiscal_desarrollo/matriz_incidencia.csv")
assert any(row["grupo"] == "asalariados públicos" and row["saldo"] == "-16.52%" for row in incidence)

rigi = csv_rows("research/epica_dashito_2026/deep_dive_2026-08-31/derived/rigi_summary.csv")[0]
assert int(rigi["proyectos_aprobados_deduplicados"]) == 22
assert int(rigi["proyectos_con_desglose_temporal_permanente"]) == 0

print("OK: super-tabs Quién paga, Desarrollo y Relatos conectados a evidencia neutral")
