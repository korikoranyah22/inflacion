from pathlib import Path
import csv,hashlib,json
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==623
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V175.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==623 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V175.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V175' and co['master_catalog_entries']==623
assert co['sigen_2009_archive_digital_and_reordering_capability_proved'] and co['sisio_contemporary_status_workflow_proved'] and co['cgn_correction_mechanism_2009_2013_proved']
assert not co['note_3672_specific_causal_attribution_proved'] and not co['note_3672_specific_monetary_attribution_proved'] and not co['note_3672_signatory_located']
assert co['commoncrawl_exact_prefix_queries_v175']==0 and co['commoncrawl_pending_retry_queries']==40 and co['requests_submitted']==co['saf355_certifications_located']==co['executed_historical_bank_rows_confirmed']==0
assert len(rows('E0_NOTE_3672_DIRECTIVE_TO_OUTCOME_ATTRIBUTION_GATE_V175.csv'))==6
assert len(rows('E0_CGN_POST_3672_FOLLOWUP_SEARCH_V175.csv'))==4 and all(x['exact_3672_hits']==x['exact_0120_09_hits']==x['exact_sisio_hits']=='0' for x in rows('E0_CGN_POST_3672_FOLLOWUP_SEARCH_V175.csv'))
assert len(rows('E0_SIGEN_2009_NOTE_NUMBERING_AND_REMIT_EVIDENCE_V175.csv'))==8
assert len(rows('E0_SIGEN_2009_ARCHIVE_AND_SISIO_CAPABILITY_V175.csv'))==4
assert len(rows('E0_NOTE_3672_SIGNATORY_AUTHORITY_WINDOW_V175.csv'))==3
assert len(rows('E0_NOTE_3672_ATTRIBUTION_PROOF_REQUIREMENTS_V175.csv'))==5
assert len(rows('V175_PDF_VISUAL_CONTROL.csv'))==3 and all(x['result'].startswith('PASS') for x in rows('V175_PDF_VISUAL_CONTROL.csv'))
keys=rows('E0_REQUEST_SEARCH_KEY_MATRIX_V175.csv'); assert {'SK175_30','SK175_31','SK175_32','SK175_33','SK175_34'}<={x['key_id'] for x in keys}
obj=rows('E0_V175_REQUEST_OBJECTS.csv'); assert {'RO175_30','RO175_31','RO175_32','RO175_33','RO175_34'}<={x['row_id'] for x in obj} and all(x['status']=='DRAFT_NOT_SENT' for x in obj) and obj==rows('E0_V175_REQUEST_OBJECTS_V175.csv')
for n in ('REQUEST_AGN_2018_REPLY_V175.md','REQUEST_BCRA_CRYL_SETTLEMENT_V175.md','REQUEST_BNA_FIRST_STAGE_BLOTTER_V175.md','REQUEST_CAJA_SETTLEMENT_HOLDINGS_V175.md','REQUEST_CNV_CUSTODY_RECORDS_V175.md','REQUEST_ECONOMIA_TESORO_SETTLEMENT_V175.md'):
 s=(H/n).read_text(encoding='utf-8-sig'); assert 'DRAFT_NOT_SENT' in s or 'BORRADOR_NO_ENVIADO' in s
panel=rows('FOUR_LEG_PASS_PANEL_V175.csv'); assert len(panel)==45 and sum(x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for x in panel)==34
assert len(rows('V175_SOURCE_BUNDLE.csv'))==10
m=json.loads((H/'MANIFEST_V175.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V175' and m['parent_checkpoint']=='V174' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V175 QA PASS · 623/623 · new=10 · WORKFLOW=PROVED · ATTRIBUTION=OPEN · panel=34 · requests=0')
