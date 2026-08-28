from pathlib import Path
import csv
p=Path(__file__).parent

def rows(n):
    with open(p/n,encoding="utf-8-sig") as f:return list(csv.DictReader(f))

c=rows("STRICT_Q4_FOUR_LEG_COVERAGE_V87.csv")[0]
assert abs(float(c["asset_numerator_million_ars"])-48590481.063)<1e-6
assert abs(float(c["asset_coverage_pct"])-50.24988528604593)<1e-12
assert c["closed_network_gate"].startswith("NO")

panel=rows("FOUR_LEG_PASS_PANEL_V87.csv")
elig=[r for r in panel if r["system_panel_eligible_v72"]=="YES_EXACT_Q4_TARGET_BASIS"]
assert len(elig)==11, len(elig)

def one(entity):
    x=[r for r in elig if r["entity"]==entity]
    assert len(x)==1,(entity,len(x))
    return x[0]

pat=one("Banco Patagonia S.A.")
assert abs(float(pat["income_otherfi"])-143548485.37997314)<1e-6
assert abs(float(pat["expense_otherfi"])-502688.2983643543)<1e-6
assert float(pat["income_bcra"])==0

citi=one("CITIBANK N.A.")
assert abs(float(citi["income_bcra"])-271540204.28621645)<1e-6
assert abs(float(citi["income_otherfi"])-2444912.8783895182)<1e-6
assert float(citi["expense_bcra"])==0 and float(citi["expense_otherfi"])==0

sup=one("Banco Supervielle S.A.")
assert abs(float(sup["income_bcra"])-86491188.97791664)<1e-6
assert abs(float(sup["income_otherfi"])-222212.68844635402)<1e-6
assert abs(float(sup["expense_otherfi"])-591120.9074580243)<1e-6

oldbound=[r for r in panel if r["entity"]=="Banco Supervielle S.A." and "BOUND" in r["quality"]]
assert not oldbound

cross=rows("V87_ENTITY_SPECIFIC_CROSSWALK_AUDIT.csv")
assert [r for r in cross if r["entity"]=="Banco Santander Argentina SA"][0]["verdict"]=="FAIL_STRICT_SPLIT"
assert [r for r in cross if r["entity"]=="Banco de la Nacion Argentina"][0]["verdict"]=="FAIL_STRICT_SPLIT"

print("QA_V87_PASS")
