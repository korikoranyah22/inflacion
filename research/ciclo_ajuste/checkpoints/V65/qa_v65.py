from pathlib import Path
import csv, math, sys, zipfile
ROOT=Path(__file__).parent

def rows(name):
    with (ROOT/name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def one(rs, key, val):
    m=[r for r in rs if r.get(key)==val]
    assert len(m)==1, (key,val,len(m))
    return m[0]

basis=rows("BASIS_HARMONIZATION_V65.csv")
r=one(basis,"item","SYSTEM_PANEL_BASIS")
assert r["v65_state"]=="INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING"

cov=rows("BCRA_BANK_SYSTEM_COVERAGE_V65.csv")
r=one(cov,"scope","BANK_SYSTEM_DENOMINATOR")
assert abs(float(r["bank_assets_denominator_million_ars"])-96697695.5)<1e-6
r=one(cov,"scope","STRICT_Q4_FOUR_LEG_EXACT_TARGET_BASIS")
assert abs(float(r["asset_coverage_pct"])-4.101041787495339)<1e-9
assert r["can_weight_pass_flows"].startswith("NO")
r=one(cov,"scope","Q4_INDIVIDUAL_COUNTERPARTY_DETAIL")
assert abs(float(r["asset_coverage_pct"])-13.070316241404118)<1e-9

panel=rows("FOUR_LEG_PASS_PANEL_V65.csv")
elig=[r for r in panel if r["system_panel_eligible_v65"].startswith("YES_EXACT_Q4") ]
assert len(elig)==1 and "Commercial Bank of China" in elig[0]["entity"]
assert one(panel,"entity","Banco Ciudad de Buenos Aires")["system_panel_eligible_v65"]=="NO"

bp=rows("BAPRO_FY_AQ_CONTROL_V65.csv")[0]
assert float(bp["income_bcra"])==1040489497.0
assert float(bp["expense_otherfi"])==2428.0
assert bp["q4_eligible"].startswith("NO")
cr=rows("CREDICOOP_FY_AQ_CONTROL_V65.csv")[0]
assert float(cr["income_bcra"])==180887922.0
assert float(cr["expense_otherfi"])==0.0
assert cr["q4_eligible"].startswith("NO")

net=rows("CLOSED_NETWORK_NETTING_TEST_V65.csv")
r=one(net,"scope","ICBC_PLUS_GALICIA")
assert abs(float(r["net_otherfi"])-3826393.097964)<1e-4
assert r["can_test_system_cancellation"]=="NO"
assert one(net,"scope","SYSTEM")["can_test_system_cancellation"]=="NOT_YET"

ief=rows("IEF_PASS_RECONCILIATION_V65.csv")
assert one(ief,"target","BCRA share of +7.7 pp")["status"]=="N/D"

hh=rows("HOUSEHOLD_SECTOR_MAPPING_V65.csv")
assert all(r["annex_q_accrued_interest_flow_bridge"]=="NOT_IDENTIFIED" for r in hh)

upd=rows("COUNTERPARTY_UPDATE_V65.csv")
assert one(upd,"claim","DIRECT_HOUSEHOLD_TO_BANK_TRANSFER")["v65"]=="NOT_IDENTIFIED"
assert one(upd,"claim","HTML_MODIFICATION")["v65"]=="FORBIDDEN"

assert not list(ROOT.glob("*.html")), "V65 must not contain HTML"
print("PASS")
