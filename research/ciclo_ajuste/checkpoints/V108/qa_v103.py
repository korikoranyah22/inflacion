from pathlib import Path
import csv, json
from decimal import Decimal
p=Path(__file__).parent
for f in ['CNV_EXACT_PRESENTATION_REVALIDATION_V103.csv','CNV_AIF_ATTACHMENT_ROUTE_DISCOVERY_V103.md','HIGH_PAYOFF_SOURCE_REVALIDATION_V103.md','RECOVERY_QUEUE_V103.csv','CURRENT_STATE_V103.csv']:
    assert (p/f).exists(), f
c=list(csv.DictReader(open(p/'STRICT_Q4_FOUR_LEG_COVERAGE_V103.csv',encoding='utf-8-sig')))[0]
assert c['asset_coverage_pct']=='59.7775957463226204806504411472763588249111893261199797672530882599989158997072479353967644'
t=list(csv.DictReader(open(p/'CNV_EXACT_PRESENTATION_REVALIDATION_V103.csv',encoding='utf-8-sig')))
assert len(t)==6
assert {x['presentation_id'] for x in t}=={'3122483','3165651','3121099','3163537','3119515','3171909'}
assert all('RECONFIRMED' in x['status'] for x in t)
q=list(csv.DictReader(open(p/'RECOVERY_QUEUE_V103.csv',encoding='utf-8-sig')))
for name in ['Banco Mariva S.A.','HSBC Bank Argentina S.A.','Banco BMA / ex Banco Itau Argentina S.A.']:
    x=next(r for r in q if r['entity']==name)
    assert 'ATTACHMENT_JSON_ROUTE' in x['status']
state=list(csv.DictReader(open(p/'CURRENT_STATE_V103.csv',encoding='utf-8-sig')))
r=next(x for x in state if x['entity']=='Banco Rioja S.A.U.')
assert 'MISMATCH' in r['q4_four_leg_status']
v=next(x for x in state if x['entity']=='Banco VOII S.A.')
assert 'SOURCE_HOLD' in v['q4_four_leg_status']
print('V103 QA PASS')
