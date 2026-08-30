from pathlib import Path
import csv
p=Path(__file__).parent
assert (p/'HIPOTECARIO_WEB_REVALIDATION_V100.md').exists()
assert (p/'BMA_FY_PRESENTATION_TARGET_CORRECTION_V100.md').exists()
q=list(csv.DictReader(open(p/'RECOVERY_QUEUE_V100.csv',encoding='utf-8-sig')))
assert any(r['entity'].startswith('Banco Hipotecario') and 'SOURCE_PRESERVATION' in r['status'] for r in q)
assert any('BMA' in r['entity'] and '#3171909' in r['missing_artifact'] for r in q)
c=list(csv.DictReader(open(p/'STRICT_Q4_FOUR_LEG_COVERAGE_V100.csv',encoding='utf-8-sig')))[0]
assert c['asset_coverage_pct']=='59.777595746322620480650441147276358824911189326119979767253088259998915899707248'
print('V100 QA PASS')
