from pathlib import Path
import csv, json, sys
p=Path(__file__).resolve().parent
required=[
"RAW_MODERN_XLSX_MANIFEST_V58.csv","MODERN_SOURCE_SHEET_MAP_V58.csv",
"IEF_COMPONENT_RECONCILIATION_V58.csv","INTEREST_FLOW_SECTOR_BRIDGE_V58.csv",
"SECURITIES_ISSUER_RESULT_BRIDGE_V58.csv","FX_CER_PASSES_BRIDGE_V58.csv",
"COUNTERPARTY_UPDATE_V58.csv","AUDITORIA_V58.md","VEREDICTO_V58.md",
"EVIDENCE_LEDGER_CICLO_AJUSTE_V58.csv","FUENTES_V58.md","README_V58.md",
"PROMPT_CODEX_V59_ENTITY_LEVEL_REAL_MARGIN_BRIDGE.md","BASE_V57.zip"
]
for f in required:
    assert (p/f).exists(), f"missing {f}"
rows=list(csv.DictReader(open(p/"IEF_COMPONENT_RECONCILIATION_V58.csv",encoding="utf-8-sig")))
by={r["component_id"]:r for r in rows}
assert by["interest_income"]["reconciliation_status"]=="REJECT_DIRECT_P24_MAPPING"
assert abs(float(by["interest_income"]["ief_q4_minus_q3_pp"])-2.1)<1e-9
assert abs(float(by["passes"]["ief_q4_minus_q3_pp"])-7.7)<1e-9
assert abs(float(by["securities_ori"]["ief_q4_minus_q3_pp"])-7.3)<1e-9
assert abs(float(by["fx"]["ief_q4_minus_q3_pp"])-11.3)<1e-9
assert abs(float(by["cer_cvs"]["ief_q4_minus_q3_pp"])+0.2)<1e-9
assert float(by["interest_income"]["q3_implied_an_vs_anchor_ratio"])>3
assert float(by["interest_income"]["q4_implied_an_vs_anchor_ratio"])>3
counter=list(csv.DictReader(open(p/"COUNTERPARTY_UPDATE_V58.csv",encoding="utf-8-sig")))
b={r["bucket"]:r for r in counter}
assert abs(float(b["PASSES_DIRECT_BCRA"]["pp"])-7.7)<1e-9
assert abs(float(b["UNRESOLVED_COUNTERPARTY"]["pp"])-21.0)<1e-9
print("PASS")
