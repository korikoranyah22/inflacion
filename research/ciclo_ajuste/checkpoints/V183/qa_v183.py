from pathlib import Path
import csv,hashlib,json
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==703
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V183.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==703 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V183.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V183' and co['master_catalog_entries']==703
assert co['my4002_foreign_balance_stable_2012_2017'] and co['my4002_2018_uepex_declared_zero'] and not co['my4002_2018_bcra_identifiable_support']
assert not co['my4002_counterparty_proved'] and not co['bid1192_my4002_link_to_res1406_proved'] and not co['bid1192_damage_or_appropriation_proved']
s=rows('E0_BID1192_MY4002_ACCOUNT_SERIES_2006_2018_V183.csv'); assert len(s)==13
assert next(x for x in s if x['year']=='2015')['ars_identity_gap']=='60982.39'
assert next(x for x in s if x['year']=='2018')['closing_vs_extract_foreign_gap']=='15182.68'
assert len(rows('E0_BID1192_MY4002_DECOMPOSITION_V183.csv'))==7 and len(rows('E0_BID1192_MY4002_CLAIM_SEPARATION_V183.csv'))==7
assert len(rows('V183_SOURCE_BUNDLE.csv'))==7 and len(rows('V183_PDF_VISUAL_CONTROL.csv'))==7 and len(rows('V183_PDF_TEXT_CONTROL.csv'))==7
obj=rows('E0_V183_REQUEST_OBJECTS.csv'); assert {'RO183_80','RO183_81','RO183_82'}<={x['row_id'] for x in obj}; assert all(x['status']=='DRAFT_NOT_SENT' for x in obj); assert obj==rows('E0_V183_REQUEST_OBJECTS_V183.csv')
panel=rows('FOUR_LEG_PASS_PANEL_V183.csv'); assert len(panel)==45 and sum(x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for x in panel)==34
m=json.loads((H/'MANIFEST_V183.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V183' and m['parent_checkpoint']=='V182' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V183 QA PASS · 703/703 · MY4002_SERIES · 2018_BANK_SUPPORT=NO · counterparty=NO · damage=NO · requests=0')
