# PROMPT CODEX V67 — LARGE-BANK 9M RETRIEVAL AND COVERAGE SCALE-UP

Continue from V66. Do not reopen basis harmonization.

## Frozen V66 state

```text
SYSTEM_PANEL_BASIS = INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING

STRICT_Q4_FOUR_LEG_EXACT
= ICBC + Banco de Valores
= 5.2096% bank assets

Q4_POINT_OTHERFI_DETAIL
= ICBC + Banco de Valores + Galicia
= 14.178874% bank assets
= OPEN_SUBSET

SUPERVIELLE
= INDIVIDUAL_Q4_TOTAL_EXACT + COUNTERPARTY_BOUND

SYSTEM_INTERBANK_PASS_CANCELLATION = N/D
IEF_7_7PP_BCRA_SHARE = N/D
```

## Mission A — maximize marginal coverage

Priority:
1. Banco Provincia 30-09-2023 separated Annex Q — FY exact already exists.
2. Banco Credicoop 30-09-2023 separated Annex Q — FY exact already exists.
3. Banco Nación separated 9M/FY Annex Q.
4. Banco Ciudad individual/separated 9M/FY.
5. Banco Macro individual/separated 9M/FY.
6. Santander Argentina individual/separated 9M/FY.
7. BBVA Argentina individual/separated 9M/FY.
8. Supervielle direct 9M counterparty split, if an Annex Q or regulatory table exists, to collapse the bound to a point.

Do not spend the main retrieval budget on small additional banks until these high-asset entities are exhausted/documented.

## Mission B — exact Q4 bridge

Use only compatible individual 9M/FY pairs and frozen homogeneous-currency differencing. Keep EXACT / BOUND / APPROX / N-D distinct.

## Mission C — network gate

Recompute asset retrieval coverage after each entity, but never weight or scale pass flows by assets.

Do not test system interbank cancellation until coverage is materially near-closed.

## Mission D — source hierarchy

Prefer BCRA/official issuer/official audit filings. A regulator-origin filing mirror can support exact transcription if the original filing is unambiguously reproduced, but document the source hierarchy caveat and seek a primary duplicate when practical.

## Frozen prohibitions
- consolidated != individual
- stock != flow
- asset share != flow weight
- open subset != system
- +7.7 pp != BCRA by assumption
- product/origination != accrued household interest
- no HTML

Create V67 package, QA, verdict, handover, and next prompt.
