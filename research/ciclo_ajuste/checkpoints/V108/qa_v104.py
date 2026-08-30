from pathlib import Path
import csv, json
p=Path(__file__).parent
for f in ['CNV_EXACT_PRESENTATION_TARGETS_V104.csv','CNV_PUBLICVIEW_FRONTEND_FORENSICS_V104.csv','CNV_PUBLICVIEW_CAPTURE_ARTIFACTS_V104.csv','CNV_PUBLICVIEW_FRONTEND_FORENSICS_V104.md','RECOVERY_QUEUE_V104.csv','CURRENT_STATE_V104.csv']:
    assert (p/f).exists(), f
c=list(csv.DictReader(open(p/'STRICT_Q4_FOUR_LEG_COVERAGE_V104.csv',encoding='utf-8-sig')))[0]
assert c['asset_coverage_pct']=='59.7775957463226204806504411472763588249111893261199797672530882599989158997072479353967644'
t=list(csv.DictReader(open(p/'CNV_EXACT_PRESENTATION_TARGETS_V104.csv',encoding='utf-8-sig')))
assert len(t)==6
assert {x['presentation_id'] for x in t}=={'3122483','3165651','3121099','3163537','3119515','3171909'}
assert '3177414' not in {x['presentation_id'] for x in t}
assert all('INHERITED' in x['status'] and 'V104_DIRECT_FETCH_CHANNEL_UNAVAILABLE' in x['status'] for x in t)
f=list(csv.DictReader(open(p/'CNV_PUBLICVIEW_FRONTEND_FORENSICS_V104.csv',encoding='utf-8-sig')))
paths={x['resource_path']:x for x in f}
for x in ['/js/Presentations/presentations.js','/lib/jquery-file-download/jquery.fileDownload.js','/Engine/js/fb.fileutils.js','/Engine/js/fbhtmlcontrols/fb.publicuploader.js']:
    assert x in paths
assert paths['/js/Presentations/presentations.js']['content_length']=='4192'
assert paths['/lib/jquery-file-download/jquery.fileDownload.js']['content_length']=='20099'
assert paths['/Engine/js/fb.fileutils.js']['content_length']=='2404'
assert paths['/Engine/js/fbhtmlcontrols/fb.publicuploader.js']['content_length']=='10737'
a=list(csv.DictReader(open(p/'CNV_PUBLICVIEW_CAPTURE_ARTIFACTS_V104.csv',encoding='utf-8-sig')))
h=next(x for x in a if x['artifact']=='extracted PublicView HTML')
assert h['bytes']=='77570'
assert h['sha256']=='33ca3bed35d68eff021ee21a92444b0d0fc8d86ec9931c34b2d0aedd9427f1ba'
q=list(csv.DictReader(open(p/'RECOVERY_QUEUE_V104.csv',encoding='utf-8-sig')))
for name in ['Banco Mariva S.A.','HSBC Bank Argentina S.A.','Banco BMA / ex Banco Itau Argentina S.A.']:
    x=next(r for r in q if r['entity']==name)
    assert 'PUBLICVIEW_FRONTEND' in x['status']
state=list(csv.DictReader(open(p/'CURRENT_STATE_V104.csv',encoding='utf-8-sig')))
r=next(x for x in state if x['entity']=='Banco Rioja S.A.U.')
assert 'MISMATCH' in r['q4_four_leg_status']
v=next(x for x in state if x['entity']=='Banco VOII S.A.')
assert 'SOURCE_HOLD' in v['q4_four_leg_status']
print('V104 QA PASS')
