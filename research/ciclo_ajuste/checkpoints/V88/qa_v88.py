from pathlib import Path
import csv
p=Path(__file__).parent

def rows(n):
    with open(p/n,encoding="utf-8-sig") as f:return list(csv.DictReader(f))

c=rows("STRICT_Q4_FOUR_LEG_COVERAGE_V88.csv")[0]
assert abs(float(c["asset_numerator_million_ars"])-51800348.982)<1e-6
assert abs(float(c["asset_coverage_pct"])-53.56937279027503)<1e-12
assert c["closed_network_gate"].startswith("NO")
panel=rows("FOUR_LEG_PASS_PANEL_V88.csv")
elig=[r for r in panel if r["system_panel_eligible_v72"]=="YES_EXACT_Q4_TARGET_BASIS"]
assert len(elig)==13, len(elig)
assert len([r for r in elig if r["entity"]=="Banco Comafi Sociedad Anonima"])==1
assert len([r for r in elig if r["entity"]=="Banco de la Provincia de Cordoba S.A."])==1
co=[r for r in elig if r["entity"]=="Banco Comafi Sociedad Anonima"][0]
ba=[r for r in elig if r["entity"]=="Banco de la Provincia de Cordoba S.A."][0]
assert abs(float(co["income_bcra"])-136510581.59993931)<1e-6
assert abs(float(co["expense_otherfi"])-654.1630439498469)<1e-6
assert abs(float(ba["income_bcra"])-53876602.36149075)<1e-6
assert abs(float(ba["expense_otherfi"])-25539.806152110756)<1e-6
cr=rows("BANCOR_ENTITY_SPECIFIC_CROSSWALK_V88.csv")
assert any(r["raw_account"]=="515034" and r["target"]=="EXCLUDE_FROM_PASS" for r in cr)
h=(p/"HIPOTECARIO_RAW_PRESENTATION_CONFLICT_V88.md").read_text(encoding="utf-8")
assert "158,630" in h and "DO NOT PROMOTE" in h
nu=(p/"ANNEX_Q_INTERIM_AVAILABILITY_NUANCE_V88.md").read_text(encoding="utf-8")
assert "annual required frequency" in nu and "interim Annex Q" in nu
req=(p/"USER_FILE_REQUESTS_V88.md").read_text(encoding="utf-8")
assert "d483d33a-5c86-4fbb-ab9c-6528bf43f572" in req
print("QA_V88_PASS")
