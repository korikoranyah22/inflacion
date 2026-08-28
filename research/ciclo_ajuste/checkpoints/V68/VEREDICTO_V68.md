# VEREDICTO V68 — PRIMARY RECOVERY AND DISCLOSURE GAP

```text
SYSTEM_PANEL_BASIS
= INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING

SANTANDER_PRIMARY_9M_INDIVIDUAL
= RECOVERED

SANTANDER_PRIMARY_FY_INDIVIDUAL
= RECOVERED

SANTANDER_9M_ANNEX_Q
= NOT_PRESENT_IN_RECOVERED_FILING

SANTANDER_FY_ANNEX_Q
= EXACT_RECOVERED

SANTANDER_Q4_TOTAL_PASS_INCOME
= 200412599.134366 thousand ARS Dec-2023 constant

SANTANDER_Q4_BCRA_PASS_INCOME_SHARE
>= 99.988548624%
= CONDITIONAL_ENTITY_LEVEL_BOUND

SANTANDER_Q4_OTHERFI_PASS_INCOME_SHARE
<= 0.011451376%
= CONDITIONAL_ENTITY_LEVEL_BOUND

SANTANDER_Q4_FOUR_LEG
= NOT_IDENTIFIED_EXPENSE_SPLIT_MISSING

STRICT_Q4_FOUR_LEG_EXACT_TARGET_BASIS
= ICBC + Banco de Valores + Banco Macro
= 11.260968% bank assets

Q4_INDIVIDUAL_PASS_INCOME_BOUND_FOOTPRINT
= ICBC + Valores + Macro + Galicia + Supervielle + Santander
= 31.146102% bank assets
= NOT_NETTABLE_NETWORK_COVERAGE

BBVA_PARENT_BANK_INDIVIDUAL_PAIR_ON_CNV_ROUTE
= NOT_LOCATED

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

V68 no agrega una cuarta entidad four-leg exacta, pero transforma Santander de un problema de parser en un problema documental bien identificado. Recupera además un bound **individual** de ingreso por contraparte extremadamente estrecho, sin usar stocks.

El contraste con el viejo control consolidado es importante: bases distintas pueden producir composiciones de contraparte radicalmente distintas. No reconciliar ni promediar ambas. Para la red sistémica se conserva sólo la base individual regulatoria.

La frontera V69 es ahora buscar **fuentes regulatorias alternativas del Anexo Q intermedio** (BCRA/attachments separados) y concentrar la recuperación en Provincia, Credicoop, Nación, Ciudad y BBVA, sin reintentar indefinidamente el mismo filing Santander que ya sabemos que omite Q.
