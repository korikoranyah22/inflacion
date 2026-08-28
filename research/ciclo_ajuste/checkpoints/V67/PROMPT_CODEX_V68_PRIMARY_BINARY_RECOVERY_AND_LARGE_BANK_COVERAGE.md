# PROMPT CODEX V68 — PRIMARY BINARY RECOVERY AND LARGE-BANK COVERAGE

Continue from V67. Do not reopen basis harmonization.

## Frozen V67 state

```text
SYSTEM_PANEL_BASIS = INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING
STRICT_Q4_FOUR_LEG_EXACT = ICBC + Banco de Valores + Banco Macro = 11.260968% bank assets
Q4_POINT_OTHERFI_DETAIL = exact three + Galicia = 20.230242% bank assets = OPEN_SUBSET
SUPERVIELLE = INDIVIDUAL_Q4_TOTAL_EXACT + COUNTERPARTY_BOUND
SANTANDER = OFFICIAL 3Q/4Q CONSOLIDATED+SEPARATED BINARIES LOCATED, VALUES NOT PARSED
SYSTEM_INTERBANK_PASS_CANCELLATION = N/D
IEF_7_7PP_BCRA_SHARE = N/D
```

## Mission A — recover high-value primary binaries

Priority:
1. Santander official 3T23/4T23 binaries already located. Use alternate retrieval/parser/CNV mirror; extract only the **separated** Annex Q.
2. Provincia 30-09-2023 separated Annex Q; FY exact already.
3. Credicoop 30-09-2023 separated Annex Q; FY exact already.
4. Nación separated 9M/FY Annex Q.
5. Ciudad individual/separated 9M/FY.
6. BBVA individual 9M/FY via issuer IR or CNV presentation links.
7. Supervielle direct 9M counterparty split.

## Mission B — exact bridge only

Use only compatible individual/separated 9M/FY pairs and frozen homogeneous-currency differencing. Do not substitute consolidated values when an individual file cannot be parsed.

## Mission C — network gate

Recompute retrieval coverage after every exact entity, but never weight flows by asset shares. Keep the system cancellation gate closed until coverage is materially near-full/closed.

## Mission D — exploit the sign-instability diagnostic

Preserve the V66→V67 open-exact-subset sign flip as a QA assertion: subset net signs are coverage-sensitive and are not system estimates.

## Frozen prohibitions
- consolidated != individual
- stock != flow
- asset share != flow weight
- open subset != system
- +7.7 pp != BCRA by assumption
- product/origination != accrued household interest
- no HTML

Create V68 package, QA, verdict, handover, and next prompt.
