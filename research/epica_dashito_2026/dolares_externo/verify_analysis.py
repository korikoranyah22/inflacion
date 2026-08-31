#!/usr/bin/env python3
"""Verificacion offline de los artefactos generados por build_analysis.py."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def read_csv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def close(actual: float, expected: float, tolerance: float = 1e-6) -> None:
    if not math.isclose(actual, expected, abs_tol=tolerance, rel_tol=0):
        raise AssertionError(f"{actual=} != {expected=} (tol={tolerance})")


def main() -> None:
    qa = json.loads((ROOT / "qa_results.json").read_text(encoding="utf-8"))
    assert qa["all_tests_pass"] is True

    bop = read_csv("bop_bridge_q1_2026.csv")
    values = {row["component"]: float(row["usd_millions"]) for row in bop}
    close(
        values["Bienes"] + values["Servicios"] + values["Ingreso primario"] + values["Ingreso secundario"],
        values["Cuenta corriente"],
    )

    reserve_flow = read_csv("reserve_flow_july_2026.csv")
    close(sum(float(row["usd_millions"]) for row in reserve_flow), 2729.0)

    claims = read_csv("reserve_claims_audit.csv")
    gross = float(claims[0]["usd_millions"])
    identified = sum(float(row["usd_millions"]) for row in claims[1:])
    close(gross, qa["derived"]["reserve_latest_usd_millions"], 0.001)
    close(identified, qa["derived"]["identified_claims_usd_millions"], 0.01)

    itcrm = read_csv("itcrm_daily.csv")
    assert itcrm[-1]["date"] == qa["derived"]["latest_itcrm_date"]
    close(float(itcrm[-1]["itcrm"]), qa["derived"]["latest_itcrm"], 0.001)

    regressions = read_csv("pass_through_distributed_ols.csv")
    assert len(regressions) == 5
    assert all(int(row["n"]) >= 16 for row in regressions)
    assert len(read_csv("counterexamples_fx_up_inflation_down.csv")) >= 2
    assert len(read_csv("evidence_sources.csv")) >= 9
    assert len(read_csv("gaps_matrix.csv")) == 8

    report = (ROOT / "ANALISIS_DOLARES_SECTOR_EXTERNO.md").read_text(encoding="utf-8")
    for token in ["50.784", "-1.651", "85,77", "6/6 controles aprobados"]:
        assert token in report

    print("OK: verificacion offline completa")


if __name__ == "__main__":
    main()
