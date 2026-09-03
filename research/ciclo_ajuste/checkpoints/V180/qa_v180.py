from pathlib import Path
import csv,hashlib,json
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==673
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V180.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==673 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V180.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V180' and co['master_catalog_entries']==673
assert co['mypesii_2004_contract_execution_date_officially_corroborated'] and co['mypesii_2005_contract_execution_date_officially_corroborated']
assert not co['mypesii_signed_executed_counterparts_located'] and not co['mypesii_res967_perfected_by_2008_02_22'] and not co['mypesii_suquia_executed_accession_located']
assert co['mypesii_res747_ifi_own_portfolio_limit_proved'] and co['mypesii_res747_macro_fiduciary_exclusive_guarantee_proved'] and not co['mypesii_guarantee_execution_proved']
assert co['mypesii_facility_rate_architecture_proved'] and not co['mypesii_facility_operation_ledger_located'] and not co['mypesii_final_liquidation_balance_located'] and not co['bid1192_damage_or_appropriation_proved']
assert len(rows('V180_SOURCE_BUNDLE.csv'))==24 and len(rows('V180_PDF_VISUAL_CONTROL.csv'))==15 and all(x['result'].startswith('PASS_ALL_') for x in rows('V180_PDF_VISUAL_CONTROL.csv'))
assert len(rows('V180_HTML_CONTENT_CONTROL.csv'))==9 and all(x['result']=='PASS_EXACT_STRING' for x in rows('V180_HTML_CONTENT_CONTROL.csv'))
assert len(rows('E0_BID1192_CONTRACT_VERSION_CONTROL_2003_2008_V180.csv'))==8
assert len(rows('E0_BID1192_EXECUTED_INSTRUMENT_EVIDENCE_LADDER_V180.csv'))==4
assert len(rows('E0_BID1192_RES747_GUARANTEE_LIMITATION_MATRIX_V180.csv'))==4
assert len(rows('E0_BID1192_IFI_GUARANTEE_INDEMNITY_MATRIX_V180.csv'))==5
assert len(rows('E0_BID1192_TRUST_OPERATION_LEDGER_2005_2008_V180.csv'))==6
assert len(rows('E0_BID1192_AGN_FINDINGS_LEDGER_V180.csv'))==6
assert len(rows('E0_BID1192_TERMINATION_LIQUIDATION_TIMELINE_V180.csv'))==7
assert len(rows('E0_BID1192_FACILIDAD_RATE_AND_VOLUME_MATRIX_V180.csv'))==5
assert len(rows('E0_BID1192_BCRA_OBLIGATION_AND_RATE_ARCHITECTURE_V180.csv'))==6
assert len(rows('E0_BID1192_INTERNAL_SOURCE_CONFLICTS_V180.csv'))==5
obj=rows('E0_V180_REQUEST_OBJECTS.csv'); targets={f'RO180_{x}' for x in range(60,69)}; assert targets<={x['row_id'] for x in obj}; assert all(x['status']=='DRAFT_NOT_SENT' for x in obj); assert obj==rows('E0_V180_REQUEST_OBJECTS_V180.csv')
keys=rows('E0_REQUEST_SEARCH_KEY_MATRIX_V180.csv'); assert {f'SK180_{x}' for x in range(62,70)}<={x['key_id'] for x in keys}
panel=rows('FOUR_LEG_PASS_PANEL_V180.csv'); assert len(panel)==45 and sum(x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for x in panel)==34
m=json.loads((H/'MANIFEST_V180.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V180' and m['parent_checkpoint']=='V179' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V180 QA PASS · 673/673 · new=24 · PDF=15/15 FULL VISUAL · EXECUTION_DATES=CORROBORATED · RES967=NOT_PERFECTED · panel=34 · requests=0')
