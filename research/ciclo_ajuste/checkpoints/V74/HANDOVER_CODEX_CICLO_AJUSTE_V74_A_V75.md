# HANDOVER CODEX — Proyecto Ciclo del Ajuste Argentina 2002–2026
## Continuación V74 → V75

**Fecha de corte:** 2026-08-28

## Estado congelado

```text
STRICT_Q4_FOUR_LEG_EXACT = ICBC + Banco de Valores + Banco Macro
STRICT_Q4_FOUR_LEG_EXACT_COVERAGE = 11.260968% bank assets
BCRA_202309_ENTITY_LEVEL_CONTROL = RECOVERED_FOR_CREDICOOP_CIUDAD_BNA_BAPRO
BCRA_202309_OPEN_DATA_7Z = ENDPOINT_UNRESOLVED
CREDICOOP_30_09_2023_PUBLICATION = PRIMARY_INDEX_CONFIRMED
CREDICOOP_30_09_2023_BINARY = PENDING
CIUDAD_9M_CONSOLIDATED_ANNEX_Q = CONTROL_ONLY_VERIFIED
BNA_9M_FULL_SEPARATED_PAYLOAD = NOT_ESTABLISHED
BAPRO_9M_TARGET = PENDING
HTML_MODIFICATION = FORBIDDEN
```

## Prioridad V75

1. Si Miyu aporta Credicoop 30-09-2023: preservar binario, fingerprint, inspeccionar basis y disclosure de pases.
2. Resolver sin adivinar el endpoint histórico BCRA `.7z` de septiembre 2023; inspeccionar diccionario y TXT para campos que puedan mapear a pases/contrapartes.
3. Continuar BNA/BAPRO/Ciudad sólo con fuentes individuales/separadas compatibles.
4. Si aparece 9M compatible con FY, aplicar el bridge y QA de cuatro patas.

## Fórmula permitida

`Q4_Dec = FY_Dec - 9M_Sep * 1.532908152197`

Sólo con misma entidad, basis, definición y unidad.
