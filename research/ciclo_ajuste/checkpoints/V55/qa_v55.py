from pathlib import Path
import csv,json,hashlib,sys
p=Path(__file__).resolve().parent
req=['RAW_BYTES_MANIFEST_V55.csv','SUBACCOUNT_DICTIONARY_V55.csv','SECURITIES_RECONCILIATION_V55.csv','INTEREST_SECTOR_RECONCILIATION_V55.csv','CER_GROSS_RECONCILIATION_V55.csv','FX_MODE_RECONCILIATION_V55.csv','COUNTERPARTY_AXIS_V55.csv','ACCOUNTING_MODE_AXIS_V55.csv','AUDITORIA_RECONCILIACION_V55.md','VEREDICTO_RECONCILIACION_V55.md','EVIDENCE_LEDGER_CICLO_AJUSTE_V55.csv','README_V55.md','MANIFEST_V55.json','BASE_V54.zip','raw_cache/es_series.txt']
missing=[x for x in req if not (p/x).exists()]
assert not missing, missing
m=json.loads((p/'MANIFEST_V55.json').read_text(encoding='utf-8'))
raw=(p/'raw_cache/es_series.txt').read_bytes()
assert hashlib.sha256(raw).hexdigest()==m['schema_cache']['sha256']
rows=list(csv.DictReader((p/'COUNTERPARTY_AXIS_V55.csv').open(encoding='utf-8-sig')))
passrow=next(r for r in rows if r['q4_bucket']=='Primas por pases')
assert abs(float(passrow['gap_pp'])-7.7)<1e-9
assert passrow['status']=='STRICTLY_IDENTIFIED'
assert '26.83%' in (p/'VEREDICTO_RECONCILIACION_V55.md').read_text(encoding='utf-8')
print('PASS V55')
