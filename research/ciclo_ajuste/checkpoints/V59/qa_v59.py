from pathlib import Path
import csv, json, sys
p=Path(__file__).parent
required=[
'POSITIVE_FINANCIAL_INCOME_FORMULA_V59.csv','POST_NIIF_SUBACCOUNT_MAP_V59.csv','COMMON_DENOMINATOR_RECONCILIATION_V59.csv',
'INTEREST_ACCRUED_SECTOR_FLOW_V59.csv','SECURITIES_RESULT_ISSUER_FLOW_V59.csv','FX_CER_PASSES_FLOW_V59.csv',
'COUNTERPARTY_UPDATE_V59.csv','AUDITORIA_V59.md','VEREDICTO_V59.md','EVIDENCE_LEDGER_CICLO_AJUSTE_V59.csv','README_V59.md','MANIFEST_V59.json','BASE_V58.zip','PROMPT_CODEX_V60_ANNUAL_AQ_SYSTEM_RECONCILIATION.md','FUENTES_V59.md']
missing=[x for x in required if not (p/x).exists()]
assert not missing, f'MISSING {missing}'
# MFIR formula rounding gate
with open(p/'POSITIVE_FINANCIAL_INCOME_FORMULA_V59.csv',encoding='utf-8-sig') as f: rows=list(csv.DictReader(f))
s={r['component_id']:r for r in rows}
assert abs(float(s['component_sum']['q3_pct_a_an'])-14.3)<1e-9
assert abs(float(s['component_sum']['q4_pct_a_an'])-30.7)<1e-9
# Counterparty frozen
with open(p/'COUNTERPARTY_UPDATE_V59.csv',encoding='utf-8-sig') as f: c=list(csv.DictReader(f))
d={r['bucket']:r for r in c}
assert abs(float(d['PASSES_DIRECT_BCRA']['pp'])-7.7)<1e-9
assert abs(float(d['UNRESOLVED_COUNTERPARTY']['pp'])-21.0)<1e-9
assert d['DIRECT_HOUSEHOLD_POINT_ESTIMATE']['v59_status'].startswith('N/D')
# Forbidden false precision
text=' '.join((p/x).read_text(encoding='utf-8',errors='ignore') for x in ['AUDITORIA_V59.md','VEREDICTO_V59.md','README_V59.md'])
assert 'HOUSEHOLD_SYSTEM_Q4_POINT_ESTIMATE = N/D' in text
assert 'DIRECT_HOUSEHOLD_TO_BANK_TRANSFER' in text and 'NOT_IDENTIFIED' in text
print('PASS')
