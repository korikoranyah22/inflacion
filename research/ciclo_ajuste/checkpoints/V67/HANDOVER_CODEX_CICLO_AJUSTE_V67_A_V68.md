# HANDOVER CODEX — Proyecto Ciclo del Ajuste Argentina 2002–2026
## Continuación desde V67 → ejecutar V68

**Fecha de corte:** 2026-08-27  
**Rama activa:** contrapartes / incidencia distributiva / flujos bancarios  
**Última iteración cerrada:** V67  
**Próxima:** `V68_PRIMARY_BINARY_RECOVERY_AND_LARGE_BANK_COVERAGE`

## Estado congelado

```text
SYSTEM_PANEL_BASIS
= INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING

BCRA_BANK_ASSETS_DEC2023
= 96,697,695.5 million ARS

FULL_FOUR_LEG_EXACT_Q4_TARGET_BASIS
= ICBC + Banco de Valores + Banco Macro
= 3 entities
= 11.260968% bank assets

POINT_Q4_OTHERFI_DETAIL
= ICBC + Banco de Valores + Banco Macro + Galicia
= 20.230242% bank assets
= OPEN_SUBSET

SUPERVIELLE_Q4
= TOTAL_EXACT_COUNTERPARTY_BOUND

SANTANDER_PRIMARY_3Q_4Q_PAIR
= OFFICIAL_CONSOLIDATED_AND_SEPARATED_BINARIES_LOCATED
= PARSER_BLOCKED

CLOSED_PASS_NETWORK = NOT_ACHIEVED
SYSTEM_INTERBANK_PASS_CANCELLATION = NOT_IDENTIFIED_COVERAGE_TOO_LOW
SYSTEM_BCRA_NET_PASS_FLOW = N/D
SYSTEM_INTERBANK_NET_PASS_FLOW = N/D
IEF_7_7PP_BCRA_SHARE = N/D
HOUSEHOLD_ANNEX_Q_ACCRUED_INTEREST_FLOW_BRIDGE = NOT_IDENTIFIED
DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED
HTML_MODIFICATION = FORBIDDEN
```

## Nuevo exacto Banco Macro

```text
Q4 income BCRA      = 61675202.827
Q4 expense BCRA     = 0
Q4 income otherFI   = 5729593.580
Q4 expense otherFI  = 2502560.286
Q4 net BCRA         = 61675202.827
Q4 net otherFI      = 3227033.294
unit = thousand ARS Dec-2023 homogeneous
```

Macro assets = 5,851,533.4 million ARS = 6.051368% of banks.

## Exact-open-subset sign test

```text
ICBC + Banco Valores exact net otherFI
= -1,058,668.831

ICBC + Banco Valores + Banco Macro exact net otherFI
= 2168364.463
```

The sign flips with coverage. Preserve this as evidence that an open subset cannot characterize system cancellation.

## Retrieval priority V68

1. Santander: recover/parse the already located official 3T23 and 4T23 consolidated+separated binaries; extract only separated Annex Q.
2. Banco Provincia 9M: FY exact already.
3. Credicoop 9M: FY exact already.
4. Banco Nación separated 9M/FY Annex Q.
5. Banco Ciudad individual/separated 9M/FY.
6. BBVA Argentina individual 9M/FY via CNV/IR.
7. Supervielle direct 9M counterparty split if found.

Do not spend the main retrieval budget on small banks while these large blocks remain unresolved.

## Frozen rules

- consolidated != individual
- stock != flow
- asset share != flow weight
- open subset != system
- Q4 != clean post-10/12
- +7.7 pp != BCRA by assumption
- product/origination != accrued household interest
- no HTML

Read first `VEREDICTO_V67.md`, `AUDITORIA_V67.md`, `MACRO_Q4_AQ_BRIDGE_V67.csv`, `BCRA_BANK_SYSTEM_COVERAGE_V67.csv`, `CLOSED_NETWORK_NETTING_TEST_V67.csv`, then the V68 prompt.
