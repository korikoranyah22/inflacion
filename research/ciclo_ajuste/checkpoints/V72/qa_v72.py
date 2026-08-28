from pathlib import Path
import pandas as pd
p=Path(__file__).resolve().parent
required=[
'AUDITORIA_V72.md','BASE_V71.zip','BASIS_HARMONIZATION_V72.csv','BCRA_BANK_SYSTEM_COVERAGE_V72.csv',
'BCRA_ANNEX_Q_FREQUENCY_AUDIT_V72.csv','BCRA_ANNEX_Q_FREQUENCY_AUDIT_V72.md',
'BNA_9M_BINARY_RECOVERY_V72.csv','BNA_AGN_ATTACHMENT_AUDIT_V72.md','BNA_AGN_RECOVERED_BINARY_FINGERPRINTS_V72.csv','BNA_FY_AQ_CONTROL_V72.csv',
'CLOSED_NETWORK_COVERAGE_V72.csv','CLOSED_NETWORK_NETTING_TEST_V72.csv','COUNTERPARTY_UPDATE_V72.csv',
'CREDICOOP_FY_AQ_CONTROL_V72.csv','CREDICOOP_PRIMARY_INDEX_AUDIT_V72.csv','EVIDENCE_LEDGER_CICLO_AJUSTE_V72.csv',
'FOUR_LEG_PASS_PANEL_V72.csv','FUENTES_V72.md','HANDOVER_CODEX_CICLO_AJUSTE_V72_A_V73.md',
'HOUSEHOLD_PRODUCT_PANEL_V72.csv','HOUSEHOLD_SECTOR_MAPPING_V72.csv','IEF_PASS_RECONCILIATION_V72.csv',
'INDIVIDUAL_AQ_RETRIEVAL_V72.csv','PASS_COUNTERPARTY_BOUNDS_V72.csv','PUBLIC_BANK_AQ_EXTRACTION_V72.csv',
'PUBLIC_BANK_COVERAGE_PRIORITY_V72.csv','PUBLIC_BANK_SOURCE_RECOVERY_V72.csv','REGULATORY_ARCHIVE_RECOVERY_V72.csv',
'README_V72.md','VEREDICTO_V72.md','PROMPT_CODEX_V73_CREDICOOP_DYNAMIC_BINARY_AND_BNA_ALTERNATE_9M_COUNTERPARTY_DISCLOSURE.md',
'RECOVERED_AGN_ATTACHMENTS/2023-210-Resolucion.pdf','RECOVERED_AGN_ATTACHMENTS/2023-210-Informe SC 1.pdf','RECOVERED_AGN_ATTACHMENTS/2023-210-Informe CC 2.pdf'
]
for f in required: assert (p/f).exists(), f'missing {f}'
assert not (p/'BNA_Q4_AQ_BRIDGE_V72.csv').exists(), 'invalid BNA Q4 bridge must not exist'
assert not list(p.glob('*.html')), 'HTML forbidden'
assert not (p/'HANDOVER_CODEX_CICLO_AJUSTE_V72_A_V72.md').exists(), 'stale handover'
assert not (p/'qa_v71.py').exists(), 'stale qa'

cov=pd.read_csv(p/'BCRA_BANK_SYSTEM_COVERAGE_V72.csv')
strict=cov[cov.scope=='STRICT_Q4_FOUR_LEG_EXACT_TARGET_BASIS'].iloc[0]
assert abs(float(strict.asset_coverage_pct)-11.260967847987649)<1e-9

freq=pd.read_csv(p/'BCRA_ANNEX_Q_FREQUENCY_AUDIT_V72.csv')
q=freq[freq.annex.str.contains('Anexo Q',case=False)].iloc[0]
assert q.frequency=='Anual'

bna=pd.read_csv(p/'BNA_9M_BINARY_RECOVERY_V72.csv')
sc=bna[bna.source.str.contains('SC 1',case=False)].iloc[0]
assert 'RECOVERED' in sc.binary_recovery
assert sc.usable_for_q4_bridge=='NO'
assert 'ANNUAL' in sc.annex_q_status.upper()

fp=pd.read_csv(p/'BNA_AGN_RECOVERED_BINARY_FINGERPRINTS_V72.csv')
assert set(fp['file'])=={'2023-210-Resolucion.pdf','2023-210-Informe SC 1.pdf','2023-210-Informe CC 2.pdf'}
assert fp['sha256'].str.len().eq(64).all()

four=pd.read_csv(p/'FOUR_LEG_PASS_PANEL_V72.csv')
col='system_panel_eligible_v72'
assert col in four.columns
bad=four[(four.basis.astype(str).str.contains('CONSOLIDATED')) & four[col].astype(str).str.upper().eq('YES')]
assert len(bad)==0
eligible=four[four[col].astype(str).eq('YES_EXACT_Q4_TARGET_BASIS')]
assert set(eligible.entity)=={'Industrial and Commercial Bank of China (Argentina) S.A.U.','Banco de Valores S.A.','Banco Macro S.A.'}

ver=(p/'VEREDICTO_V72.md').read_text(encoding='utf-8')
for token in [
'BCRA_2023_ANNEX_Q_REPORTING_FREQUENCY\n= ANNUAL',
'MANDATORY_9M_ANNEX_Q_RETRIEVAL_GATE\n= REMOVED',
'CLOSED_PASS_NETWORK\n= NOT_ACHIEVED',
'SYSTEM_BCRA_NET_PASS_FLOW\n= N/D',
'IEF_7_7PP_BCRA_SHARE\n= N/D',
'DIRECT_HOUSEHOLD_TO_BANK_TRANSFER\n= NOT_IDENTIFIED',
'HTML_MODIFICATION\n= FORBIDDEN'
]: assert token in ver, token
print('QA PASS')
