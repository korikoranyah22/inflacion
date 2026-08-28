from pathlib import Path
import csv, math
p=Path(__file__).parent

def rows(n):
    with open(p/n,encoding="utf-8-sig") as f:return list(csv.DictReader(f))

c=rows("STRICT_Q4_FOUR_LEG_COVERAGE_V86.csv")[0]
assert abs(float(c["asset_numerator_million_ars"])-41194838.394)<1e-6
assert abs(float(c["asset_coverage_pct"])-42.60167543910082)<1e-12
assert c["closed_network_gate"].startswith("NO")
panel=rows("FOUR_LEG_PASS_PANEL_V86.csv")
elig=[r for r in panel if r["system_panel_eligible_v72"]=="YES_EXACT_Q4_TARGET_BASIS"]
assert len(elig)==8, len(elig)
b=[r for r in elig if r["entity"]=="Banco BBVA Argentina S.A."]
assert len(b)==1
b=b[0]
assert abs(float(b["income_bcra"])-160559825.76797262)<1e-6
assert abs(float(b["income_otherfi"])-(-8.459195626598368))<1e-9
assert abs(float(b["expense_otherfi"])-1797.165473556341)<1e-9
prom=rows("BBVA_Q4_FOUR_LEG_PROMOTION_V86.csv")
sep=[r for r in prom if r["period"]=="9M-2023"][0]
assert float(sep["income_bcra"])+float(sep["income_otherfi"])==148514057.0
assert float(sep["expense_otherfi"])==15128.0
text=(p/"ANNEX_Q_FREQUENCY_CORRECTION_V86.md").read_text(encoding="utf-8")
assert "ANUAL" in text and "Annex Q 9M" in text
rec=(p/"RECOVERY_QUEUE_V86.csv").read_text(encoding="utf-8")
assert "interest-income / interest-expense" in rec
assert "mass" not in c["v86_change"].lower()
print("QA_V86_PASS")
