from pathlib import Path
import csv,hashlib,json
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==684
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
for sid,sentence in (("e0_bo_res967_2006_full_annex_contract_v179","V180 acredita que el modelo Res. 967 no estaba perfeccionado al 22/02/2008; no se lo trata como régimen operativo."),("e0_norm_res967_2006_mypesii_trust_v178","AGN 14/2010 informa que el contrato aprobado por Res. 967/2006 no estaba perfeccionado al 22/02/2008.")):
 note=next(x['nota'] for x in cat if x['id']==sid); assert note.count(sentence)==1
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V181.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==684 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V181.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V181' and co['master_catalog_entries']==684
assert co['mypesii_res1406_reported_by_repeated_sigen'] and co['mypesii_res1406_appeals_reported'] and not co['mypesii_res1406_full_act_located'] and not co['mypesii_res1406_final_decision_located'] and not co['mypesii_res1406_payment_proved']
assert co['mypesii_commitment_clause_formula_corroborated'] and not co['mypesii_ucp_2005_instruction_located'] and not co['mypesii_sensitivity_is_debt']
assert co['mypesii_macro_collateral_series_2006_2012_reconstructed'] and co['mypesii_bcra_trust_10155_exit_2012_supported'] and not co['mypesii_bcra_registry_exit_legal_act_located'] and not co['bid1192_damage_or_appropriation_proved']
assert len(rows('V181_SOURCE_BUNDLE.csv'))==11 and len(rows('V181_PDF_VISUAL_CONTROL.csv'))==6 and all(x['result'].startswith('PASS_RELEVANT_') for x in rows('V181_PDF_VISUAL_CONTROL.csv'))
assert len(rows('V181_HTML_CONTENT_CONTROL.csv'))==5 and all(x['result']=='PASS_CONTENT_CONTROL' for x in rows('V181_HTML_CONTENT_CONTROL.csv'))
assert len(rows('E0_BID1192_COMMITMENT_COMMISSION_DISPUTE_CHAIN_2005_2019_V181.csv'))==8
assert len(rows('E0_BID1192_RES1406_EVIDENCE_LADDER_V181.csv'))==6
assert len(rows('E0_BID1192_MACRO_COLLATERAL_TRAJECTORY_2006_2012_V181.csv'))==7
assert len(rows('E0_BID1192_BCRA_TRUST_CLOSURE_CROSSCHECK_2010_2012_V181.csv'))==4
assert len(rows('E0_BID1192_COMMISSION_ILLUSTRATIVE_SENSITIVITY_V181.csv'))==4 and all(x['legal_status']=='SENSITIVITY_NOT_DEBT' for x in rows('E0_BID1192_COMMISSION_ILLUSTRATIVE_SENSITIVITY_V181.csv'))
obj=rows('E0_V181_REQUEST_OBJECTS.csv'); assert {f'RO181_{x}' for x in range(69,77)}<={x['row_id'] for x in obj}; assert all(x['status']=='DRAFT_NOT_SENT' for x in obj); assert obj==rows('E0_V181_REQUEST_OBJECTS_V181.csv')
keys=rows('E0_REQUEST_SEARCH_KEY_MATRIX_V181.csv'); assert {f'SK181_{x}' for x in range(70,76)}<={x['key_id'] for x in keys}
panel=rows('FOUR_LEG_PASS_PANEL_V181.csv'); assert len(panel)==45 and sum(x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for x in panel)==34
m=json.loads((H/'MANIFEST_V181.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V181' and m['parent_checkpoint']=='V180' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V181 QA PASS · 684/684 · new=11 · PDF=6 relevant-page visual · RES1406=REPORTED_CONTESTED · MACRO_COLLATERAL=2006-2012 · damage=NO · panel=34 · requests=0')
