from pathlib import Path
import csv, json, hashlib, sys
R=Path(__file__).parent
errors=[]
req=['SERIES_VALUE_BYTES_MANIFEST_V56.csv','ACCOUNT_EQUIVALENCE_NIIF_V56.csv','OFFICIAL_CATALOG_SLICE_V56.csv','MONTHLY_SUBACCOUNT_VALUES_2023_V56.csv','TARGET_RECONCILIATION_V56.csv','COUNTERPARTY_UPDATE_V56.csv','AUDITORIA_V56.md','VEREDICTO_V56.md','EVIDENCE_LEDGER_CICLO_AJUSTE_V56.csv','FUENTES_V56.md','README_V56.md','MANIFEST_V56.json','fetch_bcra_v4_values.py','PROMPT_CODEX_V57_API_VALUE_EXTRACTION_AND_RECONCILIATION.md','BASE_V55.zip','raw_cache/Series_estadisticas.xlsx','raw_cache/es_series.txt']
for x in req:
    if not (R/x).exists(): errors.append('missing '+x)
with open(R/'ACCOUNT_EQUIVALENCE_NIIF_V56.csv',encoding='utf-8-sig') as f: eq=list(csv.DictReader(f))
if len(eq)!=23: errors.append(f'equivalence rows {len(eq)} !=23')
if any(r['published_series_id_continuity']!='SUPPORTED_SAME_ID_IN_MODERN_OFFICIAL_CATALOG' for r in eq): errors.append('series continuity failed')
if any(r['modern_periodicity']!='Mensual' for r in eq): errors.append('not all monthly')
if any(r['modern_txt_location']!='DIN1' for r in eq): errors.append('not all DIN1')
with open(R/'MONTHLY_SUBACCOUNT_VALUES_2023_V56.csv',encoding='utf-8-sig') as f: vals=list(csv.DictReader(f))
if len(vals)!=92: errors.append(f'value placeholder rows {len(vals)} !=92')
if any(r['value_status']!='NOT_MATERIALIZED' for r in vals): errors.append('invented value status')
with open(R/'COUNTERPARTY_UPDATE_V56.csv',encoding='utf-8-sig') as f: cp=list(csv.DictReader(f))
if cp[0]['pp']!='7.7' or cp[0]['share_gross_positive_pct']!='26.83': errors.append('frozen BCRA floor changed')
sha=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
if sha(R/'raw_cache'/'Series_estadisticas.xlsx')!='3d9a98fa443b833ebb34c814863c1259a89d4ab8d59570578ee030c00288b5d0': errors.append('modern catalog hash mismatch')
if sha(R/'raw_cache'/'es_series.txt')!='46089e8501001529f6a089e9981fb72f1e5f46e8817504ddc76f18996f28dd2b': errors.append('legacy catalog hash mismatch')
print('PASS' if not errors else 'FAIL')
for e in errors: print('-',e)
sys.exit(1 if errors else 0)
