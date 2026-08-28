# AUDITORÍA V62 — Machine-readable entity result aggregation

V62 conserva los gates de V61 y amplía cobertura sin reinstalar identidades descartadas.

## Cobertura
- Q4 broad interest: 6 entidades.
- Household-like Q4: 5 entidades.
- Submuestra estricta consolidada para household-like: Macro + Ciudad + BBVA + Supervielle.

## Household-like
BBVA Q4: ARS 119.515 bn / broad 879.638 bn = 13.5868%.
Supervielle Q4: ARS 46.506 bn / broad 339.238 bn = 13.7090%.
Submuestra consolidada: 17.7546% del broad interest. DESCRIPTIVE_ONLY; no es sistema ni sector hogar estricto.

## Santander pass bound
Q4 total pass income reconstruido = ARS 202.636 bn. FY BCRA pass income = ARS 6.246 bn.
Por no negatividad de la subcuenta bruta, BCRA Q4 <= FY BCRA, por lo que BCRA share Q4 <= 3.0825% y other-FI share Q4 >= 96.9175%. ENTITY_LEVEL_ONLY.

## BBVA
Broad interest Q4 = ARS 879.638 bn; household-like = ARS 119.515 bn; pass income total = ARS 160.569 bn. Counterparty split N/D.

## Supervielle
La línea Other agrupa títulos BCRA + repo + otros títulos; no permite aislar pases.

## Interbank cancellation
Observed other-FI pass income lower bound = ARS 573.983 bn, pero las patas de egreso comparables están casi ausentes. No inferir no-cancelación.

## IEF
No reconciliar pesos de muestra con +7.7pp sin numerador sistémico, netting y denominador compatibles. `IEF_7_7PP_BCRA_SHARE=N/D`.
