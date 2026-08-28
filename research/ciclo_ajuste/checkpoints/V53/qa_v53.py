#!/usr/bin/env python3
from pathlib import Path
import csv, json, math, sys

ROOT = Path(__file__).resolve().parent
required = [
    "SECURITIES_ISSUER_VALUATION_SPLIT_V53.csv",
    "INTEREST_INCOME_SECTOR_SPLIT_V53.csv",
    "CER_ASSET_LIABILITY_SECTOR_MAP_V53.csv",
    "FX_GROSS_COUNTERPARTY_MAP_V53.csv",
    "HOUSEHOLD_DIRECT_FLOW_BOUND_V53.csv",
    "AUDITORIA_CUANTIFICACION_CONTRAPARTES_V53.md",
    "VEREDICTO_CUANTIFICACION_CONTRAPARTES_V53.md",
    "EVIDENCE_LEDGER_CICLO_AJUSTE_V53.csv",
    "README_V53.md",
    "FUENTES_V53.md",
    "PROMPT_CODEX_V54_RAW_BCRA_MICRODATA.md",
    "BASE_V52.zip",
]
for name in required:
    p = ROOT / name
    assert p.exists() and p.stat().st_size > 0, f"missing/empty: {name}"

with (ROOT/"HOUSEHOLD_DIRECT_FLOW_BOUND_V53.csv").open(encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

by_target = {r["target"]: r for r in rows}
def num(r, k): return float(r[k])

classified = by_target["Strictly resolved classification mass"]
unresolved = by_target["Unresolved/mixed mass"]
assert math.isclose(num(classified,"identified_min_pp"), 19.0, abs_tol=1e-9)
assert math.isclose(num(unresolved,"identified_min_pp"), 9.7, abs_tol=1e-9)
assert math.isclose(num(classified,"identified_min_pp")+num(unresolved,"identified_min_pp"), 28.7, abs_tol=1e-9)
assert math.isclose(num(classified,"min_pct_gross_positive")+num(unresolved,"min_pct_gross_positive"), 100.0, abs_tol=0.02)

hh = by_target["Household direct contractual bank revenue — strictly isolated bucket"]
assert math.isclose(num(hh,"logical_bucket_ceiling_pp"), 2.1, abs_tol=1e-9)
assert num(hh,"identified_min_pp") == 0.0

bcra = by_target["BCRA-linked accounting contribution"]
assert math.isclose(num(bcra,"identified_min_pp"), 7.7, abs_tol=1e-9)

market = by_target["Market valuation"]
assert math.isclose(num(market,"identified_min_pp"), 11.3, abs_tol=1e-9)

# No HTML should be generated.
assert not list(ROOT.glob("*.html")), "V53 must not modify/create HTML"

# Guard against dangerous language in verdict.
verdict = (ROOT/"VEREDICTO_CUANTIFICACION_CONTRAPARTES_V53.md").read_text(encoding="utf-8")
assert "DIRECT_HOUSEHOLD_TO_BANK_TRANSFER" in verdict
assert "NOT_IDENTIFIED_AT_ABNORMAL_GAP_LEVEL" in verdict
assert "HOUSEHOLD_DIRECT_POINT_ESTIMATE" in verdict
assert "= N/D" in verdict

print("QA V53 PASS")
