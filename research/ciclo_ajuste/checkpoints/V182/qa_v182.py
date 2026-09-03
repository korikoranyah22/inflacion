from pathlib import Path
import csv,hashlib,json
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==697
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V182.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==697 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V182.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V182' and co['master_catalog_entries']==697
assert co['bid1192_my4002_identified'] and not co['bid1192_my4002_link_to_res1406_proved']
assert co['bid1192_2020_all_financial_fields_zero'] and not co['bid1192_2020_final_closure_certified']
assert co['bid1192_2021_absent_from_published_saf362'] and not co['bid1192_final_closure_act_located']
assert not co['mypesii_res1406_infoleg_published_identity_match'] and not co['mypesii_res1406_payment_proved'] and not co['bid1192_damage_or_appropriation_proved']
assert len(rows('V182_SOURCE_BUNDLE.csv'))==14 and len(rows('V182_PDF_VISUAL_CONTROL.csv'))==4 and len(rows('V182_XLSX_CONTENT_CONTROL.csv'))==4
assert len(rows('V182_HTML_CONTENT_CONTROL.csv'))==4 and len(rows('V182_JSON_CONTENT_CONTROL.csv'))==2
assert len(rows('E0_BID1192_CGN_TRANSITION_2018_2021_V182.csv'))==4 and len(rows('E0_BID1192_ACCOUNT_BALANCES_REFERENCE_2018_V182.csv'))==16
assert len(rows('E0_BID1192_MY4002_EVIDENCE_LADDER_V182.csv'))==5 and len(rows('E0_RES1406_IDENTITY_AND_ARCHIVE_CONTROL_V182.csv'))==5
obj=rows('E0_V182_REQUEST_OBJECTS.csv'); assert {'RO182_77','RO182_78','RO182_79'}<={x['row_id'] for x in obj}; assert all(x['status']=='DRAFT_NOT_SENT' for x in obj); assert obj==rows('E0_V182_REQUEST_OBJECTS_V182.csv')
panel=rows('FOUR_LEG_PASS_PANEL_V182.csv'); assert len(panel)==45 and sum(x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for x in panel)==34
m=json.loads((H/'MANIFEST_V182.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V182' and m['parent_checkpoint']=='V181' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V182 QA PASS · 697/697 · MY4002=REFERENCE_ONLY · 2020_ZERO_CLOSURE_UNCERTIFIED · 2021_EXIT_PUBLICATION_ONLY · damage=NO · requests=0')
