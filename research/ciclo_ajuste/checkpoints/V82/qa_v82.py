from pathlib import Path
import csv, math
p=Path(__file__).parent
with open(p/'STRICT_Q4_FOUR_LEG_COVERAGE_V82.csv',encoding='utf-8') as f:
    r=next(csv.DictReader(f))
assert math.isclose(float(r['asset_coverage_pct']), 23.54332498027319, rel_tol=0, abs_tol=1e-12)
assert float(r['increment_vs_v81_pp']) == 0
assert r['closed_network_gate'].startswith('NO_')
with open(p/'FOUR_LEG_PASS_PANEL_V82.csv',encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
elig=[r for r in rows if r['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS']
assert len(elig)==5, len(elig)
assert {r['entity'] for r in elig} == {'Industrial and Commercial Bank of China (Argentina) S.A.U.','Banco de Valores S.A.','Banco Macro S.A.','Banco Credicoop Cooperativo Limitado','Banco de la Provincia de Buenos Aires'}
with open(p/'RECOVERY_QUEUE_V82.csv',encoding='utf-8') as f:
    rq=list(csv.DictReader(f))
assert rq[0]['status']=='PENDING_USER_UPLOAD'
assert 'Anexo' in rq[0]['missing_artifact']
print('QA_V82_PASS')
