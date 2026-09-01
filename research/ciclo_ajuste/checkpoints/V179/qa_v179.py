from pathlib import Path
import csv,hashlib,json
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==649
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V179.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==649 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V179.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V179' and co['master_catalog_entries']==649
assert co['mypesii_approved_contract_full_body_located'] and not co['mypesii_executed_contract_full_body_located']
assert co['mypesii_ifi_guarantee_indemnity_model_proved'] and not co['mypesii_ifi_guarantee_execution_proved']
assert co['mypesii_clause16_reporting_duties_proved'] and not co['mypesii_clause16_reports_located']
assert not co['mypesii_2006_to_fondyf_2013_transition_instrument_located'] and not co['bid1192_damage_or_appropriation_proved']
assert co['requests_submitted']==co['saf355_certifications_located']==co['executed_historical_bank_rows_confirmed']==0
assert len(rows('E0_BID1192_RES967_DIGITAL_PACKAGE_STRUCTURE_V179.csv'))==6
assert len(rows('E0_BID1192_2006_ROLE_RESPONSIBILITY_MATRIX_V179.csv'))==10
assert len(rows('E0_BID1192_IFI_GUARANTEE_INDEMNITY_MATRIX_V179.csv'))==11
assert len(rows('E0_BID1192_CONTRACTUAL_REPORTING_DATA_INVENTORY_V179.csv'))==10
assert len(rows('E0_BID1192_2006_VS_2013_ROLE_NONTRANSPOSITION_V179.csv'))==9
assert len(rows('E0_BID1192_EXECUTED_MODEL_STATUS_V179.csv'))==7
assert rows('V179_PDF_VISUAL_CONTROL.csv')[0]['result']=='PASS_ALL_99_PAGES_VISUALLY_INSPECTED'
assert len(rows('V179_HTML_CONTENT_CONTROL.csv'))==5 and all(x['result']=='PASS_EXACT_STRING' for x in rows('V179_HTML_CONTENT_CONTROL.csv'))
assert len(rows('V179_SOURCE_BUNDLE.csv'))==6
keys=rows('E0_REQUEST_SEARCH_KEY_MATRIX_V179.csv'); target_keys={f'SK178_{x}' for x in range(50,56)}|{f'SK179_{x}' for x in range(56,62)}; assert target_keys<={x['key_id'] for x in keys}; assert all(x['exact_key'] for x in keys if x['key_id'] in target_keys)
obj=rows('E0_V179_REQUEST_OBJECTS.csv'); target_objects={f'RO178_{x}' for x in range(48,54)}|{f'RO179_{x}' for x in range(54,60)}; assert target_objects<={x['row_id'] for x in obj}; assert all(x['status']=='DRAFT_NOT_SENT' for x in obj); assert all(x['object_id'] and x['exact_record'] for x in obj if x['row_id'] in target_objects); assert obj==rows('E0_V179_REQUEST_OBJECTS_V179.csv')
panel=rows('FOUR_LEG_PASS_PANEL_V179.csv'); assert len(panel)==45 and sum(x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for x in panel)==34
m=json.loads((H/'MANIFEST_V179.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V179' and m['parent_checkpoint']=='V178' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V179 QA PASS · 649/649 · RES967=99/99 VISUAL · IFI-GUARANTEE=MODEL_PROVED · EXECUTION=OPEN · panel=34 · requests=0')
