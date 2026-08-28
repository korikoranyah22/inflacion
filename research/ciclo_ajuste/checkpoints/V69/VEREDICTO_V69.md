# VEREDICTO V69 — PUBLIC BANK SOURCE PATH AND COVERAGE PRIORITY

```text
SYSTEM_PANEL_BASIS
= INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING

STRICT_Q4_FOUR_LEG_EXACT_TARGET_BASIS
= ICBC + Banco de Valores + Banco Macro
= 11.260968% bank assets

NEW_Q4_FOUR_LEG_EXACT_ENTITY
= NO

BNA_FY_INDIVIDUAL_ANNEX_Q
= EXACT_RECOVERED

BNA_FY_INDIVIDUAL_PASS
income_BCRA     = 766170919 thousand ARS
expense_BCRA    = 0
income_otherFI  = 0
expense_otherFI = 0

BNA_FY_CONSOLIDATED_OTHERFI_INCOME
= 3980009 thousand ARS
= CONTROL_ONLY

BNA_9M_SEPARATED_SOURCE
= OFFICIAL_AGN_PACKAGE_IDENTIFIED

BNA_9M_BINARY
= NOT_RECOVERED_CURRENT_502

BNA_Q4_FOUR_LEG
= N/D

BNA_BANK_ASSET_SHARE
= 22.015263%
= RETRIEVAL_PRIORITY_ONLY

STRICT_IF_BNA_Q4_EXACT_HYPOTHETICAL
= 33.276231%

BNA_PLUS_PROVINCIA_PLUS_CREDICOOP_PLUS_CIUDAD_ASSET_FOOTPRINT
= 38.119804%
= UNRESOLVED_TARGET_FOOTPRINT

STRICT_PLUS_ALL_FOUR_IF_EXACT_HYPOTHETICAL
= 49.380772%

CLOSED_PASS_NETWORK
= NOT_ACHIEVED

SYSTEM_INTERBANK_PASS_CANCELLATION
= NOT_IDENTIFIED_COVERAGE_TOO_LOW

SYSTEM_BCRA_NET_PASS_FLOW
= N/D

SYSTEM_INTERBANK_NET_PASS_FLOW
= N/D

IEF_7_7PP_BCRA_SHARE
= N/D

HOUSEHOLD_ANNEX_Q_ACCRUED_INTEREST_FLOW_BRIDGE
= NOT_IDENTIFIED

DIRECT_HOUSEHOLD_TO_BANK_TRANSFER
= NOT_IDENTIFIED

HTML_MODIFICATION
= FORBIDDEN
```

## Interpretación

V69 no agrega una nueva entidad Q4 four-leg exacta. Su avance es distinto: identifica y cuantifica el cuello de botella de mayor retorno y corrige/valida la base de Banco Nación con evidencia FY individual directa.

La diferencia observada entre el Schedule Q individual y consolidado de BNA refuerza la decisión de V65 de construir el panel sistémico únicamente sobre entidades individuales y neteos explícitos. No debe "reconciliarse" esa diferencia promediando bases.

El 9M separado de BNA no es hipotético: AGN documenta oficialmente el paquete correspondiente al 30/09/2023. El problema actual es recuperar el binario/attachment, que devuelve 502 en esta ruta. Hasta recuperar y auditar el Anexo Q no existe bridge Q4.

La prioridad V70 pasa a ser recuperación binaria de BNA 9M y, en paralelo, Provincia/Credicoop/Ciudad. Los activos sólo ordenan el esfuerzo de retrieval; no estiman la magnitud de los flujos.
