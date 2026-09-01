from pathlib import Path
import csv,hashlib,json
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==613
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V174.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==613 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V174.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V174' and co['master_catalog_entries']==613
assert co['recipient_note_to_local_file_pattern_proved'] and not co['note_3672_recipient_file_located'] and not co['archiveweb_zero_proves_note_absence']
assert co['commoncrawl_service_errors_v174']==2 and co['commoncrawl_pending_retry_queries']==40 and co['requests_submitted']==co['saf355_certifications_located']==co['executed_historical_bank_rows_confirmed']==0
assert len(rows('E0_SIGEN_2009_NOTE_SERIAL_DATE_ENVELOPE_V174.csv'))==6 and len(rows('E0_RECIPIENT_NOTE_TO_LOCAL_FILE_COMPARATORS_V174.csv'))==3
assert len(rows('E0_ARCHIVEWEB_EXACT_SEARCH_CONTROL_V174.csv'))==1 and len(rows('E0_SIGEN_NOTE_SEARCH_WINDOW_V174.csv'))==3
assert len(rows('V174_PDF_VISUAL_CONTROL.csv'))==3 and all(x['result'].startswith('PASS') for x in rows('V174_PDF_VISUAL_CONTROL.csv'))
keys=rows('E0_REQUEST_SEARCH_KEY_MATRIX_V174.csv'); assert {'SK174_20','SK174_21','SK174_22','SK174_23','SK174_24','SK174_25'}<={x['key_id'] for x in keys}
obj=rows('E0_V174_REQUEST_OBJECTS.csv'); assert {'RO174_20','RO174_21','RO174_22'}<={x['row_id'] for x in obj} and all(x['status']=='DRAFT_NOT_SENT' for x in obj) and obj==rows('E0_V174_REQUEST_OBJECTS_V174.csv')
for n in ('REQUEST_AGN_2018_REPLY_V174.md','REQUEST_BCRA_CRYL_SETTLEMENT_V174.md','REQUEST_BNA_FIRST_STAGE_BLOTTER_V174.md','REQUEST_CAJA_SETTLEMENT_HOLDINGS_V174.md','REQUEST_CNV_CUSTODY_RECORDS_V174.md','REQUEST_ECONOMIA_TESORO_SETTLEMENT_V174.md'):
 s=(H/n).read_text(encoding='utf-8-sig'); assert 'DRAFT_NOT_SENT' in s or 'BORRADOR_NO_ENVIADO' in s
panel=rows('FOUR_LEG_PASS_PANEL_V174.csv'); assert len(panel)==45 and sum(x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for x in panel)==34
assert len(rows('V174_SOURCE_BUNDLE.csv'))==8
m=json.loads((H/'MANIFEST_V174.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V174' and m['parent_checkpoint']=='V173' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V174 QA PASS · 613/613 · new=6 · RECIPIENT-FILE-PATTERN=PROVED · CC=2-errors/40-pending · panel=34 · requests=0 · SAF355=0/5 · execution=0/10')
