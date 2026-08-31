from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def read_csv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


required = [
    "DEEP_DIVE_RESULTS.md",
    "gap_resolution_matrix.csv",
    "source_manifest.csv",
    "derived/eph_strategy_summary.csv",
    "derived/eph_exclusive_profiles.csv",
    "derived/bcra_reserve_liquidity_bridge.csv",
    "derived/debt_wall_summary.csv",
    "derived/rigi_summary.csv",
    "derived/public_capital_accounting_inventory.csv",
]
for relative in required:
    assert (ROOT / relative).is_file(), f"Falta {relative}"

manifest = read_csv("source_manifest.csv")
source_files = sorted(path for path in (ROOT / "sources").rglob("*") if path.is_file())
assert len(manifest) == len(source_files)
by_path = {row["ruta_relativa"]: row for row in manifest}
for file in source_files:
    relative = file.relative_to(ROOT / "sources").as_posix()
    assert relative in by_path
    digest = hashlib.sha256(file.read_bytes()).hexdigest()
    assert digest == by_path[relative]["sha256"]

eph = read_csv("derived/eph_strategy_summary.csv")
latest_any = next(
    row for row in eph
    if row["periodo"] == "2026-Q1"
    and row["estrato_ipcf"] == "total"
    and row["metrica"] == "cualquier_estrategia_v13_v17"
)
assert abs(float(latest_any["porcentaje_ponderado"]) - 71.778) < 0.001

rigi = read_csv("derived/rigi_summary.csv")[0]
assert int(rigi["proyectos_aprobados_deduplicados"]) == 22
assert float(rigi["inversion_comprometida_usd_m"]) == 47073
assert int(rigi["empleos_directos_indirectos_proyectados"]) == 95950

debt = read_csv("derived/debt_wall_summary.csv")[0]
assert abs(float(debt["servicios_usd_m"]) - 243187.688) < 0.001

bridge = read_csv("derived/bcra_reserve_liquidity_bridge.csv")
one_year = next(row for row in bridge if row["horizonte"] == "hasta_1_anio")
assert abs(float(one_year["residual_bruto_menos_flujos_usd_m"]) - 5819.75) < 0.001

print(
    f"OK: deep dive validado; {len(source_files)} fuentes con SHA-256; "
    "EPH, RIGI, BCRA, deuda y capital público consistentes"
)
