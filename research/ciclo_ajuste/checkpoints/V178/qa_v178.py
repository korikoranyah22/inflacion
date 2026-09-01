from pathlib import Path
import csv,hashlib,json
from decimal import Decimal
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==643
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V178.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==643 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V178.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V178' and co['master_catalog_entries']==643
assert co['bid1192_account_series_2011_2016_preserved'] and co['bid1192_fondyf_legal_chain_proved'] and not co['mypesii_executed_contract_full_body_located']
assert not co['bid1192_note3672_sisio_crosswalk_proved'] and not co['bid1192_damage_or_appropriation_proved']
assert co['requests_submitted']==co['saf355_certifications_located']==co['executed_historical_bank_rows_confirmed']==0
assert len(rows('E0_BID1192_ACCOUNT_TABLE_TOTALS_2011_2016_V178.csv'))==6
t=rows('E0_BID1192_2015_2016_TOTAL_CROSSWALK_V178.csv'); assert len(t)==9 and Decimal(t[8]['amount_ars'])==Decimal('1579470.00')
assert len(rows('E0_BID1192_MP0191_CLOSURE_ATTRIBUTION_CHAIN_V178.csv'))==6
assert len(rows('E0_BID1192_FIDEICOMISO_FONDYF_LEGAL_CHAIN_V178.csv'))==10
assert len(rows('E0_BID1192_BNA_ADMINISTRATION_RESPONSIBILITY_MATRIX_V178.csv'))==8
assert len(rows('E0_BID1192_PUBLIC_DOCUMENT_BOUNDARY_V178.csv'))==8
assert len(rows('V178_PDF_VISUAL_CONTROL.csv'))==6 and all(x['result'].startswith('PASS') for x in rows('V178_PDF_VISUAL_CONTROL.csv'))
assert len(rows('V178_HTML_CONTENT_CONTROL.csv'))==7 and all(x['result'].startswith('PASS') for x in rows('V178_HTML_CONTENT_CONTROL.csv'))
assert len(rows('V178_SOURCE_BUNDLE.csv'))==13
keys=rows('E0_REQUEST_SEARCH_KEY_MATRIX_V178.csv'); assert {f'SK178_{x}' for x in range(50,56)}<={x['key_id'] for x in keys}
obj=rows('E0_V178_REQUEST_OBJECTS.csv'); assert {f'RO178_{x}' for x in range(48,54)}<={x['row_id'] for x in obj} and all(x['status']=='DRAFT_NOT_SENT' for x in obj) and obj==rows('E0_V178_REQUEST_OBJECTS_V178.csv')
panel=rows('FOUR_LEG_PASS_PANEL_V178.csv'); assert len(panel)==45 and sum(x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for x in panel)==34
m=json.loads((H/'MANIFEST_V178.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V178' and m['parent_checkpoint']=='V177' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V178 QA PASS · 643/643 · new=13 · FONDYF-chain=PROVED · contract-body=OPEN · panel=34 · requests=0')
