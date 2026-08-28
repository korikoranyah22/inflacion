from pathlib import Path
import csv
from decimal import Decimal, getcontext
getcontext().prec=80
base=Path(__file__).parent
with (base/"BST_Q4_FOUR_LEG_PROMOTION_V96.csv").open(encoding="utf-8") as f: rows=list(csv.DictReader(f))
q=[r for r in rows if r["period"]=="Q4-2023"][0]
assert Decimal(q["income_bcra"])==Decimal("12365122.634821469517664")
assert Decimal(q["expense_bcra"])==Decimal("0")
assert Decimal(q["income_otherfi"])==Decimal("48716.595730834366476")
assert Decimal(q["expense_otherfi"])==Decimal("21762.074146383823128")
with (base/"STRICT_Q4_FOUR_LEG_COVERAGE_V96.csv").open(encoding="utf-8") as f: c=list(csv.DictReader(f))[0]
assert Decimal(c["asset_numerator_million_ars"])==Decimal("57803557.512")
assert Decimal(c["asset_coverage_pct"])==Decimal("59.777595746322620480650441147276358824911189326119979767253088259998915899707248")
assert Decimal(c["increment_vs_v95_pp"])==Decimal("0.167822844340690621732552044117742185489828969088513593377207215863794809877346")
assert c["closed_network_gate"].startswith("NO")
with (base/"CURRENT_STATE_V96.csv").open(encoding="utf-8") as f: s=list(csv.DictReader(f))
assert any(r["entity"]=="Banco de Servicios y Transacciones S.A." and r["strict_panel_status"]=="ELIGIBLE" for r in s)
assert any(r["entity"]=="Banco CMF S.A." and r["q4_four_leg_status"]=="N/D_STRICT" for r in s)
assert any(r["entity"]=="Banco del Chubut S.A." and r["q4_four_leg_status"]=="N/D_STRICT" for r in s)
with (base/"BST_BCRA_RAW_ACCOUNT_AUDIT_V96.csv").open(encoding="utf-8") as f: rr=list(csv.DictReader(f))
assert sum(Decimal(r["absolute_result_k"]) for r in rr if r["period"]=="202309" and r["account"] in {"511108","511027"})==Decimal("7577705")
assert any(r["period"]=="202309" and r["account"]=="521022" and Decimal(r["absolute_result_k"])==Decimal("107266") for r in rr)
assert any(r["period"]=="202312" and r["account"]=="511108" and Decimal(r["absolute_result_k"])==Decimal("23689034") for r in rr)
with (base/"RECOVERY_QUEUE_V96.csv").open(encoding="utf-8") as f: rq=list(csv.DictReader(f))
assert not any(r["entity"]=="Banco de Servicios y Transacciones S.A." for r in rq)
assert any(r["entity"]=="Banco Columbia S.A." and r["status"]=="OPEN_NEXT_AUTONOMOUS" for r in rq)
print("V96 QA PASS")
