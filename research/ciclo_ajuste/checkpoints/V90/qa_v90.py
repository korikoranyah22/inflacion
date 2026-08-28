from decimal import Decimal, getcontext
import pandas as pd
from pathlib import Path
getcontext().prec=80
base=Path(__file__).resolve().parent
coverage=pd.read_csv(base/'STRICT_Q4_FOUR_LEG_COVERAGE_V90.csv',dtype=str).iloc[0]
assert Decimal(coverage['asset_numerator_million_ars']) == Decimal('55232805.681')
assert Decimal(coverage['system_assets_million_ars']) == Decimal('96697695.5')
assert Decimal(coverage['asset_coverage_pct']) == Decimal('57.1190506613469397520440391467240292194967562593050627561233')
assert Decimal(coverage['increment_vs_v89_pp']) == Decimal('0.7578536853548903861933297055667681346139215903030491559129')
assert coverage['closed_network_gate'].startswith('NO_')
panel=pd.read_csv(base/'FOUR_LEG_PASS_PANEL_V90.csv',dtype=str)
elig=panel[panel['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS']
assert len(elig)==18, len(elig)
b=elig[elig['entity']=='Banco de Inversion y Comercio Exterior S.A.']
assert len(b)==1
r=b.iloc[0]
assert Decimal(r['income_bcra']) == Decimal('34882023.954531658032028')
assert Decimal(r['expense_bcra']) == Decimal('0E-15')
assert Decimal(r['income_otherfi']) == Decimal('-1.076792919412032')
assert Decimal(r['expense_otherfi']) == Decimal('44197.000000000000000')
state=pd.read_csv(base/'CURRENT_STATE_V90.csv',dtype=str)
br=state[state['entity']=='Banco de Inversion y Comercio Exterior S.A.']
assert len(br)==1 and br.iloc[0]['strict_panel_status']=='ELIGIBLE'
for e in ['Banco de la Nacion Argentina','Banco Santander Argentina SA','Banco Hipotecario S.A.','Banco de Santiago del Estero S.A.']:
    rr=state[state['entity']==e]
    assert len(rr)>=1 and not (rr['strict_panel_status']=='ELIGIBLE').any(), e
rq=pd.read_csv(base/'RECOVERY_QUEUE_V90.csv',dtype=str)
assert not rq['entity'].str.contains('BICE|Inversion y Comercio Exterior',case=False,regex=True).any()
print('QA_V90_PASS')
