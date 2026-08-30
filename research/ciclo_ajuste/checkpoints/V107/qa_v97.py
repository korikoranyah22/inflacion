from pathlib import Path
import csv, json
from decimal import Decimal, getcontext
getcontext().prec=80
base=Path(__file__).parent
repo=base.parents[3]
f=Decimal("1.532908152197492")
with (base/"COLUMBIA_BCRA_RAW_ACCOUNT_AUDIT_V97.csv").open(encoding="utf-8") as h: rr=list(csv.DictReader(h))
def s(period,accounts): return sum(Decimal(r["absolute_result_k"]) for r in rr if r["period"]==period and r["account"] in accounts)
assert s("202309",{"511027","511108","511055"})==Decimal("2070947")
assert s("202312",{"511027","511108","511055"})==Decimal("8366812")
assert s("202309",{"521022"})==Decimal("512498")
assert s("202312",{"521022"})==Decimal("882825")
assert any(r["period"]=="202312" and r["account"]=="511055" and Decimal(r["absolute_result_k"])==Decimal("1395") for r in rr)
with (base/"COLUMBIA_Q4_FOUR_LEG_CANDIDATE_V97.csv").open(encoding="utf-8") as h: q=list(csv.DictReader(h))
q4=[r for r in q if r["period"]=="Q4-2023"][0]
assert Decimal(q4["income_bcra"])==Decimal("5192240.460931060535076")
assert Decimal(q4["expense_otherfi"])==Decimal("97212.637815089744984")
assert Decimal(q4["income_otherfi"])==0 and Decimal(q4["expense_bcra"])==0
with (base/"STRICT_Q4_FOUR_LEG_COVERAGE_V97.csv").open(encoding="utf-8") as h: c=list(csv.DictReader(h))[0]
assert Decimal(c["asset_numerator_million_ars"])==Decimal("57803557.512")
assert Decimal(c["asset_coverage_pct"])==Decimal("59.777595746322620480650441147276358824911189326119979767253088259998915899707248")
assert Decimal(c["increment_vs_v96_pp"])==0
with (base/"FOUR_LEG_PASS_PANEL_V97.csv").open(encoding="utf-8") as h: panel=list(csv.DictReader(h))
assert not any(r["entity"]=="Banco Columbia S.A." and r["system_panel_eligible_v72"].startswith("YES") for r in panel)
with (base/"CURRENT_STATE_V97.csv").open(encoding="utf-8") as h: st=list(csv.DictReader(h))
assert any(r["entity"]=="Banco Columbia S.A." and r["strict_panel_status"]=="PENDING" and "SOURCE_HOLD" in r["q4_four_leg_status"] for r in st)
assert any(r["entity"]=="Banco Mariva S.A." and r["q4_four_leg_status"]=="N/D_STRICT" for r in st)
sc=json.load(open(repo/"research/ciclo_ajuste/source_audit/CURRENT_SOURCE_COMPLETENESS_V97.json",encoding="utf-8"))
assert sc["master_catalog_entries"]==193 and sc["remaining_physical_gaps"]==2 and sc["binary_required_source_complete"] is False
with open(repo/"data/fuentes/FUENTES.csv",encoding="utf-8-sig",newline="") as h: src={r["id"]:r for r in csv.DictReader(h)}
for k in ["columbia_eeff_9m2023_sep_pending","columbia_eeff_fy2023_aq_pending"]:
    assert k in src and not src[k]["archivo_local"] and not src[k]["sha256"]
print("V97 QA PASS")
