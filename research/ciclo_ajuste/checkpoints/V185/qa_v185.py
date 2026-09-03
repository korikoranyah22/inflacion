from pathlib import Path
import csv,hashlib,json
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==718
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V185.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==718 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V185.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V185' and co['account_54395_36_esidif_ledger_balance']==-36600000
assert not co['account_54395_36_my4002_crosswalk_proved'] and not co['bid1192_composition_proved'] and not co['damage_or_liability_proved']
gap=rows('E0_FONDYF_54395_36_ACCOUNT_GAP_V185.csv'); assert len(gap)==8 and any(x['field']=='eSIDIF_ledger_balance' and x['value']=='-36600000' for x in gap)
tl=rows('E0_SAF362_RECONCILIATION_TIMELINE_2021_2024_V185.csv'); assert len(tl)==9 and sum(x['account_named']=='YES' for x in tl)==1
sep=rows('E0_FONDYF_MY4002_ACCOUNT_SEPARATION_V185.csv'); assert len(sep)==6 and sum(x['status']=='NOT_PROVED' for x in sep)>=3
assert len(rows('V185_SOURCE_BUNDLE.csv'))==10 and len(rows('V185_PDF_VISUAL_CONTROL.csv'))==10
obj=rows('E0_V185_REQUEST_OBJECTS.csv'); assert {'RO185_87','RO185_88','RO185_89','RO185_90','RO185_91','RO185_92'}<={x['row_id'] for x in obj}; assert all(x['status']=='DRAFT_NOT_SENT' for x in obj)
m=json.loads((H/'MANIFEST_V185.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V185' and m['parent_checkpoint']=='V184' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V185 QA PASS · 718/718 · 54395/36=-36.6m ESIDIF LEDGER · MY4002/BID1192=OPEN · damage=NO · requests=0')
