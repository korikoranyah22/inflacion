from pathlib import Path
import csv, math, hashlib

HERE = Path(__file__).resolve().parent
V80 = HERE.parent / "V80"

def rows(p):
    with p.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

assert (HERE/"FOUR_LEG_PASS_PANEL_V81.csv").read_bytes() == (V80/"FOUR_LEG_PASS_PANEL_V80.csv").read_bytes()
cov = rows(HERE/"STRICT_Q4_FOUR_LEG_COVERAGE_V81.csv")[0]
assert abs(float(cov["asset_coverage_pct"]) - 23.54332498027319) < 1e-12
assert cov["increment_vs_v80_pp"] == "0"

rec = rows(HERE/"BCRA_PASS_AGGREGATE_RECONCILIATION_V81.csv")
for r in rec:
    assert abs(float(r["difference_million_ars"])) < 1e-6

ctl = rows(HERE/"BCRA_PUBLIC_BANK_PASS_AGGREGATE_CONTROL_V81.csv")
q4 = next(r for r in ctl if r["aggregation_period"] == "Q4_2023")
assert q4["four_leg_crosswalk_status"] == "NOT_ESTABLISHED"
assert q4["strict_panel_use"] == "CONTROL_ONLY_NO_ENTITY_PROMOTION"

print("QA_V81_PASS")
