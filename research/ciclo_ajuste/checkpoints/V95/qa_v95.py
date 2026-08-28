from pathlib import Path
import csv
from decimal import Decimal, getcontext
getcontext().prec=80
base=Path(__file__).parent
with (base/"BANCO_FORMOSA_Q4_FOUR_LEG_PROMOTION_V95.csv").open(encoding="utf-8") as f:
 rows=list(csv.DictReader(f))
q=[r for r in rows if r["period"]=="Q4-2023"][0]
assert Decimal(q["income_bcra"])==Decimal("8771309.525142089603936")
assert Decimal(q["expense_bcra"])==Decimal("5985.000000000000000")
assert Decimal(q["income_otherfi"])==Decimal("1.270423879561360")
assert Decimal(q["expense_otherfi"])==Decimal("-1.706017614623548")
with (base/"STRICT_Q4_FOUR_LEG_COVERAGE_V95.csv").open(encoding="utf-8") as f:
 c=list(csv.DictReader(f))[0]
assert Decimal(c["asset_numerator_million_ars"])==Decimal("57641276.689")
assert Decimal(c["asset_coverage_pct"])==Decimal("59.609772901981929858917889103158616639421360357031466173875881044135121089829902")
assert Decimal(c["increment_vs_v94_pp"])==Decimal("0.276997859788706133125995748264755699374448897802326633523546587519244447764528")
assert c["closed_network_gate"].startswith("NO")
with (base/"CURRENT_STATE_V95.csv").open(encoding="utf-8") as f:
 s=list(csv.DictReader(f))
assert any(r["entity"]=="Banco de Formosa S.A." and r["strict_panel_status"]=="ELIGIBLE" for r in s)
assert any(r["entity"]=="Banco de Corrientes S.A." and r["q4_four_leg_status"]=="N/D_STRICT" for r in s)
with (base/"BANCO_FORMOSA_BCRA_RAW_ACCOUNT_AUDIT_V95.csv").open(encoding="utf-8") as f:
 rr=list(csv.DictReader(f))
assert any(r["period"]=="202312" and r["account"]=="525042" and Decimal(r["absolute_result_k"])==Decimal("5985") for r in rr)
assert Decimal("120514")+Decimal("5985")==Decimal("126499")
assert Decimal("13949461")+Decimal("2178")==Decimal("13951639")
with (base/"RECOVERY_QUEUE_V95.csv").open(encoding="utf-8") as f:
 rq=list(csv.DictReader(f))
assert not any(r["entity"]=="Banco de Formosa S.A." for r in rq)
assert any(r["entity"]=="Banco CMF S.A." and r["status"]=="OPEN_NEXT_AUTONOMOUS" for r in rq)
print("V95 QA PASS")
