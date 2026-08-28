from pathlib import Path
import pandas as pd, math, sys
p=Path(__file__).resolve().parent
errors=[]
req=['AUDITORIA_V68.md', 'BANCO_VALORES_Q4_AQ_BRIDGE_V68.csv', 'BAPRO_FY_AQ_CONTROL_V68.csv', 'BASE_V67.zip', 'BASIS_HARMONIZATION_V68.csv', 'BCRA_BANK_SYSTEM_COVERAGE_V68.csv', 'CLOSED_NETWORK_COVERAGE_V68.csv', 'CLOSED_NETWORK_NETTING_TEST_V68.csv', 'COUNTERPARTY_UPDATE_V68.csv', 'CREDICOOP_FY_AQ_CONTROL_V68.csv', 'EVIDENCE_LEDGER_CICLO_AJUSTE_V68.csv', 'FOUR_LEG_PASS_PANEL_V68.csv', 'FUENTES_V68.md', 'HANDOVER_CODEX_CICLO_AJUSTE_V68_A_V69.md', 'HOUSEHOLD_PRODUCT_PANEL_V68.csv', 'HOUSEHOLD_SECTOR_MAPPING_V68.csv', 'IEF_PASS_RECONCILIATION_V68.csv', 'INDIVIDUAL_AQ_RETRIEVAL_V68.csv', 'MACRO_Q4_AQ_BRIDGE_V68.csv', 'MANIFEST_V68.json', 'PASS_COUNTERPARTY_BOUNDS_V68.csv', 'PROMPT_CODEX_V69_ALTERNATE_INTERIM_AQ_SOURCE_AND_PUBLIC_BANK_SCALEUP.md', 'QA_RESULT_V68.txt', 'README_V68.md', 'SANTANDER_FY_AQ_CONTROL_V68.csv', 'SANTANDER_INTERIM_ANNEX_AUDIT_V68.md', 'SANTANDER_PRIMARY_RECOVERY_V68.csv', 'SUPERVIELLE_Q4_PASS_BOUND_V68.csv', 'VEREDICTO_V68.md', 'qa_v68.py']
# Required core files explicit
core=['AUDITORIA_V68.md','BASE_V67.zip','BCRA_BANK_SYSTEM_COVERAGE_V68.csv','CLOSED_NETWORK_COVERAGE_V68.csv','CLOSED_NETWORK_NETTING_TEST_V68.csv','COUNTERPARTY_UPDATE_V68.csv','EVIDENCE_LEDGER_CICLO_AJUSTE_V68.csv','FOUR_LEG_PASS_PANEL_V68.csv','FUENTES_V68.md','HANDOVER_CODEX_CICLO_AJUSTE_V68_A_V69.md','IEF_PASS_RECONCILIATION_V68.csv','INDIVIDUAL_AQ_RETRIEVAL_V68.csv','PASS_COUNTERPARTY_BOUNDS_V68.csv','SANTANDER_FY_AQ_CONTROL_V68.csv','SANTANDER_PRIMARY_RECOVERY_V68.csv','SANTANDER_INTERIM_ANNEX_AUDIT_V68.md','PROMPT_CODEX_V69_ALTERNATE_INTERIM_AQ_SOURCE_AND_PUBLIC_BANK_SCALEUP.md','README_V68.md','VEREDICTO_V68.md']
for x in core:
    if not (p/x).exists(): errors.append('missing '+x)

s=pd.read_csv(p/'SANTANDER_PRIMARY_RECOVERY_V68.csv')
q=s[(s.stage=='Q4_BRIDGE') & (s.metric=='pass_interest_income_total')].iloc[0]
if not math.isclose(float(q.value),200412599.13436595,abs_tol=1e-5): errors.append('Santander Q4 total mismatch')
b=s[(s.stage=='Q4_BOUND') & (s.metric=='BCRA_pass_income_share')].iloc[0]
lo=float(str(b.value).split('_to_')[0])
if not math.isclose(lo,99.98854862413884,abs_tol=1e-9): errors.append('Santander BCRA bound missing')

cov=pd.read_csv(p/'BCRA_BANK_SYSTEM_COVERAGE_V68.csv')
r=cov[cov.scope=='STRICT_Q4_FOUR_LEG_EXACT_TARGET_BASIS'].iloc[0]
if not math.isclose(float(r.asset_coverage_pct),11.260967847987647,abs_tol=1e-9): errors.append('strict coverage changed unexpectedly')
r2=cov[cov.scope=='Q4_INDIVIDUAL_PASS_INCOME_BOUND_FOOTPRINT'].iloc[0]
if not math.isclose(float(r2.asset_coverage_pct),31.146101925459014,abs_tol=1e-9): errors.append('income-bound footprint mismatch')

ret=pd.read_csv(p/'INDIVIDUAL_AQ_RETRIEVAL_V68.csv')
sr=ret[ret.entity=='Banco Santander Argentina SA'].iloc[0]
if 'ANNEX_Q_NOT_PRESENT' not in str(sr.nine_month_status): errors.append('Santander disclosure gap not frozen')
if 'PARSER' in str(sr.fy_status): errors.append('Santander parser block not resolved')

net=pd.read_csv(p/'CLOSED_NETWORK_NETTING_TEST_V68.csv')
r0=net[net.scope=='ICBC_PLUS_BANCO_VALORES_EXACT_V66_CONTROL'].iloc[0]
r1=net[net.scope=='ICBC_PLUS_BANCO_VALORES_PLUS_MACRO_EXACT'].iloc[0]
if not (float(r0.net_otherfi)<0<float(r1.net_otherfi)): errors.append('sign-instability diagnostic lost')
if str(net[net.scope=='SYSTEM'].iloc[0].can_test_system_cancellation)!='NOT_YET': errors.append('system gate relaxed')

cu=pd.read_csv(p/'COUNTERPARTY_UPDATE_V68.csv')
def val(claim): return str(cu[cu.claim==claim].iloc[0].v68)
if val('IEF_7_7PP_BCRA_SHARE')!='N/D': errors.append('IEF gate relaxed')
if val('HTML_MODIFICATION')!='FORBIDDEN': errors.append('HTML gate relaxed')
if any(x.suffix.lower() in ('.html','.htm') for x in p.iterdir()): errors.append('HTML present')

# Prevent Santander income bound from being counted as exact four-leg
fl=pd.read_csv(p/'FOUR_LEG_PASS_PANEL_V68.csv')
ss=fl[(fl.entity=='Banco Santander Argentina SA') & (fl.basis=='SEPARATED_INDIVIDUAL')]
if any(ss['system_panel_eligible_v68'].astype(str).str.contains('YES_EXACT_Q4')): errors.append('Santander incorrectly promoted to exact Q4')

print('QA_PASS' if not errors else 'QA_FAIL')
for e in errors: print(e)
sys.exit(0 if not errors else 1)
