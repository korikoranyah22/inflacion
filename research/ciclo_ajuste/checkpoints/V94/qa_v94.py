from pathlib import Path
import csv
from decimal import Decimal, getcontext
getcontext().prec=80
base=Path(__file__).parent
with (base/"BPN_Q4_FOUR_LEG_PROMOTION_V94.csv").open(encoding="utf-8") as f:
 rows=list(csv.DictReader(f))
q=[r for r in rows if r["period"]=="Q4-2023"][0]
assert Decimal(q["income_bcra"])==Decimal("51335922.727276686635448")
assert Decimal(q["expense_bcra"])==0
assert Decimal(q["income_otherfi"])==0
assert Decimal(q["expense_otherfi"])==0
with (base/"STRICT_Q4_FOUR_LEG_COVERAGE_V94.csv").open(encoding="utf-8") as f:
 c=list(csv.DictReader(f))[0]
assert Decimal(c["asset_numerator_million_ars"])==Decimal("57373426.142")
assert Decimal(c["asset_coverage_pct"])==Decimal("59.332775042193223725791893354893860940046911459229139540352334456615876642065374")
assert Decimal(c["increment_vs_v93_pp"])==Decimal("0.543890419808401742107701005139258980582427633965692595021563879978918422104486")
assert c["closed_network_gate"].startswith("NO")
with (base/"CURRENT_STATE_V94.csv").open(encoding="utf-8") as f:
 s=list(csv.DictReader(f))
assert any(r["entity"]=="Banco Provincia del Neuquén S.A." and r["strict_panel_status"]=="ELIGIBLE" for r in s)
assert any(r["entity"]=="Banco de Santiago del Estero S.A." and r["q4_four_leg_status"]=="N/D_STRICT" for r in s)
with (base/"RECOVERY_QUEUE_V94.csv").open(encoding="utf-8") as f:
 rq=list(csv.DictReader(f))
assert not any(r["entity"]=="Banco Provincia del Neuquén S.A." for r in rq)
assert any(r["entity"]=="Banco de Corrientes S.A." and r["status"]=="OPEN_NEXT_AUTONOMOUS" for r in rq)
assert any(r["entity"]=="Banco de Santiago del Estero S.A." and r["status"].startswith("HOLD") for r in rq)
# BPN raw annual one-to-one control
with (base/"BPN_BCRA_RAW_ACCOUNT_AUDIT_V94.csv").open(encoding="utf-8") as f:
 rr=list(csv.DictReader(f))
assert any(r["period"]=="202312" and r["account"]=="511108" and Decimal(r["credit_k"])==Decimal("129240317.000") for r in rr)
print("V94 QA PASS")
