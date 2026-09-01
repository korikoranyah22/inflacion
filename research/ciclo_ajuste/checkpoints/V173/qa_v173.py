from pathlib import Path
import csv,hashlib,json
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==607
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V173.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==607 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V173.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V173' and co['master_catalog_entries']==607
assert co['sigen_resolution_41_2007_body_located'] and co['sigen_resolution_41_2007_annexes_located'] and co['sigen_cidd_not_code_located'] and not co['note_3672_archive_digital_record_located']
assert co['commoncrawl_service_errors_v173']==2 and co['commoncrawl_pending_retry_queries']==40 and co['requests_submitted']==co['saf355_certifications_located']==co['executed_historical_bank_rows_confirmed']==0
assert len(rows('E0_SIGEN_CIDD_FIELD_DICTIONARY_V173.csv'))==12 and len(rows('E0_SIGEN_SPD_FORM_SCHEMA_V173.csv'))==9 and len(rows('E0_SIGEN_DIGITALIZATION_LIFECYCLE_V173.csv'))==7
assert len(rows('E0_SIGEN_ARCHIVEWEB_UNIVERSE_AUDIT_V173.csv'))==4 and len(rows('E0_SIGEN_LEGACY_TO_GDE_DIGITAL_NOTES_CROSSWALK_V173.csv'))==3
assert len(rows('V173_PDF_VISUAL_CONTROL.csv'))==2 and all(x['result'].startswith('PASS') for x in rows('V173_PDF_VISUAL_CONTROL.csv'))
cc=rows('E0_COMMONCRAWL_HEALTH_CONTROL_V173.csv'); assert len(cc)==2 and all(x['classification']=='SERVICE_ERROR' for x in cc)
keys=rows('E0_REQUEST_SEARCH_KEY_MATRIX_V173.csv'); assert {'SK173_20','SK173_21','SK173_22','SK173_23','SK173_24','SK173_25'}<={x['key_id'] for x in keys}
obj=rows('E0_V173_REQUEST_OBJECTS.csv'); assert {'RO173_20','RO173_21','RO173_22','RO173_23'}<={x['row_id'] for x in obj} and all(x['status']=='DRAFT_NOT_SENT' for x in obj) and obj==rows('E0_V173_REQUEST_OBJECTS_V173.csv')
for n in ('REQUEST_AGN_2018_REPLY_V173.md','REQUEST_BCRA_CRYL_SETTLEMENT_V173.md','REQUEST_BNA_FIRST_STAGE_BLOTTER_V173.md','REQUEST_CAJA_SETTLEMENT_HOLDINGS_V173.md','REQUEST_CNV_CUSTODY_RECORDS_V173.md','REQUEST_ECONOMIA_TESORO_SETTLEMENT_V173.md'):
 s=(H/n).read_text(encoding='utf-8-sig'); assert 'DRAFT_NOT_SENT' in s or 'BORRADOR_NO_ENVIADO' in s
panel=rows('FOUR_LEG_PASS_PANEL_V173.csv'); assert len(panel)==45 and sum(x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for x in panel)==34
assert len(rows('V173_SOURCE_BUNDLE.csv'))==9
m=json.loads((H/'MANIFEST_V173.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V173' and m['parent_checkpoint']=='V172' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V173 QA PASS · 607/607 · new=5 · RES41+CIDD+SPD=LOCATED · CC=2-errors/40-pending · panel=34 · requests=0 · SAF355=0/5 · execution=0/10')
