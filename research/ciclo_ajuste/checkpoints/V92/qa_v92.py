from decimal import Decimal, getcontext
import pandas as pd
from pathlib import Path
getcontext().prec=80
base=Path(__file__).resolve().parent
coverage=pd.read_csv(base/'STRICT_Q4_FOUR_LEG_COVERAGE_V92.csv',dtype=str).iloc[0]
assert Decimal(coverage['asset_numerator_million_ars']) == Decimal('56348425.741')
assert Decimal(coverage['system_assets_million_ars']) == Decimal('96697695.5')
assert Decimal(coverage['asset_coverage_pct']) == Decimal('58.272770048589213793621379529153308519125980618638424532051024938851826101688225')
assert Decimal(coverage['increment_vs_v91_pp']) == Decimal('0.356713850538454662551911591316051580567398320262968417897818464556893188835095')
assert coverage['closed_network_gate'].startswith('NO_')
panel=pd.read_csv(base/'FOUR_LEG_PASS_PANEL_V92.csv',dtype=str)
elig=panel[panel['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS']
assert len(elig)==20, len(elig)
b=elig[elig['entity']=='Nuevo Banco del Chaco S.A.']
assert len(b)==1
r=b.iloc[0]
assert Decimal(r['income_bcra']) == Decimal('11135244.167859780236144')
assert Decimal(r['expense_bcra']) == Decimal('0')
assert Decimal(r['income_otherfi']) == Decimal('-0.122955442752296')
assert Decimal(r['expense_otherfi']) == Decimal('0')
state=pd.read_csv(base/'CURRENT_STATE_V92.csv',dtype=str)
br=state[state['entity']=='Nuevo Banco del Chaco S.A.']
assert len(br)==1 and br.iloc[0]['strict_panel_status']=='ELIGIBLE'
for e in ['Banco de la Nacion Argentina','Banco Santander Argentina SA','Banco Hipotecario S.A.','Banco de Santiago del Estero S.A.']:
    rr=state[state['entity']==e]
    assert len(rr)>=1 and not (rr['strict_panel_status']=='ELIGIBLE').any(), e
rq=pd.read_csv(base/'RECOVERY_QUEUE_V92.csv',dtype=str)
assert not (rq['entity']=='Nuevo Banco del Chaco S.A.').any()
assert rq['entity'].str.contains('Banco de La Pampa',case=False,regex=False).any()
print('QA_V92_PASS')
