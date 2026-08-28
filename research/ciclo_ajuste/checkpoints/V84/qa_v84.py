from pathlib import Path
import csv, math
p=Path(__file__).parent
with open(p/'STRICT_Q4_FOUR_LEG_COVERAGE_V84.csv',encoding='utf-8') as f:r=next(csv.DictReader(f))
assert math.isclose(float(r['asset_coverage_pct']), 27.36550851928007, abs_tol=1e-12)
assert float(r['increment_vs_v83_pp']) > 3.82
with open(p/'FOUR_LEG_PASS_PANEL_V84.csv',encoding='utf-8') as f: rows=list(csv.DictReader(f))
elig=[r for r in rows if r['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS']
assert len(elig)==6
assert any(r['entity']=='Banco Ciudad de Buenos Aires' and r['basis']=='INDIVIDUAL_ENTITY_REGULATORY' for r in elig)
with open(p/'BCRA_RAW_ACCOUNT_RECONCILIATION_V84.csv',encoding='utf-8') as f: rr=list(csv.DictReader(f))
assert all(r['verdict'].startswith('EXACT_MATCH') for r in rr)
print('QA_V84_PASS')
