# PROMPT CODEX V62 — Machine-readable entity result aggregation

Continue from V61 without reopening V34–V60.

## Objective
Obtain a homogeneous high-coverage entity panel for Sep/FY 2023 Anexo Q or equivalent machine-readable disclosures and aggregate Q4 flows by exact code/definition.

## Must solve
1. Add Santander, BBVA, Provincia, Credicoop, ICBC, Supervielle and Nación Q3 if available.
2. Keep consolidation basis explicit; do not sum individual and consolidated statements silently.
3. For passes aggregate four flows separately: income BCRA, expense BCRA, income other-FI, expense other-FI.
4. Test whether interbank other-FI net flow approaches zero at high coverage and reconcile to IEF pass-premia component.
5. Aggregate mortgages, pledged, personal and cards only as PRODUCT_PROXY; search for a true sector-household mapping separately.
6. Measure coverage by a homogeneous denominator only (assets or broad interest on same basis). If impossible, coverage remains N/D.

## Gates
- Do not reinstate 7.7pp=BCRA.
- Do not use year-end pass stocks as period-flow proxies.
- Do not treat public-securities interest as Treasury without issuer identity.
- Do not make a household→bank transfer claim from sample ratios.
- Do not modify HTML.

## Outputs
ENTITY_COVERAGE_V62.csv
ENTITY_Q4_AQ_PANEL_V62.csv
PASS_GROSS_NET_SYSTEM_V62.csv
INTERBANK_CANCELLATION_TEST_V62.csv
HOUSEHOLD_PRODUCT_SYSTEM_V62.csv
IEF_PASS_RECONCILIATION_V62.csv
COUNTERPARTY_UPDATE_V62.csv
AUDITORIA_V62.md
VEREDICTO_V62.md
EVIDENCE_LEDGER_CICLO_AJUSTE_V62.csv
README_V62.md
MANIFEST_V62.json
QA script
