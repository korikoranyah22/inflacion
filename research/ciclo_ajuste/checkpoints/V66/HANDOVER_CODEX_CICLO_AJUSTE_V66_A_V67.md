# HANDOVER CODEX — Proyecto Ciclo del Ajuste Argentina 2002–2026
## Continuación desde V66 → ejecutar V67

**Fecha de corte:** 2026-08-27  
**Rama activa:** contrapartes / incidencia distributiva / flujos bancarios  
**Última iteración cerrada:** V66  
**Próxima:** `V67_LARGE_BANK_9M_RETRIEVAL_AND_COVERAGE_SCALEUP`

## Estado congelado

```text
SYSTEM_PANEL_BASIS
= INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING

BCRA_BANK_ASSETS_DEC2023
= 96,697,695.5 million ARS

FULL_FOUR_LEG_EXACT_Q4_TARGET_BASIS
= ICBC + Banco de Valores
= 2 entities
= 5.2096% bank assets

POINT_Q4_OTHERFI_DETAIL
= ICBC + Banco de Valores + Galicia
= 14.178874% bank assets
= OPEN_SUBSET

SUPERVIELLE_Q4
= TOTAL_EXACT_COUNTERPARTY_BOUND

CLOSED_PASS_NETWORK = NOT_ACHIEVED
SYSTEM_INTERBANK_PASS_CANCELLATION = NOT_IDENTIFIED_COVERAGE_TOO_LOW
SYSTEM_BCRA_NET_PASS_FLOW = N/D
SYSTEM_INTERBANK_NET_PASS_FLOW = N/D
IEF_7_7PP_BCRA_SHARE = N/D
HOUSEHOLD_ANNEX_Q_ACCRUED_INTEREST_FLOW_BRIDGE = NOT_IDENTIFIED
DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED
HTML_MODIFICATION = FORBIDDEN
```

## Nuevo exacto Banco de Valores

```text
Q4 income BCRA     = 132269429.624
Q4 expense BCRA    = 0
Q4 income otherFI  = 47920.656
Q4 expense otherFI = 204552.353
Q4 net BCRA        = 132269429.624
Q4 net otherFI     = -156631.697
unit = thousand ARS Dec-2023 homogeneous
```

## Supervielle

```text
Q4 total pass income  = 86713401.666
Q4 total pass expense = 591120.907
income BCRA bound     = [83427561.666, 86713401.666]
income otherFI bound  = [0, 3,285,840]
expense BCRA          = 0
expense otherFI       = 591120.907
```

No point-identify the income split until direct 9M counterparty disclosure is found.

## Retrieval priority V67

1. Provincia 9M — FY already exact.
2. Credicoop 9M — FY already exact.
3. Nación separated 9M/FY.
4. Ciudad individual.
5. Macro individual.
6. Santander individual.
7. BBVA individual.
8. Direct Supervielle 9M split.

The next bottleneck is **coverage scale**, not accounting-basis design.

Read first: `VEREDICTO_V66.md`, `AUDITORIA_V66.md`, `INDIVIDUAL_AQ_RETRIEVAL_V66.csv`, `BANCO_VALORES_Q4_AQ_BRIDGE_V66.csv`, `SUPERVIELLE_Q4_PASS_BOUND_V66.csv`, `BCRA_BANK_SYSTEM_COVERAGE_V66.csv`, `CLOSED_NETWORK_NETTING_TEST_V66.csv`, then the V67 prompt.
