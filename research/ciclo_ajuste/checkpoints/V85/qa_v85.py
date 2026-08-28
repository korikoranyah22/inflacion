from pathlib import Path
import csv, math
p=Path(__file__).parent
with open(p/'STRICT_Q4_FOUR_LEG_COVERAGE_V85.csv',encoding='utf-8') as f:r=next(csv.DictReader(f))
assert math.isclose(float(r['asset_coverage_pct']), 36.334782973188844, abs_tol=1e-12)
assert math.isclose(float(r['asset_numerator_million_ars']), 35134897.8, abs_tol=1e-9)
with open(p/'FOUR_LEG_PASS_PANEL_V85.csv',encoding='utf-8') as f:rows=list(csv.DictReader(f))
elig=[x for x in rows if x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS']
assert len(elig)==7, len(elig)
g=[x for x in elig if x['entity']=='Banco de Galicia y Buenos Aires SAU']
assert len(g)==1 and float(g[0]['expense_bcra'])==0
with open(p/'BCRA_63_BANK_RAW_SWEEP_V85.csv',encoding='utf-8') as f:s=list(csv.DictReader(f))
assert len(s)==63, len(s)
assert all(x['strict_promotion_from_raw_sweep'].startswith('NO') for x in s)
with open(p/'RAW_TO_ANNEXQ_ENTITY_SPECIFIC_RECONCILIATION_V85.csv',encoding='utf-8') as f: rr=list(csv.DictReader(f))
assert any(x['entity']=='Santander' and x['verdict']=='COUNTEREXAMPLE_NOT_DIRECT_MAPPING' for x in rr)
print('QA_V85_PASS')
