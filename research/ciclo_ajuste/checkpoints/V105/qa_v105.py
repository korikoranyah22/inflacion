from pathlib import Path
import csv
p=Path(__file__).parent
need=['CNV_EXACT_PRESENTATION_TARGETS_V105.csv','CNV_OFFICIAL_TARGET_REVALIDATION_V105.csv','CNV_PUBLICVIEW_LIVE_INDEX_V105.csv','CNV_ATTACHMENT_JSON_SCHEMA_CORROBORATION_V105.csv','CNV_ATTACHMENT_ROUTE_V105.md','RECOVERY_QUEUE_V105.csv','CURRENT_STATE_V105.csv']
for f in need: assert (p/f).exists(), f
c=list(csv.DictReader(open(p/'STRICT_Q4_FOUR_LEG_COVERAGE_V105.csv',encoding='utf-8-sig')))[0]
assert c['asset_coverage_pct']=='59.7775957463226204806504411472763588249111893261199797672530882599989158997072479353967644'
t=list(csv.DictReader(open(p/'CNV_EXACT_PRESENTATION_TARGETS_V105.csv',encoding='utf-8-sig')))
assert len(t)==6
assert {x['presentation_id'] for x in t}=={'3122483','3165651','3121099','3163537','3119515','3171909'}
assert '3177414' not in {x['presentation_id'] for x in t}
m=next(x for x in t if x['presentation_id']=='3122483')
assert 'DIRECT_PUBLICVIEW_LIVE_INDEX_CONFIRMED_V105' in m['status']
b=next(x for x in t if x['presentation_id']=='3171909')
assert '3177414' in b['status'] and 'DO_NOT_SUBSTITUTE' in b['status']
r=list(csv.DictReader(open(p/'CNV_OFFICIAL_TARGET_REVALIDATION_V105.csv',encoding='utf-8-sig')))
assert len(r)==6 and all(x['basis'].startswith('INDIVIDUAL') for x in r)
s=list(csv.DictReader(open(p/'CNV_ATTACHMENT_JSON_SCHEMA_CORROBORATION_V105.csv',encoding='utf-8-sig')))
fields={x['field'] for x in s}
assert {'pdf_blob_guid','pdf_nombre_archivo','pdf_tamano_bytes','pdf_hash'} <= fields
q=list(csv.DictReader(open(p/'RECOVERY_QUEUE_V105.csv',encoding='utf-8-sig')))
for name in ['Banco Mariva S.A.','HSBC Bank Argentina S.A.','Banco BMA / ex Banco Itau Argentina S.A.']:
    x=next(r for r in q if r['entity']==name); assert 'BLOB_GUID_NOT_RECOVERED' in x['status']
state=list(csv.DictReader(open(p/'CURRENT_STATE_V105.csv',encoding='utf-8-sig')))
rio=next(x for x in state if x['entity']=='Banco Rioja S.A.U.'); assert 'MISMATCH' in rio['q4_four_leg_status']
voii=next(x for x in state if x['entity']=='Banco VOII S.A.'); assert 'SOURCE_HOLD' in voii['q4_four_leg_status']
print('V105 QA PASS')
