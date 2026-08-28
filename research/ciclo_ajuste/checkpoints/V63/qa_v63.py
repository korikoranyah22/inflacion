from pathlib import Path
import csv
p=Path(__file__).parent
req=['BASE_V62.zip','ENTITY_COVERAGE_V63.csv','CONSOLIDATED_Q4_AQ_PANEL_V63.csv','INDIVIDUAL_Q4_AQ_PANEL_V63.csv','FOUR_LEG_PASS_PANEL_V63.csv','SYMMETRIC_INTERBANK_NETTING_TEST_V63.csv','HOUSEHOLD_PRODUCT_PANEL_V63.csv','HOUSEHOLD_SECTOR_MAPPING_AUDIT_V63.md','IEF_PASS_RECONCILIATION_V63.csv','COUNTERPARTY_UPDATE_V63.csv','AUDITORIA_V63.md','VEREDICTO_V63.md','EVIDENCE_LEDGER_CICLO_AJUSTE_V63.csv','README_V63.md','PROMPT_CODEX_V64_CLOSED_PASS_NETWORK_COVERAGE_AND_SECTOR_MAPPING.md']
assert all((p/x).exists() for x in req)
with open(p/'COUNTERPARTY_UPDATE_V63.csv',encoding='utf-8-sig') as f:m={r['claim']:r['v63'] for r in csv.DictReader(f)}
assert m['IEF_7_7PP_BCRA_SHARE']=='N/D'
assert m['HOUSEHOLD_SYSTEM_Q4_POINT_ESTIMATE']=='N/D'
assert m['SUBSET_INTERBANK_NETTING_AS_SYSTEM_TEST']=='REJECTED'
with open(p/'FOUR_LEG_PASS_PANEL_V63.csv',encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
c=next(r for r in rows if r['entity']=='Banco Ciudad de Buenos Aires')
assert float(c['income_bcra'])==0 and float(c['expense_bcra'])==0
assert float(c['income_otherfi'])>0 and float(c['expense_otherfi'])>0
v=(p/'VEREDICTO_V63.md').read_text()
assert 'DIRECT_HOUSEHOLD_TO_BANK_TRANSFER' in v and 'NOT_IDENTIFIED' in v
print('PASS')
