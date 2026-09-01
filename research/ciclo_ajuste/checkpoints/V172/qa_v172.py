from pathlib import Path
import csv, hashlib, json
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / 'research/ciclo_ajuste'
AUDIT = CYCLE / 'source_audit'
COVERAGE = '63.4406041403540997520463142785031521252747951992299547614348265414453439585848248058817492708499966268585997481191265825'
NEW_IDS = {'e0_sigen_memory_2007_computerized_mesa_and_digital_archive_v172','e0_cgn_circular_17_2005_note_subject_and_prior_reference_v172','e0_cgn_disposition_32_2009_hybrid_mesa_submission_v172'}
def rows(name):
    return list(csv.DictReader((HERE/name).open(encoding='utf-8-sig', newline='')))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
catalog = list(csv.DictReader((REPO/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig', newline='')))
assert len(catalog) == len({r['id'] for r in catalog}) == 602
new = [r for r in catalog if r['id'] in NEW_IDS]
assert len(new) == 3
for r in catalog:
    p = REPO/r['archivo_local'].lstrip('/')
    assert p.is_file() and sha(p) == r['sha256'].lower()
audit = list(csv.DictReader((AUDIT/'MASTER_LOCAL_HASH_VALIDATION_V172.csv').open(encoding='utf-8-sig', newline='')))
assert len(audit) == 602 and all(r['exists']=='True' and r['hash_ok']=='True' for r in audit)
assert (AUDIT/'SOURCE_PRESERVATION_MISSING_V172.csv').read_text(encoding='utf-8-sig').count('\n') == 1
complete = json.loads((AUDIT/'CURRENT_SOURCE_COMPLETENESS_V172.json').read_text(encoding='utf-8-sig'))
assert complete['checkpoint']=='V172' and complete['master_catalog_entries']==complete['physical_local_copies']==complete['physical_local_hash_ok']==602
assert complete['commoncrawl_exact_prefix_queries_v172']==complete['commoncrawl_valid_no_capture_v172']==106
assert complete['commoncrawl_service_errors_v172']==complete['commoncrawl_capture_rows_v172']==0
assert complete['sigen_computerized_mesa_capability_located'] is True and complete['sigen_resolution_41_2007_body_located'] is False
assert complete['comdoc_operational_by_2008_some_circuits'] is True and complete['comdoc_2010_creation_claim_corrected'] is True
assert complete['requests_submitted']==complete['responses_received']==complete['saf355_certifications_located']==complete['executed_historical_bank_rows_confirmed']==0
execution = rows('E0_COMMONCRAWL_EXACT_PREFIX_EXECUTION_V172.csv')
assert len(execution)==106 and all(r['classification']=='NO_CAPTURE_VALID' for r in execution)
assert {r['run_scope'] for r in execution}=={'HEALTH_CONTROL_2014_49','2016_REMAINING','2017_2020_FULL'}
summary = rows('E0_COMMONCRAWL_QUERY_COMPLETENESS_V172.csv')
total = next(r for r in summary if r['batch']=='V172_TOTAL')
assert total['queries']=='106' and total['valid_no_capture']=='106' and total['service_errors']=='0' and total['captures']=='0'
control = rows('V172_PDF_VISUAL_CONTROL.csv')
assert len(control)==1 and control[0]['pdf_page']=='22' and control[0]['printed_page']=='21' and control[0]['visual_result'].startswith('PASS')
assert len(rows('E0_SIGEN_MESA_DIGITAL_ARCHIVE_CONTINUITY_V172.csv'))==3
assert len(rows('E0_CGN_NOTE_METADATA_AND_HYBRID_CUSTODY_V172.csv'))==6
assert len(rows('E0_COMDOC_SCOPE_CORRECTION_V172.csv'))==3
assert len(rows('E0_SIGEN_RES41_2007_BODY_SEARCH_V172.csv'))==3
keys = rows('E0_REQUEST_SEARCH_KEY_MATRIX_V172.csv')
assert {'SK172_20','SK172_21','SK172_22','SK172_23','SK172_24'} <= {r['key_id'] for r in keys}
objects = rows('E0_V172_REQUEST_OBJECTS.csv')
assert {'RO172_20','RO172_21','RO172_22','RO172_23'} <= {r['row_id'] for r in objects}
assert all(r['status']=='DRAFT_NOT_SENT' for r in objects)
assert objects == rows('E0_V172_REQUEST_OBJECTS_V172.csv')
for name in ('REQUEST_AGN_2018_REPLY_V172.md','REQUEST_BCRA_CRYL_SETTLEMENT_V172.md','REQUEST_BNA_FIRST_STAGE_BLOTTER_V172.md','REQUEST_CAJA_SETTLEMENT_HOLDINGS_V172.md','REQUEST_CNV_CUSTODY_RECORDS_V172.md','REQUEST_ECONOMIA_TESORO_SETTLEMENT_V172.md'):
    text=(HERE/name).read_text(encoding='utf-8-sig')
    assert 'DRAFT_NOT_SENT' in text or 'BORRADOR_NO_ENVIADO' in text
assert 'Adenda V172 · Mesa SIGEN' in (HERE/'REQUEST_ECONOMIA_TESORO_SETTLEMENT_V172.md').read_text(encoding='utf-8-sig')
panel=rows('FOUR_LEG_PASS_PANEL_V172.csv')
assert len(panel)==45 and sum(r['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for r in panel)==34
coverage=rows('STRICT_Q4_FOUR_LEG_COVERAGE_V172.csv')
assert len(coverage)==1 and coverage[0]['asset_coverage_pct']==COVERAGE and coverage[0]['asset_numerator_million_ars']=='61345602.215'
bundle=rows('V172_SOURCE_BUNDLE.csv')
assert len(bundle)==7
for r in bundle:
    p=REPO/r['path'].lstrip('/')
    assert p.is_file() and p.stat().st_size==int(r['bytes']) and sha(p)==r['sha256']
manifest=json.loads((HERE/'MANIFEST_V172.json').read_text(encoding='utf-8-sig'))
assert manifest['checkpoint']=='V172' and manifest['parent_checkpoint']=='V171' and manifest['requests_submitted']==0
assert manifest['commoncrawl_queries_v172']==manifest['commoncrawl_valid_negatives_v172']==106
assert manifest['commoncrawl_service_errors_v172']==manifest['commoncrawl_captures_v172']==0
for r in manifest['files']:
    p=HERE/r['path']; assert p.is_file() and p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
print('V172 QA PASS · 602/602 · new=3 · cc=106/106-valid-negative/0-error/0-capture · SIGEN_CGN_ROUTES=LOCATED · panel=34 · requests=0 · SAF355=0/5 · execution=0/10')
