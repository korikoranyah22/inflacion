from pathlib import Path
import csv,hashlib,json
from decimal import Decimal
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==630
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V177.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==630 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V177.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V177' and co['master_catalog_entries']==630
assert co['bid1192_program_continuity_2008_2019_proved'] and co['bid1192_exact_account_ids_common_2008_2009_2018']==14
assert co['bid1192_reference_2018_account_count']==16 and Decimal(co['bid1192_reference_2018_total_ars'])==Decimal('824861366.21')
assert not co['bid1192_2016_statement_verification_possible'] and not co['bid1192_2019_current_information_submitted']
assert not co['bid1192_note3672_sisio_crosswalk_proved'] and not co['bid1192_damage_or_appropriation_proved'] and not co['note_3672_target_sisio_rows_located']
assert co['requests_submitted']==co['saf355_certifications_located']==co['executed_historical_bank_rows_confirmed']==0 and co['commoncrawl_pending_retry_queries']==40
chain=rows('E0_BID1192_LONGITUDINAL_EVIDENCE_CHAIN_V177.csv'); assert len(chain)==8
ac=rows('E0_BID1192_ACCOUNT_ID_CONTINUITY_V177.csv'); assert len(ac)==16 and sum(x['present_2008']=='YES' for x in ac)==15 and sum(x['present_2009']=='YES' for x in ac)==14 and sum(x['present_2008']==x['present_2009']=='YES' for x in ac)==14
assert sum(Decimal(x['reference_2018_ars']) for x in ac)==Decimal('824861366.21')
qb=rows('E0_BID1192_QUANTIFIED_UNVERIFIED_BALANCES_V177.csv'); assert len(qb)==5 and Decimal(qb[2]['amount_ars'])==Decimal(qb[1]['amount_ars'])-Decimal(qb[0]['amount_ars'])
assert len(rows('E0_BID1192_RECURRENT_FLAG_TRAJECTORY_V177.csv'))==5
assert len(rows('E0_BID1192_RESPONSIBILITY_AND_EVIDENCE_LIMITS_V177.csv'))==6
assert len(rows('E0_NOTE_3672_BID1192_TARGET_CROSSWALK_REQUEST_V177.csv'))==6
assert len(rows('V177_PDF_VISUAL_CONTROL.csv'))==5 and all(x['result'].startswith('PASS') for x in rows('V177_PDF_VISUAL_CONTROL.csv'))
keys=rows('E0_REQUEST_SEARCH_KEY_MATRIX_V177.csv'); assert {'SK177_45','SK177_46','SK177_47','SK177_48','SK177_49'}<={x['key_id'] for x in keys}
obj=rows('E0_V177_REQUEST_OBJECTS.csv'); assert {'RO177_44','RO177_45','RO177_46','RO177_47'}<={x['row_id'] for x in obj} and all(x['status']=='DRAFT_NOT_SENT' for x in obj) and obj==rows('E0_V177_REQUEST_OBJECTS_V177.csv')
for n in ('REQUEST_AGN_2018_REPLY_V177.md','REQUEST_BCRA_CRYL_SETTLEMENT_V177.md','REQUEST_BNA_FIRST_STAGE_BLOTTER_V177.md','REQUEST_CAJA_SETTLEMENT_HOLDINGS_V177.md','REQUEST_CNV_CUSTODY_RECORDS_V177.md','REQUEST_ECONOMIA_TESORO_SETTLEMENT_V177.md'):
 s=(H/n).read_text(encoding='utf-8-sig'); assert 'DRAFT_NOT_SENT' in s or 'BORRADOR_NO_ENVIADO' in s
panel=rows('FOUR_LEG_PASS_PANEL_V177.csv'); assert len(panel)==45 and sum(x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for x in panel)==34
assert len(rows('V177_SOURCE_BUNDLE.csv'))==5
m=json.loads((H/'MANIFEST_V177.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V177' and m['parent_checkpoint']=='V176' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V177 QA PASS · 630/630 · new=3 · BID1192-chain=PROVED · SISIO-crosswalk=OPEN · panel=34 · requests=0')
