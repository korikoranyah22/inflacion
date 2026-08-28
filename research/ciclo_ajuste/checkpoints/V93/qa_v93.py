from pathlib import Path
import csv, json
from decimal import Decimal, getcontext
getcontext().prec=80
base=Path(__file__).parent
factor=Decimal("1.532908152197492")
with (base/"BANCO_LA_PAMPA_Q4_FOUR_LEG_PROMOTION_V93.csv").open(encoding="utf-8") as f:
 rows=list(csv.DictReader(f))
q=[r for r in rows if r["period"]=="Q4-2023"][0]
assert Decimal(q["income_bcra"])==Decimal("24871195.212720731137404")
assert Decimal(q["expense_bcra"])==0
assert Decimal(q["income_otherfi"])==0
assert Decimal(q["expense_otherfi"])==Decimal("-0.715779426438328")
with (base/"STRICT_Q4_FOUR_LEG_COVERAGE_V93.csv").open(encoding="utf-8") as f:
 c=list(csv.DictReader(f))[0]
assert Decimal(c["asset_numerator_million_ars"])==Decimal("56847496.640")
assert Decimal(c["asset_coverage_pct"])==Decimal("58.788884622384821983684192349754601959464483825263446945330770576636958219960888")
assert c["closed_network_gate"].startswith("NO")
with (base/"CURRENT_STATE_V93.csv").open(encoding="utf-8") as f:
 s=list(csv.DictReader(f))
assert any(r["entity"]=="Banco de La Pampa S.E.M." and r["strict_panel_status"]=="ELIGIBLE" for r in s)
with (base/"RECOVERY_QUEUE_V93.csv").open(encoding="utf-8") as f:
 rq=list(csv.DictReader(f))
assert not any(r["entity"]=="Banco de La Pampa S.E.M." for r in rq)
assert any(r["entity"]=="Banco de Santiago del Estero S.A." and r["status"]=="OPEN_NEXT_AUTONOMOUS" for r in rq)
print("V93 QA PASS")
