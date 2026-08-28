from pathlib import Path
import csv, math
ROOT=Path(__file__).resolve().parent
FACTOR=3533.2/2304.9
def q4(fy,sep): return fy-sep*FACTOR
assert math.isclose(q4(438280940,155837409), 199396505.32656518, rel_tol=0, abs_tol=1e-6)
assert math.isclose(q4(344649,197543), 41833.72489045083, rel_tol=0, abs_tol=1e-6)
assert math.isclose(q4(2307851,889799), 943870.8590828236, rel_tol=0, abs_tol=1e-6)
assert q4(438280940,155837409) > 0
assert q4(344649,197543)-q4(2307851,889799) < 0
with open(ROOT/'FOUR_LEG_PASS_PANEL_V64.csv',encoding='utf-8-sig') as f:
    rows=list(csv.DictReader(f))
icbc=[r for r in rows if r['entity'].startswith('Industrial and Commercial')][0]
assert icbc['basis']=='INDIVIDUAL_STANDALONE'
assert icbc['closed_system_test'].startswith('NO_')
with open(ROOT/'CLOSED_NETWORK_NETTING_TEST_V64.csv',encoding='utf-8-sig') as f:
    rows=list(csv.DictReader(f))
system=[r for r in rows if r['scope']=='SYSTEM'][0]
assert system['can_test_system_cancellation']!='YES'
with open(ROOT/'HOUSEHOLD_SECTOR_MAPPING_V64.csv',encoding='utf-8-sig') as f:
    rows=list(csv.DictReader(f))
assert all(r['institutional_sector_identity']!='YES' for r in rows)
print('PASS')
