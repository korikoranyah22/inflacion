from pathlib import Path
import csv, sys
P=Path(__file__).parent
required=[
'RAW_API_MANIFEST_V57.csv','MONTHLY_SUBACCOUNT_VALUES_2023_V57.csv','NOMINAL_RECONCILIATION_V57.csv','PP_TARGET_RECONCILIATION_V57.csv','ACCOUNT_MAPPING_NIIF_V57.csv','COUNTERPARTY_UPDATE_V57.csv','AUDITORIA_V57.md','VEREDICTO_V57.md','EVIDENCE_LEDGER_CICLO_AJUSTE_V57.csv','README_V57.md','MANIFEST_V57.json','BASE_V56.zip','PUBLICATION_REGIME_CORRECTION_V57.csv','POST2020_ACCUMULATED_RESULTS_V57.csv','IPC_RESTATEMENT_COEFFICIENTS_V57.csv']
for f in required:
    assert (P/f).exists(), f
with open(P/'MONTHLY_SUBACCOUNT_VALUES_2023_V57.csv',encoding='utf-8-sig') as f:
    rows=list(csv.DictReader(f))
assert len(rows)==92
assert all(r['value']=='' for r in rows)
assert all('NOT_PUBLISHED' in r['status'] for r in rows)
with open(P/'COUNTERPARTY_UPDATE_V57.csv',encoding='utf-8-sig') as f:
    c={r['bucket']:r for r in csv.DictReader(f)}
assert c['PASSES_DIRECT_BCRA']['pp']=='7.7' and c['PASSES_DIRECT_BCRA']['share_gross_positive_pct']=='26.83'
assert c['UNRESOLVED_COUNTERPARTY']['pp']=='21.0' and c['UNRESOLVED_COUNTERPARTY']['share_gross_positive_pct']=='73.17'
with open(P/'PP_TARGET_RECONCILIATION_V57.csv',encoding='utf-8-sig') as f:
    t={r['target']:r for r in csv.DictReader(f)}
assert t['Q4_2023_INTEREST_INCOME_ABNORMAL_GAP']['v57_status']=='PARTIAL_BROAD_FLOW_DIRECTION_ONLY'
for k in ['Q4_2023_SECURITIES_ABNORMAL_GAP','Q4_2023_CER_ABNORMAL_GAP','Q4_2023_FX_ABNORMAL_GAP']:
    assert t[k]['v57_status']=='NOT_RECONCILED'
assert not list(P.glob('*.html'))
print('PASS')
