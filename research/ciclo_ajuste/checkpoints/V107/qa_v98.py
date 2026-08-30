from pathlib import Path
import csv, json, hashlib
from decimal import Decimal, getcontext
getcontext().prec=80
base=Path(__file__).parent
repo=base.parents[3]

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()

with (base/'CMF_ISSUER_RAW_RECONCILIATION_V98.csv').open(encoding='utf-8') as h: r=list(csv.DictReader(h))
assert len(r)==2
assert Decimal(r[0]['issuer_pass_income_total_k'])==Decimal('10095166')==Decimal(r[0]['raw_income_k'])
assert Decimal(r[0]['issuer_pass_expense_total_k'])==Decimal('3830')==Decimal(r[0]['raw_expense_k'])
assert Decimal(r[1]['issuer_pass_income_total_k'])==Decimal('36619212')==Decimal(r[1]['raw_income_k'])
assert Decimal(r[1]['issuer_pass_expense_total_k'])==Decimal('7933')==Decimal(r[1]['raw_expense_k'])
for x in r: assert x['flow_counterparty_split_status']=='NOT_IDENTIFIED_FROM_FLOW_PRESENTATION' and x['strict_decision']=='HOLD_N_D_STRICT'
pa=repo/'research/ciclo_ajuste/inputs/issuer_retrieval/v98/binaries/CMF_Anual-2023-Balance_e_Informes_Separado.pdf'
pi=repo/'research/ciclo_ajuste/inputs/issuer_retrieval/v98/binaries/CMF_Trimestral-2023-03-Balance_e_Informes_Individual.pdf'
assert sha(pa)=='7ae34c445b53ba8edcee5d5b0efd0919f4dab77f587a12e0ab710b13b551aeef'
assert sha(pi)=='d5ab9998c7fbbc22e6ed599d033316e136406d9b8de28839da466d3bddd304a7'
with (base/'STRICT_Q4_FOUR_LEG_COVERAGE_V98.csv').open(encoding='utf-8') as h: c=list(csv.DictReader(h))[0]
assert Decimal(c['asset_numerator_million_ars'])==Decimal('57803557.512')
assert Decimal(c['asset_coverage_pct'])==Decimal('59.777595746322620480650441147276358824911189326119979767253088259998915899707248')
assert Decimal(c['increment_vs_v97_pp'])==0
with (base/'CURRENT_STATE_V98.csv').open(encoding='utf-8') as h: st=list(csv.DictReader(h))
assert any(x['entity']=='Banco CMF S.A.' and x['strict_panel_status']=='PENDING' and x['q4_four_leg_status'].startswith('N/D_STRICT') for x in st)
assert any(x['entity']=='HSBC Bank Argentina S.A.' and '3163537' in x['fy_status'] and '3121099' in x['nine_month_status'] for x in st)
assert any(x['entity']=='Banco de Corrientes S.A.' and 'EXACT_BINARY_ENDPOINT' in x['fy_status'] for x in st)
with (base/'FOUR_LEG_PASS_PANEL_V98.csv').open(encoding='utf-8') as h: panel=list(csv.DictReader(h))
# no accidental V98 CMF/HSBC/Corrientes promotion
for e in ['Banco CMF S.A.','HSBC Bank Argentina S.A.','Banco de Corrientes S.A.']:
 assert not any(x['entity']==e and x['system_panel_eligible_v72'].startswith('YES') for x in panel)
print('V98 analytical QA PASS')
