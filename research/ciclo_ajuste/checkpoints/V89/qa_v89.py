from decimal import Decimal, getcontext
import pandas as pd
from pathlib import Path
getcontext().prec=60
base=Path(__file__).resolve().parent
coverage=pd.read_csv(base/'STRICT_Q4_FOUR_LEG_COVERAGE_V89.csv',dtype=str).iloc[0]
assert Decimal(coverage['asset_numerator_million_ars']) == Decimal('54499978.632')
assert Decimal(coverage['system_assets_million_ars']) == Decimal('96697695.5')
assert Decimal(coverage['asset_coverage_pct']) == Decimal('56.3611969759920493658507094411572610848828346690020136002104')
assert Decimal(coverage['increment_vs_v88_pp']) == Decimal('2.7918241857170215602501095799123775395453969221010136002104')
assert coverage['closed_network_gate'].startswith('NO_')
panel=pd.read_csv(base/'FOUR_LEG_PASS_PANEL_V89.csv',dtype=str)
elig=panel[panel['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS']
assert len(elig)==17, len(elig)
for e in ['Nuevo Banco de Santa Fe Sociedad Anonima','Nuevo Banco de Entre Ríos S.A.','Banco de San Juan S.A.','Banco de Santa Cruz S.A.']:
    assert (elig['entity']==e).sum()==1, e
# ensure held entities are not accidentally exact
state=pd.read_csv(base/'CURRENT_STATE_V89.csv',dtype=str)
for e in ['Banco de la Nacion Argentina','Banco Santander Argentina SA','Banco Hipotecario S.A.','Banco de Santiago del Estero S.A.']:
    r=state[state['entity']==e]
    assert len(r)>=1 and not (r['strict_panel_status']=='ELIGIBLE').any(), e
print('QA_V89_PASS')
