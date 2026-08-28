from pathlib import Path
import pandas as pd
p=Path(__file__).resolve().parent
required=[
'AUDITORIA_V70.md','BASE_V69.zip','BASIS_HARMONIZATION_V70.csv','BCRA_BANK_SYSTEM_COVERAGE_V70.csv',
'BNA_9M_BINARY_RECOVERY_V70.csv','BNA_FY_AQ_CONTROL_V70.csv','CLOSED_NETWORK_COVERAGE_V70.csv',
'CLOSED_NETWORK_NETTING_TEST_V70.csv','COUNTERPARTY_UPDATE_V70.csv','EVIDENCE_LEDGER_CICLO_AJUSTE_V70.csv',
'FOUR_LEG_PASS_PANEL_V70.csv','FUENTES_V70.md','HANDOVER_CODEX_CICLO_AJUSTE_V70_A_V71.md',
'HOUSEHOLD_PRODUCT_PANEL_V70.csv','HOUSEHOLD_SECTOR_MAPPING_V70.csv','IEF_PASS_RECONCILIATION_V70.csv',
'INDIVIDUAL_AQ_RETRIEVAL_V70.csv','PASS_COUNTERPARTY_BOUNDS_V70.csv','PUBLIC_BANK_AQ_EXTRACTION_V70.csv',
'PUBLIC_BANK_COVERAGE_PRIORITY_V70.csv','PUBLIC_BANK_SOURCE_RECOVERY_V70.csv','README_V70.md',
'VEREDICTO_V70.md','PROMPT_CODEX_V71_REGULATORY_ARCHIVE_RECOVERY_AND_PUBLIC_BANK_9M_AQ.md'
]
for f in required: assert (p/f).exists(), f'missing {f}'
assert not (p/'BNA_Q4_AQ_BRIDGE_V70.csv').exists(), 'invalid Q4 bridge must not exist'
assert not list(p.glob('*.html')), 'HTML forbidden'

cov=pd.read_csv(p/'BCRA_BANK_SYSTEM_COVERAGE_V70.csv')
strict=cov[cov.scope=='STRICT_Q4_FOUR_LEG_EXACT_TARGET_BASIS'].iloc[0]
assert abs(float(strict.asset_coverage_pct)-11.260967847987649)<1e-9

bna=pd.read_csv(p/'BNA_9M_BINARY_RECOVERY_V70.csv')
issuer=bna[bna.source.str.contains('Balance Condensado',case=False)].iloc[0]
assert issuer.binary_recovery=='RECOVERED'
assert issuer.basis_target_compatibility=='NO_CONSOLIDATED_INCLUSIVE_CONTROL_ONLY'
assert issuer.annex_q_status=='ABSENT_ONE_PAGE_SUMMARY'
assert issuer.usable_for_q4_bridge=='NO'
agn=bna[bna.source.str.contains('AGN')].iloc[0]
assert '502' in agn.binary_recovery
assert agn.usable_for_q4_bridge=='NO'

four=pd.read_csv(p/'FOUR_LEG_PASS_PANEL_V70.csv')
col='system_panel_eligible_v70'
assert col in four.columns
bad=four[(four.basis.astype(str).str.contains('CONSOLIDATED')) & four[col].astype(str).str.upper().eq('YES')]
assert len(bad)==0
eligible=four[four[col].astype(str).eq('YES_EXACT_Q4_TARGET_BASIS')]
assert set(eligible.entity)=={'Industrial and Commercial Bank of China (Argentina) S.A.U.','Banco de Valores S.A.','Banco Macro S.A.'}

ver=(p/'VEREDICTO_V70.md').read_text(encoding='utf-8')
for token in [
'CLOSED_PASS_NETWORK\n= NOT_ACHIEVED',
'SYSTEM_BCRA_NET_PASS_FLOW\n= N/D',
'IEF_7_7PP_BCRA_SHARE\n= N/D',
'DIRECT_HOUSEHOLD_TO_BANK_TRANSFER\n= NOT_IDENTIFIED',
'HTML_MODIFICATION\n= FORBIDDEN'
]: assert token in ver, token
print('QA PASS')
