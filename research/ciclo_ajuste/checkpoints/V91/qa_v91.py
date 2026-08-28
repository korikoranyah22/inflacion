from decimal import Decimal, getcontext
import pandas as pd
from pathlib import Path
getcontext().prec=80
base=Path(__file__).resolve().parent
coverage=pd.read_csv(base/'STRICT_Q4_FOUR_LEG_COVERAGE_V91.csv',dtype=str).iloc[0]
assert Decimal(coverage['asset_numerator_million_ars']) == Decimal('56003491.668')
assert Decimal(coverage['system_assets_million_ars']) == Decimal('96697695.5')
assert Decimal(coverage['asset_coverage_pct']) == Decimal('57.916056198050759131069467937837256938558582298375456114153206474294932912853130')
assert Decimal(coverage['increment_vs_v90_pp']) == Decimal('0.797005536703819379025428791113227719061826039070393358029906474294932912853130')
assert coverage['closed_network_gate'].startswith('NO_')
panel=pd.read_csv(base/'FOUR_LEG_PASS_PANEL_V91.csv',dtype=str)
elig=panel[panel['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS']
assert len(elig)==19, len(elig)
b=elig[elig['entity']=='Banco Industrial S.A.']
assert len(b)==1
r=b.iloc[0]
assert Decimal(r['income_bcra']) == Decimal('152115463.880168364322132')
assert Decimal(r['expense_bcra']) == Decimal('0.000000000000000')
assert Decimal(r['income_otherfi']) == Decimal('13088.901470779662428')
assert Decimal(r['expense_otherfi']) == Decimal('1964.590567920517340')
state=pd.read_csv(base/'CURRENT_STATE_V91.csv',dtype=str)
br=state[state['entity']=='Banco Industrial S.A.']
assert len(br)==1 and br.iloc[0]['strict_panel_status']=='ELIGIBLE'
for e in ['Banco de la Nacion Argentina','Banco Santander Argentina SA','Banco Hipotecario S.A.','Banco de Santiago del Estero S.A.']:
    rr=state[state['entity']==e]
    assert len(rr)>=1 and not (rr['strict_panel_status']=='ELIGIBLE').any(), e
rq=pd.read_csv(base/'RECOVERY_QUEUE_V91.csv',dtype=str)
assert not (rq['entity']=='Banco Industrial S.A.').any()
assert rq['entity'].str.contains('Banco BMA',case=False,regex=False).any()
print('QA_V91_PASS')
