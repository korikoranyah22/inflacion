from pathlib import Path
import csv
p=Path(__file__).parent
req=['RAW_ENTITY_2023_MANIFEST_V60.csv','AQ_SYSTEM_AGGREGATE_2023_V60.csv','AQ_TO_IEF_ANNUAL_BRIDGE_V60.csv','HOUSEHOLD_LIKE_INTEREST_ANNUAL_V60.csv','SECURITIES_PUBLIC_ISSUER_GATE_V60.csv','COUNTERPARTY_UPDATE_V60.csv','AQ_FREQUENCY_CORRECTION_V60.csv','ENTITY_Q4_AQ_BRIDGE_V60.csv','PASS_COUNTERPARTY_FALSIFIER_V60.csv','IPC_REEXPRESSION_V60.csv','AUDITORIA_V60.md','VEREDICTO_V60.md','EVIDENCE_LEDGER_CICLO_AJUSTE_V60.csv','README_V60.md','BASE_V59.zip']
assert all((p/x).exists() for x in req)
with open(p/'COUNTERPARTY_UPDATE_V60.csv',encoding='utf-8-sig') as f:
 m={r['claim']:r['v60_status'] for r in csv.DictReader(f)}
assert m['7_7PP_AS_STRICT_BCRA_FLOOR']=='REVOKED'
assert m['HOUSEHOLD_SYSTEM_Q4_POINT_ESTIMATE']=='N/D'
with open(p/'AQ_SYSTEM_AGGREGATE_2023_V60.csv',encoding='utf-8-sig') as f:
 rows=list(csv.DictReader(f))
assert [r for r in rows if r['scope']=='SYSTEM'][0]['status']=='NOT_RUN'
v=(p/'VEREDICTO_V60.md').read_text()
assert 'DIRECT_HOUSEHOLD_TO_BANK_TRANSFER' in v and 'NOT_IDENTIFIED' in v
print('PASS')
