from pathlib import Path
import csv, math, zipfile
ROOT=Path(__file__).parent

def rows(name):
    with (ROOT/name).open(encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def one(rs,key,val):
    m=[r for r in rs if r.get(key)==val]; assert len(m)==1,(key,val,len(m)); return m[0]

def f(x): return float(x)

basis=rows('BASIS_HARMONIZATION_V66.csv')
assert one(basis,'item','SYSTEM_PANEL_BASIS')['v66_state']=='INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING'

bv=rows('BANCO_VALORES_Q4_AQ_BRIDGE_V66.csv')
assert abs(f(one(bv,'metric','income_bcra')['q4_dec2023_thousand_ars'])-132269429.624235)<1e-3
assert abs(f(one(bv,'metric','income_otherfi')['q4_dec2023_thousand_ars'])-47920.656341)<1e-3
assert abs(f(one(bv,'metric','expense_otherfi')['q4_dec2023_thousand_ars'])-204552.353464)<1e-3
assert abs(f(one(bv,'metric','net_otherfi')['q4_dec2023_thousand_ars'])+156631.697124)<1e-3

sup=rows('SUPERVIELLE_Q4_PASS_BOUND_V66.csv')
assert abs(f(one(sup,'metric','total_pass_income')['lower_q4_thousand_ars'])-86713401.666363)<1e-3
assert abs(f(one(sup,'metric','total_pass_expense')['lower_q4_thousand_ars'])-591120.907458)<1e-3
assert f(one(sup,'metric','income_otherfi')['lower_q4_thousand_ars'])==0
assert abs(f(one(sup,'metric','income_otherfi')['upper_q4_thousand_ars'])-3285840)<1e-6
assert one(sup,'metric','income_bcra')['quality']=='BOUND'

panel=rows('FOUR_LEG_PASS_PANEL_V66.csv')
elig=[r for r in panel if r['system_panel_eligible_v66'].startswith('YES_EXACT_Q4')]
assert len(elig)==2
assert any('Commercial Bank of China' in r['entity'] for r in elig)
assert any(r['entity']=='Banco de Valores S.A.' for r in elig)
assert one(panel,'entity','Banco Supervielle S.A.')['system_panel_eligible_v66']=='NO_BOUND_NOT_EXACT'

cov=rows('BCRA_BANK_SYSTEM_COVERAGE_V66.csv')
r=one(cov,'scope','STRICT_Q4_FOUR_LEG_EXACT_TARGET_BASIS')
assert abs(f(r['asset_coverage_pct'])-5.209599850288)<1e-9
assert r['can_weight_pass_flows'].startswith('NO')
r=one(cov,'scope','Q4_INDIVIDUAL_COUNTERPARTY_DETAIL_POINT')
assert abs(f(r['asset_coverage_pct'])-14.178874304197)<1e-9

net=rows('CLOSED_NETWORK_NETTING_TEST_V66.csv')
r=one(net,'scope','ICBC_PLUS_BANCO_VALORES_EXACT')
assert abs(f(r['net_otherfi'])+1058668.831317)<1e-3
assert r['can_test_system_cancellation']=='NO'
r=one(net,'scope','ICBC_PLUS_BANCO_VALORES_PLUS_GALICIA')
assert abs(f(r['net_otherfi'])-3669761.400841)<1e-3
assert r['can_test_system_cancellation']=='NO'
assert one(net,'scope','SYSTEM')['can_test_system_cancellation']=='NOT_YET'

ief=rows('IEF_PASS_RECONCILIATION_V66.csv')
assert one(ief,'target','BCRA share of +7.7 pp')['status']=='N/D'

hh=rows('HOUSEHOLD_SECTOR_MAPPING_V66.csv')
assert all(r['annex_q_accrued_interest_flow_bridge']=='NOT_IDENTIFIED' for r in hh)

upd=rows('COUNTERPARTY_UPDATE_V66.csv')
assert one(upd,'claim','SYSTEM_INTERBANK_PASS_CANCELLATION')['v66']=='NOT_IDENTIFIED_COVERAGE_TOO_LOW'
assert one(upd,'claim','DIRECT_HOUSEHOLD_TO_BANK_TRANSFER')['v66']=='NOT_IDENTIFIED'
assert one(upd,'claim','HTML_MODIFICATION')['v66']=='FORBIDDEN'

bp=rows('BAPRO_FY_AQ_CONTROL_V66.csv')[0]; assert bp['q4_eligible'].startswith('NO')
cr=rows('CREDICOOP_FY_AQ_CONTROL_V66.csv')[0]; assert cr['q4_eligible'].startswith('NO')

assert not list(ROOT.glob('*.html'))
print('PASS')
