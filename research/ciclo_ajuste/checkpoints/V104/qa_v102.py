from pathlib import Path
import csv
from decimal import Decimal
p=Path(__file__).parent
for f in ['VOII_Q4_FOUR_LEG_CANDIDATE_V102.csv','VOII_BCRA_RAW_REPO_ACCOUNT_AUDIT_V102.csv','V102_ENTITY_SPECIFIC_CROSSWALK_AUDIT.csv','BANCO_RIOJA_REPO_MISMATCH_AUDIT_V102.csv']:
    assert (p/f).exists(), f
c=list(csv.DictReader(open(p/'STRICT_Q4_FOUR_LEG_COVERAGE_V102.csv',encoding='utf-8-sig')))[0]
assert c['asset_coverage_pct']=='59.7775957463226204806504411472763588249111893261199797672530882599989158997072479353967644'
state=list(csv.DictReader(open(p/'CURRENT_STATE_V102.csv',encoding='utf-8-sig')))
v=next(x for x in state if x['entity']=='Banco VOII S.A.')
assert 'SOURCE_HOLD' in v['q4_four_leg_status']
r=next(x for x in state if x['entity']=='Banco Rioja S.A.U.')
assert 'MISMATCH' in r['q4_four_leg_status']
q=list(csv.DictReader(open(p/'VOII_Q4_FOUR_LEG_CANDIDATE_V102.csv',encoding='utf-8-sig')))[0]
assert Decimal(q['q4_income_otherfi'])==Decimal('1449217.007028504769916')
assert Decimal(q['q4_expense_otherfi'])==Decimal('-2.848019436825984')
assert Decimal(q['q4_expense_otherfi']) < 0
x=list(csv.DictReader(open(p/'V102_ENTITY_SPECIFIC_CROSSWALK_AUDIT.csv',encoding='utf-8-sig')))
assert all(Decimal(y['difference_k'])==0 for y in x)
rj=list(csv.DictReader(open(p/'BANCO_RIOJA_REPO_MISMATCH_AUDIT_V102.csv',encoding='utf-8-sig')))
assert Decimal(rj[0]['difference_issuer_minus_raw_k'])==Decimal('158789')
print('V102 QA PASS')
