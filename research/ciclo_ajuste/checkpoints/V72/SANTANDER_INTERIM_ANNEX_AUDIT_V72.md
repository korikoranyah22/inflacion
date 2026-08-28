# SANTANDER INTERIM ANNEX AUDIT — V68

## Resultado

```text
SANTANDER_9M_PRIMARY_INDIVIDUAL = RECOVERED
SANTANDER_9M_ANNEX_Q = NOT_PRESENT_IN_RECOVERED_FILING
SANTANDER_9M_PASS_INTEREST_TOTAL = 100,510,106 thousand ARS Sep-2023 homogeneous
SANTANDER_FY_ANNEX_Q = RECOVERED_EXACT
SANTANDER_Q4_TOTAL_PASS_INCOME = 200,412,599.134366 thousand ARS Dec-2023 constant
SANTANDER_Q4_FOUR_LEG = NOT_IDENTIFIED
```

## Qué se observó directamente

El filing individual intermedio al 30/09/2023 identifica los anexos O, P y R, pero no Q. La Nota 26.1 sí informa el total acumulado de ingresos por operaciones de pase: 100,510,106 miles de pesos.

El filing individual FY 2023 contiene Anexo Q y abre el ingreso anual por pases en BCRA y otras entidades financieras.

## Bridge permitido

Se usa sólo el total de ingreso por pase, que existe en ambos períodos:

```text
Q4 total income
= FY total income
- 9M total income × IPC_Dec/IPC_Sep
= 354,485,360
- 100,510,106 × 1.532908152197
= 200,412,599.134366
```

No se usa el stock de pases al 30/09 ni la Nota 7 para asignar contraparte del flujo.

## Bound condicional de contraparte del ingreso

El FY completo informa sólo 22,950 miles de pesos de ingreso por pases contra otras entidades financieras. Bajo la condición explícita de que los subflujos acumulados de ingreso por contraparte no sean negativos:

```text
Q4 otherFI income ∈ [0 ; 22,950]
Q4 BCRA income    ∈ [200,389,649.134366 ; 200,412,599.134366]
BCRA share        ∈ [99.988548624% ; 100%]
otherFI share     ∈ [0% ; 0.011451376%]
```

Esto es un `ENTITY_LEVEL_INCOME_BOUND`, no un punto exacto y no un bound del sistema.

## Lo que sigue faltando

El 9M no abre específicamente el egreso por pases ni su contraparte. Por ello no se identifica Q4 `expense_BCRA`, `expense_otherFI`, `net_BCRA` ni `net_otherFI`. Santander no entra al conjunto four-leg exacto.


## Reinterpretación V72
BCRA A 7809 fija A-Q con frecuencia anual. La ausencia de Q en el filing 9M deja de ser una rareza/retrieval gap y pasa a ser consistente con la arquitectura regulatoria. El bound Q4 ya construido a partir del total de pases 9M sigue siendo válido bajo sus supuestos, pero no crea el split de cuatro patas.
