# PROMPT CODEX V69 — ALTERNATE INTERIM AQ SOURCE AND PUBLIC-BANK SCALEUP

Continue from V68. Do not reopen basis harmonization.

## Frozen state

```text
SYSTEM_PANEL_BASIS = INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING
STRICT_Q4_FOUR_LEG_EXACT = ICBC + Banco de Valores + Banco Macro = 11.260968% bank assets
SANTANDER_9M_PRIMARY = RECOVERED, ANNEX_Q_NOT_PRESENT
SANTANDER_Q4_TOTAL_PASS_INCOME = 200412599.134366 thousand ARS Dec-2023
SANTANDER_Q4_BCRA_INCOME_SHARE >= 99.988548624% CONDITIONAL ENTITY BOUND
SANTANDER_Q4_FOUR_LEG = N/D because 9M expense/counterparty split is missing
SYSTEM_INTERBANK_PASS_CANCELLATION = N/D
IEF_7_7PP_BCRA_SHARE = N/D
```

## Mission A — switch disclosure path

Do not retry the same Santander 9M filing. Search BCRA regulatory attachments/data, issuer supplemental filings, or other primary regulatory channels for an interim Annex Q that may have been submitted separately.

## Mission B — high-mass public/cooperative banks

Priority:
1. Banco Provincia 30-09-2023 separated Annex Q (FY exact already).
2. Credicoop 30-09-2023 separated Annex Q (FY exact already).
3. Banco Nación separated 9M/FY Annex Q.
4. Banco Ciudad individual/separated 9M/FY.
5. BBVA individual via BCRA/issuer route rather than CNV consolidated parent-bank filing.

## Mission C — exact/conditional gates

- Exact four-leg requires all four pass flow legs on compatible individual basis.
- Bounds must state every sign/nonnegativity assumption.
- Do not infer flow counterparties from stock.
- Do not combine consolidated Santander bound with individual Santander bound.
- Asset share is retrieval coverage only, never flow weight.

## Mission D — system gate

Keep system netting closed until network coverage is materially near-full/closed. Preserve the V66→V67 exact-open-subset sign flip as QA evidence.

## Frozen prohibitions
- consolidated != individual
- stock != flow
- open subset != system
- +7.7 pp != BCRA by assumption
- product/origination != accrued household interest
- Q4 != clean post-10/12
- no HTML

Create V69 package, QA, verdict, handover, and next prompt.
