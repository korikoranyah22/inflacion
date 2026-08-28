from pathlib import Path
import pandas as pd, math, json, sys
p=Path(__file__).resolve().parent
errors=[]
req=['AUDITORIA_V67.md', 'BASE_V66.zip', 'BASIS_HARMONIZATION_V67.csv', 'BCRA_BANK_SYSTEM_COVERAGE_V67.csv', 'CLOSED_NETWORK_COVERAGE_V67.csv', 'CLOSED_NETWORK_NETTING_TEST_V67.csv', 'COUNTERPARTY_UPDATE_V67.csv', 'EVIDENCE_LEDGER_CICLO_AJUSTE_V67.csv', 'FOUR_LEG_PASS_PANEL_V67.csv', 'FUENTES_V67.md', 'HANDOVER_CODEX_CICLO_AJUSTE_V67_A_V68.md', 'HOUSEHOLD_PRODUCT_PANEL_V67.csv', 'HOUSEHOLD_SECTOR_MAPPING_V67.csv', 'IEF_PASS_RECONCILIATION_V67.csv', 'INDIVIDUAL_AQ_RETRIEVAL_V67.csv', 'MACRO_Q4_AQ_BRIDGE_V67.csv', 'PASS_COUNTERPARTY_BOUNDS_V67.csv', 'PROMPT_CODEX_V68_PRIMARY_BINARY_RECOVERY_AND_LARGE_BANK_COVERAGE.md', 'README_V67.md', 'VEREDICTO_V67.md']
for x in req:
    if not (p/x).exists(): errors.append('missing '+x)

b=pd.read_csv(p/'MACRO_Q4_AQ_BRIDGE_V67.csv')
q=b[b.period=='Q4-2023'].iloc[0]
checks={
'income_bcra':61675202.8273678,'expense_bcra':0.0,'income_otherfi':5729593.579547919,'expense_otherfi':2502560.2856956925,'net_otherfi':3227033.293852227}
for k,v in checks.items():
    if not math.isclose(float(q[k]),v,rel_tol=0,abs_tol=1e-5): errors.append(f'Macro {k} mismatch')

cov=pd.read_csv(p/'BCRA_BANK_SYSTEM_COVERAGE_V67.csv')
r=cov[cov.scope=='STRICT_Q4_FOUR_LEG_EXACT_TARGET_BASIS'].iloc[0]
if not math.isclose(float(r.asset_coverage_pct),11.260967847987649,abs_tol=1e-9): errors.append('coverage mismatch')
if 'Banco Macro' not in str(r.entities): errors.append('Macro missing exact coverage')

net=pd.read_csv(p/'CLOSED_NETWORK_NETTING_TEST_V67.csv')
r0=net[net.scope=='ICBC_PLUS_BANCO_VALORES_EXACT_V66_CONTROL'].iloc[0]
r1=net[net.scope=='ICBC_PLUS_BANCO_VALORES_PLUS_MACRO_EXACT'].iloc[0]
if not (float(r0.net_otherfi)<0<float(r1.net_otherfi)): errors.append('open-subset sign flip not preserved')
if str(net[net.scope=='SYSTEM'].iloc[0].can_test_system_cancellation)!='NOT_YET': errors.append('system gate relaxed')

cu=pd.read_csv(p/'COUNTERPARTY_UPDATE_V67.csv')
def val(claim): return str(cu[cu.claim==claim].iloc[0].v67)
if val('IEF_7_7PP_BCRA_SHARE')!='N/D': errors.append('IEF gate relaxed')
if val('HTML_MODIFICATION')!='FORBIDDEN': errors.append('HTML gate relaxed')
if any(x.suffix.lower() in ('.html','.htm') for x in p.iterdir()): errors.append('HTML present')

print('QA_PASS' if not errors else 'QA_FAIL')
for e in errors: print(e)
sys.exit(0 if not errors else 1)
