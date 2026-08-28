from pathlib import Path
import pandas as pd, json, sys
ROOT=Path(__file__).resolve().parent
required=[
'COMPONENT_COUNTERPARTY_MAP_V52.csv','INCIDENCE_CHAIN_V52.csv','HOUSEHOLD_LINK_CLASSIFICATION_V52.csv','FALSIFICADORES_INCIDENCE_V52.csv','AUDITORIA_CONTRAPARTES_V52.md','VEREDICTO_CONTRAPARTES_V52.md','EVIDENCE_LEDGER_CICLO_AJUSTE_V52.csv','PROMPT_CODEX_V53_COUNTERPARTY_QUANTIFICATION.md','README_V52.md','MANIFEST_V52.json']
missing=[x for x in required if not (ROOT/x).exists()]
assert not missing, f'Missing: {missing}'
df=pd.read_csv(ROOT/'COMPONENT_COUNTERPARTY_MAP_V52.csv')
allowed={'DIRECT_HOUSEHOLD_CONTRACT','INDIRECT_HOUSEHOLD_EXPOSURE','BCRA_COUNTERPARTY','TREASURY_COUNTERPARTY','MARKET_VALUATION','CORPORATE_COUNTERPARTY','DEPOSITOR_COUNTERPARTY','MIXED','N/D'}
assert set(df.primary_counterparty_label).issubset(allowed), set(df.primary_counterparty_label)-allowed
# Frozen core gates
ver=(ROOT/'VEREDICTO_CONTRAPARTES_V52.md').read_text(encoding='utf-8')
assert 'DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED_AT_ABNORMAL_GAP_LEVEL' in ver
assert 'TAXPAYER_IDENTITY = REJECTED' in ver
assert 'NEXT = V53_COUNTERPARTY_QUANTIFICATION' in ver
# no HTML should be generated in V52
assert not list(ROOT.glob('*.html')), 'V52 must not modify/generate HTML'
# diagnostic check
q=df[(df.episode==2023)&(df.window=='Q4_2023_vs_Q3_2023')]
p=float(q.loc[q.accounting_component=='pass_premiums','abnormal_gap_pp'].iloc[0])
assert abs(p-7.7)<1e-9
print('V52 QA PASS')
