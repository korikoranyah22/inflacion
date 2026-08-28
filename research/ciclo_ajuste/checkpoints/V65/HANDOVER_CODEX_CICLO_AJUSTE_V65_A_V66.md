# HANDOVER CODEX — Proyecto Ciclo del Ajuste Argentina 2002–2026
## Continuación desde V65 → ejecutar V66

**Fecha de corte:** 2026-08-27  
**Rama activa:** contrapartes / incidencia distributiva / flujos bancarios  
**Última iteración cerrada:** V65  
**Próxima:** `V66_INDIVIDUAL_AQ_RETRIEVAL_AND_CLOSED_NETWORK_EXPANSION`

## Qué resolvió V65

### Base sistémica
```text
SYSTEM_PANEL_BASIS
= INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING

CONSOLIDATED_GROUP_FILINGS
= CONTROL_ONLY_FOR_SYSTEM_PANEL
```

No volver a mezclar Ciudad/Macro/Santander/BBVA/Supervielle consolidados con ICBC/Galicia individuales para un test sistémico.

### Denominador oficial
```text
BANKS_ASSETS_DEC2023
= 96,697,695.5 million ARS
BANKS_DEPOSITS_DEC2023
= 62,483,328.1 million ARS
BANK_COUNT
= 63
```

Coverage is retrieval diagnostic only.

### Cobertura estricta actual
```text
FULL_FOUR_LEG_EXACT_Q4_TARGET_BASIS
= ICBC only
= 4.101042% bank assets

INDIVIDUAL_Q4_OTHERFI_DETAIL
= ICBC + Galicia
= 13.070316% bank assets
= OPEN SUBSET
```

ICBC+Galicia otherFI Q4:
```text
income = 6192393.115 thousand ARS
expense= 2366000.017 thousand ARS
net    = 3826393.098 thousand ARS
```
No system inference.

### Nuevo Banco Provincia FY
```text
BAPRO_FY2023_SEPARATED
income_BCRA    = 1,040,489,497
expense_BCRA   = 0
income_otherFI = 0
expense_otherFI= 2,428
unit = thousand ARS homogeneous
quality = EXACT

BAPRO_Q4 = N/D_9M_NOT_RETRIEVED
```

### Nuevo Credicoop FY
```text
CREDICOOP_FY2023_SEPARATED
income_BCRA    = 180,887,922
expense_BCRA   = 0
income_otherFI = 0
expense_otherFI= 0
unit = thousand ARS homogeneous
quality = EXACT

CREDICOOP_Q4 = N/D_9M_COMPATIBLE_PDF_NOT_RETRIEVED
```

### Household
BCRA has lending statistics by holder type and amounts operated, but no direct Annex-Q accrued-interest allocation was identified.

```text
HOUSEHOLD_ANNEX_Q_ACCRUED_INTEREST_FLOW_BRIDGE = NOT_IDENTIFIED
HOUSEHOLD_SYSTEM_Q4_POINT_ESTIMATE = N/D
DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED
```

## Gates still closed
```text
CLOSED_PASS_NETWORK = NOT_ACHIEVED
SYSTEM_INTERBANK_PASS_CANCELLATION = NOT_IDENTIFIED_COVERAGE_TOO_LOW
SYSTEM_BCRA_NET_PASS_FLOW = N/D
SYSTEM_INTERBANK_NET_PASS_FLOW = N/D
IEF_7_7PP_BCRA_SHARE = N/D
HTML_MODIFICATION = FORBIDDEN
```

## First action V66
Read:
1. `VEREDICTO_V65.md`
2. `AUDITORIA_V65.md`
3. `BASIS_HARMONIZATION_V65.csv`
4. `BCRA_BANK_SYSTEM_COVERAGE_V65.csv`
5. `FOUR_LEG_PASS_PANEL_V65.csv`
6. `BAPRO_FY_AQ_CONTROL_V65.csv`
7. `CREDICOOP_FY_AQ_CONTROL_V65.csv`
8. `CLOSED_NETWORK_NETTING_TEST_V65.csv`
9. `PROMPT_CODEX_V66_INDIVIDUAL_AQ_RETRIEVAL_AND_CLOSED_NETWORK_EXPANSION.md`

Then retrieve the missing **individual 9M Annex Q** documents. Do not revisit the accounting-basis decision unless contradicted by direct regulatory evidence.
