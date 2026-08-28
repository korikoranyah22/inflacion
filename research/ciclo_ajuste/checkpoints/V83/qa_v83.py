from pathlib import Path
import csv, hashlib
root=Path(__file__).resolve().parents[4]
v83=Path(__file__).resolve().parent
coverage=list(csv.DictReader(open(v83/'STRICT_Q4_FOUR_LEG_COVERAGE_V83.csv',encoding='utf-8')))[0]
assert abs(float(coverage['asset_coverage_pct'])-23.54332498027319) < 1e-12
assert float(coverage['increment_vs_v82_pp']) == 0
panel=list(csv.DictReader(open(v83/'FOUR_LEG_PASS_PANEL_V83.csv',encoding='utf-8')))
strict=[r for r in panel if r['period']=='Q4-2023' and r['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS']
assert len(strict)==5
p=root/'research/ciclo_ajuste/inputs/manual_recovery/bna_agn/2023-210-Informe CC 2.pdf'
h=hashlib.sha256(p.read_bytes()).hexdigest()
assert h=='563b4e6f30ff13bd7a8cec6f794ad90a64383866cf907c434d9c7841a703ffd5'
events=list(csv.DictReader(open(v83/'USER_UPLOAD_DUPLICATE_EVENTS_V83.csv',encoding='utf-8')))
assert events[0]['canonical_sha256']==h
assert 'DUPLICATE' in events[0]['verdict']
print('QA_V83_PASS')
