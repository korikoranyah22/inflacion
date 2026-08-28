from pathlib import Path
import pandas as pd
p=Path(__file__).resolve().parent
required=[
'AUDITORIA_V71.md','BASE_V70.zip','BASIS_HARMONIZATION_V71.csv','BCRA_BANK_SYSTEM_COVERAGE_V71.csv',
'BNA_9M_BINARY_RECOVERY_V71.csv','BNA_AGN_ATTACHMENT_AUDIT_V71.md','BNA_FY_AQ_CONTROL_V71.csv',
'CLOSED_NETWORK_COVERAGE_V71.csv','CLOSED_NETWORK_NETTING_TEST_V71.csv','COUNTERPARTY_UPDATE_V71.csv',
'CREDICOOP_FY_AQ_CONTROL_V71.csv','CREDICOOP_PRIMARY_INDEX_AUDIT_V71.csv','EVIDENCE_LEDGER_CICLO_AJUSTE_V71.csv',
'FOUR_LEG_PASS_PANEL_V71.csv','FUENTES_V71.md','HANDOVER_CODEX_CICLO_AJUSTE_V71_A_V72.md',
'HOUSEHOLD_PRODUCT_PANEL_V71.csv','HOUSEHOLD_SECTOR_MAPPING_V71.csv','IEF_PASS_RECONCILIATION_V71.csv',
'INDIVIDUAL_AQ_RETRIEVAL_V71.csv','PASS_COUNTERPARTY_BOUNDS_V71.csv','PUBLIC_BANK_AQ_EXTRACTION_V71.csv',
'PUBLIC_BANK_COVERAGE_PRIORITY_V71.csv','PUBLIC_BANK_SOURCE_RECOVERY_V71.csv','REGULATORY_ARCHIVE_RECOVERY_V71.csv',
'README_V71.md','VEREDICTO_V71.md','PROMPT_CODEX_V72_DYNAMIC_ISSUER_ENDPOINT_RECOVERY_AND_BNA_REGULATORY_STATEMENT_SEARCH.md'
]
for f in required: assert (p/f).exists(), f'missing {f}'
assert not (p/'BNA_Q4_AQ_BRIDGE_V71.csv').exists(), 'invalid Q4 bridge must not exist'
assert not list(p.glob('*.html')), 'HTML forbidden'

cov=pd.read_csv(p/'BCRA_BANK_SYSTEM_COVERAGE_V71.csv')
strict=cov[cov.scope=='STRICT_Q4_FOUR_LEG_EXACT_TARGET_BASIS'].iloc[0]
assert abs(float(strict.asset_coverage_pct)-11.260967847987649)<1e-9

bna=pd.read_csv(p/'BNA_9M_BINARY_RECOVERY_V71.csv')
sc=bna[bna.source.str.contains('SC 1',case=False)].iloc[0]
assert '502' in sc.binary_recovery
assert sc.usable_for_q4_bridge=='NO'
landing=bna[bna.source.str.contains('landing page',case=False)].iloc[0]
assert landing.annex_q_status=='FULL_STATEMENT_PAYLOAD_NOT_ESTABLISHED'

cred=pd.read_csv(p/'CREDICOOP_PRIMARY_INDEX_AUDIT_V71.csv')
row=cred[cred.period=='30/09/2023'].iloc[0]
assert row.index_status=='DATE_LINK_LISTED'
assert row.binary_status=='DYNAMIC_LINK_ID_NOT_EXPOSED_TO_CURRENT_CRAWLER'
assert row.numeric_use=='NO'

four=pd.read_csv(p/'FOUR_LEG_PASS_PANEL_V71.csv')
col='system_panel_eligible_v71'
assert col in four.columns
bad=four[(four.basis.astype(str).str.contains('CONSOLIDATED')) & four[col].astype(str).str.upper().eq('YES')]
assert len(bad)==0
eligible=four[four[col].astype(str).eq('YES_EXACT_Q4_TARGET_BASIS')]
assert set(eligible.entity)=={'Industrial and Commercial Bank of China (Argentina) S.A.U.','Banco de Valores S.A.','Banco Macro S.A.'}

ver=(p/'VEREDICTO_V71.md').read_text(encoding='utf-8')
for token in [
'CLOSED_PASS_NETWORK\n= NOT_ACHIEVED',
'SYSTEM_BCRA_NET_PASS_FLOW\n= N/D',
'IEF_7_7PP_BCRA_SHARE\n= N/D',
'DIRECT_HOUSEHOLD_TO_BANK_TRANSFER\n= NOT_IDENTIFIED',
'HTML_MODIFICATION\n= FORBIDDEN'
]: assert token in ver, token
print('QA PASS')
