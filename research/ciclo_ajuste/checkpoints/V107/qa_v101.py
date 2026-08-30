from pathlib import Path
import csv, json
from decimal import Decimal
p=Path(__file__).parent
for f in ['BACS_Q4_FOUR_LEG_CANDIDATE_V101.csv','BMR_Q4_FOUR_LEG_CANDIDATE_V101.csv','BTF_Q4_FOUR_LEG_CANDIDATE_V101.csv','BMR_BTF_EXHAUSTIVE_INTEREST_RECONCILIATION_V101.csv','V101_ENTITY_SPECIFIC_CROSSWALK_AUDIT.csv']:
    assert (p/f).exists(), f
c=list(csv.DictReader(open(p/'STRICT_Q4_FOUR_LEG_COVERAGE_V101.csv',encoding='utf-8-sig')))[0]
assert c['asset_coverage_pct']=='59.7775957463226204806504411472763588249111893261199797672530882599989158997072479353967644'
assert c['increment_vs_v100_pp']=='0'
state=list(csv.DictReader(open(p/'CURRENT_STATE_V101.csv',encoding='utf-8-sig')))
for e in ['BACS Banco de Credito y Securitizacion S.A.','Banco Municipal de Rosario','Banco Provincia de Tierra del Fuego']:
    r=next(x for x in state if x['entity']==e)
    assert 'SOURCE_HOLD' in r['q4_four_leg_status']
for fn,expected in [('BACS_Q4_FOUR_LEG_CANDIDATE_V101.csv','26576523.202785377437612'),('BMR_Q4_FOUR_LEG_CANDIDATE_V101.csv','3433170.427567358059400'),('BTF_Q4_FOUR_LEG_CANDIDATE_V101.csv','3910389.706408089269876')]:
    r=list(csv.DictReader(open(p/fn,encoding='utf-8-sig')))[0]; assert r['q4_income_bcra']==expected
recon=list(csv.DictReader(open(p/'BMR_BTF_EXHAUSTIVE_INTEREST_RECONCILIATION_V101.csv',encoding='utf-8-sig')))
assert all(Decimal(r['difference'])==0 for r in recon)
print('V101 QA PASS')
