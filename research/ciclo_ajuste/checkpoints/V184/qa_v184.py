from pathlib import Path
import csv,hashlib,json
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==708
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
mis=next(x for x in cat if x['id']=='e0_cgn_account2020_bank_accounts_mypes_absence_v182'); assert 'contenido interno Anexo 4.36' in mis['titulo']
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V184.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==708 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V184.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V184' and co['master_catalog_entries']==708
assert co['my4002_2020_administrative_active_reported'] and co['my4002_2020_numeric_fields_blank'] and not co['my4002_2020_balance_proved']
assert not co['my4002_executed_transfer_agreement_located'] and not co['bid1192_my4002_link_to_res1406_proved'] and not co['bid1192_damage_or_appropriation_proved']
trans=rows('E0_BID1192_CGN_TRANSITION_2018_2021_V184.csv'); assert len(trans)==5 and any(x['bank_account_state']=='MY4002_REPORTED_ACTIVE_UNDER_FONDYF_2020_FIELDS_BLANK' for x in trans)
ladder=rows('E0_BID1192_MY4002_EVIDENCE_LADDER_V184.csv'); assert len(ladder)==8 and any(x['status']=='SUPPORTED_ADMINISTRATIVE_NARRATIVE' for x in ladder)
assert len(rows('V184_SOURCE_BUNDLE.csv'))==5 and len(rows('V184_PDF_VISUAL_CONTROL.csv'))==2 and len(rows('V184_HTML_CONTENT_CONTROL.csv'))==3
obj=rows('E0_V184_REQUEST_OBJECTS.csv'); assert {'RO184_83','RO184_84','RO184_85','RO184_86'}<={x['row_id'] for x in obj}; assert all(x['status']=='DRAFT_NOT_SENT' for x in obj); assert obj==rows('E0_V184_REQUEST_OBJECTS_V184.csv')
panel=rows('FOUR_LEG_PASS_PANEL_V184.csv'); assert len(panel)==45 and sum(x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for x in panel)==34
m=json.loads((H/'MANIFEST_V184.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V184' and m['parent_checkpoint']=='V183' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V184 QA PASS · 708/708 · MY4002_ACTIVE_REPORTED · 2020_BALANCE=OPEN · transfer=OPEN · damage=NO · requests=0')
