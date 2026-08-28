from pathlib import Path
import pandas as pd, json, sys
P=Path(__file__).resolve().parent
req=[
'RAW_SOURCE_MANIFEST_V54.csv','SECURITIES_RESULT_BRIDGE_V54.csv','INTEREST_INCOME_ACCOUNTING_BRIDGE_V54.csv',
'CER_GROSS_BRIDGE_V54.csv','FX_GROSS_RESULT_BRIDGE_V54.csv','Q4_2023_JOINT_COUNTERPARTY_PARTITION_V54.csv',
'AUDITORIA_MICRODATA_BRIDGE_V54.md','VEREDICTO_MICRODATA_BRIDGE_V54.md','EVIDENCE_LEDGER_CICLO_AJUSTE_V54.csv',
'README_V54.md','MANIFEST_V54.json','BASE_V53.zip','FUENTES_V54.md','PROMPT_CODEX_V55_BYTE_MATERIALIZATION_AND_SUBACCOUNT_RECONCILIATION.md'
]
missing=[x for x in req if not (P/x).exists()]
assert not missing, f"Missing: {missing}"
part=pd.read_csv(P/'Q4_2023_JOINT_COUNTERPARTY_PARTITION_V54.csv')
rows=part[part['bucket'].isin(['Primas por pases','Diferencias de cotización','Resultado por títulos valores','Ingresos por intereses','Otros resultados financieros'])]
assert abs(rows['gap_pp'].sum()-28.7)<1e-9
sumr=part[part['bucket'].isin(['STRICT_IDENTIFIED_COUNTERPARTY_MASS','UNRESOLVED_COUNTERPARTY_MASS'])]
assert abs(sumr['gap_pp'].sum()-28.7)<1e-9
raw=pd.read_csv(P/'RAW_SOURCE_MANIFEST_V54.csv')
assert (~raw['local_bytes_materialized']).all()
assert (raw['sha256']=='N/D').all()
ver=(P/'VEREDICTO_MICRODATA_BRIDGE_V54.md').read_text(encoding='utf-8')
for s in ['V53_MARKET_VALUATION_FLOOR_39_37 = REVOKED','V53_HOUSEHOLD_[0,2.1]PP_STRICT_CEILING = REVOKED','BCRA_DIRECT_COUNTERPARTY_FLOOR = 7.7 PP']:
    assert s in ver, s
print('PASS')
