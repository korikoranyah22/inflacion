from pathlib import Path
import csv,hashlib,json
from decimal import Decimal
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==627
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V176.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==627 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V176.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V176' and co['master_catalog_entries']==627
assert co['sisio_composite_key_schema_empirically_proved'] and co['sisio_longitudinal_status_history_empirically_proved'] and co['note_3672_signatory_role_located']
assert not co['note_3672_target_sisio_rows_located'] and not co['note_3672_personal_signatory_located'] and not co['note_3672_specific_monetary_attribution_proved']
assert co['commoncrawl_exact_prefix_queries_v176']==0 and co['commoncrawl_pending_retry_queries']==40 and co['requests_submitted']==co['saf355_certifications_located']==co['executed_historical_bank_rows_confirmed']==0
assert len(rows('E0_SISIO_COMPOSITE_KEY_LONGITUDINAL_EXAMPLE_V176.csv'))==4
assert [x['status'] for x in rows('E0_SISIO_COMPOSITE_KEY_LONGITUDINAL_EXAMPLE_V176.csv')]==['En Trámite','En Trámite','En Trámite','Regularizada']
assert len(rows('E0_SISIO_UEPEX_STATUS_SEMANTICS_V176.csv'))==5
assert len(rows('E0_SISIO_OUTCOME_CLASSIFICATION_RULES_V176.csv'))==6
assert len(rows('E0_NOTE_3672_SISIO_TARGET_EXPORT_SCHEMA_V176.csv'))==6
for x in rows('E0_SISIO_UEPEX_AMOUNT_DISCONTINUITY_EXAMPLE_V176.csv'):
 assert Decimal(x['prior_final_ars'])-Decimal(x['next_initial_ars'])==Decimal(x['reported_difference_ars'])
assert len(rows('V176_PDF_VISUAL_CONTROL.csv'))==7 and all(x['result'].startswith('PASS') for x in rows('V176_PDF_VISUAL_CONTROL.csv'))
keys=rows('E0_REQUEST_SEARCH_KEY_MATRIX_V176.csv'); assert {'SK176_40','SK176_41','SK176_42','SK176_43','SK176_44'}<={x['key_id'] for x in keys}
obj=rows('E0_V176_REQUEST_OBJECTS.csv'); assert {'RO176_40','RO176_41','RO176_42','RO176_43'}<={x['row_id'] for x in obj} and all(x['status']=='DRAFT_NOT_SENT' for x in obj) and obj==rows('E0_V176_REQUEST_OBJECTS_V176.csv')
for n in ('REQUEST_AGN_2018_REPLY_V176.md','REQUEST_BCRA_CRYL_SETTLEMENT_V176.md','REQUEST_BNA_FIRST_STAGE_BLOTTER_V176.md','REQUEST_CAJA_SETTLEMENT_HOLDINGS_V176.md','REQUEST_CNV_CUSTODY_RECORDS_V176.md','REQUEST_ECONOMIA_TESORO_SETTLEMENT_V176.md'):
 s=(H/n).read_text(encoding='utf-8-sig'); assert 'DRAFT_NOT_SENT' in s or 'BORRADOR_NO_ENVIADO' in s
panel=rows('FOUR_LEG_PASS_PANEL_V176.csv'); assert len(panel)==45 and sum(x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for x in panel)==34
assert len(rows('V176_SOURCE_BUNDLE.csv'))==4
m=json.loads((H/'MANIFEST_V176.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V176' and m['parent_checkpoint']=='V175' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V176 QA PASS · 627/627 · new=4 · SISIO-HISTORY=PROVED · TARGET-ROWS=OPEN · panel=34 · requests=0')
