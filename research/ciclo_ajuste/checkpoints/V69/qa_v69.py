from pathlib import Path
import pandas as pd, math, json
p=Path(__file__).resolve().parent
required=['AUDITORIA_V69.md', 'BANCO_VALORES_Q4_AQ_BRIDGE_V69.csv', 'BAPRO_FY_AQ_CONTROL_V69.csv', 'BASE_V68.zip', 'BASIS_HARMONIZATION_V69.csv', 'BCRA_BANK_SYSTEM_COVERAGE_V69.csv', 'BNA_FY_AQ_CONTROL_V69.csv', 'CLOSED_NETWORK_COVERAGE_V69.csv', 'CLOSED_NETWORK_NETTING_TEST_V69.csv', 'COUNTERPARTY_UPDATE_V69.csv', 'CREDICOOP_FY_AQ_CONTROL_V69.csv', 'EVIDENCE_LEDGER_CICLO_AJUSTE_V69.csv', 'FOUR_LEG_PASS_PANEL_V69.csv', 'FUENTES_V69.md', 'HANDOVER_CODEX_CICLO_AJUSTE_V69_A_V70.md', 'HOUSEHOLD_PRODUCT_PANEL_V69.csv', 'HOUSEHOLD_SECTOR_MAPPING_V69.csv', 'IEF_PASS_RECONCILIATION_V69.csv', 'INDIVIDUAL_AQ_RETRIEVAL_V69.csv', 'MACRO_Q4_AQ_BRIDGE_V69.csv', 'PASS_COUNTERPARTY_BOUNDS_V69.csv', 'PROMPT_CODEX_V70_BNA_9M_BINARY_RECOVERY_AND_PUBLIC_BANK_AQ_EXTRACTION.md', 'PUBLIC_BANK_COVERAGE_PRIORITY_V69.csv', 'PUBLIC_BANK_SOURCE_RECOVERY_V69.csv', 'README_V69.md', 'SANTANDER_FY_AQ_CONTROL_V69.csv', 'SANTANDER_INTERIM_ANNEX_AUDIT_V69.md', 'SANTANDER_PRIMARY_RECOVERY_V69.csv', 'SUPERVIELLE_Q4_PASS_BOUND_V69.csv', 'VEREDICTO_V69.md']
for f in required:
    assert (p/f).exists(), f"missing {f}"
assert not list(p.glob("*.html")), "HTML forbidden"

den=96697695.5
cov=pd.read_csv(p/"BCRA_BANK_SYSTEM_COVERAGE_V69.csv")
strict=cov[cov.scope=="STRICT_Q4_FOUR_LEG_EXACT_TARGET_BASIS"].iloc[0]
assert abs(float(strict.asset_coverage_pct)-11.260967847987649)<1e-9
hyp=cov[cov.scope=="STRICT_PLUS_ALL_PUBLIC_COOP_PRIORITY_IF_EXACT_HYPOTHETICAL"].iloc[0]
assert abs(float(hyp.asset_coverage_pct)-49.38077154072405)<1e-9
assert float(hyp.asset_coverage_pct)<50

bna=pd.read_csv(p/"BNA_FY_AQ_CONTROL_V69.csv")
ind=bna[bna.basis=="SEPARATED_INDIVIDUAL"].iloc[0]
assert float(ind.income_bcra)==766170919.0
assert float(ind.income_otherfi)==0.0
assert float(ind.expense_bcra)==0.0
assert float(ind.expense_otherfi)==0.0
assert str(ind.q4_eligible).startswith("NO_")

four=pd.read_csv(p/"FOUR_LEG_PASS_PANEL_V69.csv")
# No consolidated row may be system eligible
eligible_col="system_panel_eligible_v69"
if eligible_col in four.columns:
    bad=four[(four.basis.astype(str).str.contains("CONSOLIDATED")) & (four[eligible_col].astype(str).str.upper().eq("YES"))]
    assert len(bad)==0

retr=pd.read_csv(p/"PUBLIC_BANK_SOURCE_RECOVERY_V69.csv")
rbna=retr[retr.entity=="Banco de la Nacion Argentina"].iloc[0]
assert "502" in str(rbna.binary_status)
assert str(rbna.q4_four_leg) in ("N/D","ND","nan")

priority=pd.read_csv(p/"PUBLIC_BANK_COVERAGE_PRIORITY_V69.csv")
assert abs(priority.increment_pp.sum()-38.119803692736404)<1e-9
assert (priority.flow_weighting_allowed=="NO").all()

ver=(p/"VEREDICTO_V69.md").read_text(encoding="utf-8")
for token in [
"CLOSED_PASS_NETWORK\n= NOT_ACHIEVED",
"SYSTEM_BCRA_NET_PASS_FLOW\n= N/D",
"IEF_7_7PP_BCRA_SHARE\n= N/D",
"DIRECT_HOUSEHOLD_TO_BANK_TRANSFER\n= NOT_IDENTIFIED",
"HTML_MODIFICATION\n= FORBIDDEN"
]:
    assert token in ver, token

print("QA PASS")
