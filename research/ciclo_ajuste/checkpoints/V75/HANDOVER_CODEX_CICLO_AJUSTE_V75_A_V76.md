# HANDOVER CODEX — Proyecto Ciclo del Ajuste Argentina 2002–2026
## Continuación V75 → V76

**Fecha de corte:** 2026-08-28

## Estado congelado

```text
STRICT_Q4_FOUR_LEG_EXACT = ICBC + Banco de Valores + Banco Macro + Banco Credicoop
STRICT_Q4_FOUR_LEG_EXACT_COVERAGE = 14.564124643487% bank assets
CREDICOOP_30_09_2023_BINARY = RECOVERED_AND_ARCHIVED
CREDICOOP_9M_ALTERNATE_PASS_DISCLOSURE = EXACT_CROSSWALK_TO_FY_ANNEX_Q
CREDICOOP_Q4_FOUR_LEG = EXACT
BNA_9M_FULL_SEPARATED_PAYLOAD = NOT_ESTABLISHED
BAPRO_9M_TARGET = PENDING
CIUDAD_9M_INDIVIDUAL_TARGET = PENDING
BCRA_202309_OPEN_DATA_7Z = ENDPOINT_UNRESOLVED
HTML_MODIFICATION = FORBIDDEN
```

## Prioridad V76

1. BNA: recuperar filing separado 30/09/2023 o disclosure primario alternativo de pases por contraparte.
2. BAPRO: recuperar 9M separado/individual.
3. Ciudad: buscar equivalente individual al consolidado ya controlado.
4. Continuar resolución verificable del `.7z` BCRA; no adivinar endpoints.
5. Aplicar el mismo patrón Credicoop: una Note 6/nota equivalente puede sustituir Q si su taxonomía se reconcilia exactamente contra FY.

## Fórmula congelada

`Q4_Dec = FY_Dec - 9M_Sep * 1.532908152197492`
