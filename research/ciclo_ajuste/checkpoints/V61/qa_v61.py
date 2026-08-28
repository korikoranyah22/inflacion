from pathlib import Path
import csv
p=Path(__file__).parent
req=['ENTITY_COVERAGE_V61.csv','ENTITY_Q4_AQ_SYSTEM_SAMPLE_V61.csv','PASS_COUNTERPARTY_SYSTEM_V61.csv','INTERBANK_PASS_NETTING_AUDIT_V61.md','HOUSEHOLD_PRODUCT_BOUND_V61.csv','SYSTEM_RECONCILIATION_V61.csv','COUNTERPARTY_UPDATE_V61.csv','AUDITORIA_V61.md','VEREDICTO_V61.md','EVIDENCE_LEDGER_CICLO_AJUSTE_V61.csv','README_V61.md','BASE_V60.zip']
assert all((p/x).exists() for x in req)
with open(p/'COUNTERPARTY_UPDATE_V61.csv',encoding='utf-8-sig') as f:m={r['claim']:r['v61'] for r in csv.DictReader(f)}
assert m['IEF_7_7PP_BCRA_SHARE']=='N/D'
assert m['DIRECT_HOUSEHOLD_TO_BANK_TRANSFER']=='NOT_IDENTIFIED'
with open(p/'ENTITY_COVERAGE_V61.csv',encoding='utf-8-sig') as f:r=list(csv.DictReader(f))
assert sum(x['q4_reconstructable']=='YES' for x in r)==3
print('PASS')
