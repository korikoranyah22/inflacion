# HANDOVER CODEX — Proyecto Ciclo del Ajuste Argentina 2002–2026
## Continuación desde V73 → V74

**Fecha de corte:** 2026-08-28
**Último checkpoint:** V73

## Estado congelado

```text
STRICT_Q4_FOUR_LEG_EXACT = ICBC + Banco de Valores + Banco Macro
STRICT_Q4_FOUR_LEG_EXACT_COVERAGE = 11.260968% bank assets
ANNEX_Q_9M_MANDATORY_GATE = REMOVED
CREDICOOP_30_09_2023_PUBLICATION = PRIMARY_INDEX_CONFIRMED
CREDICOOP_30_09_2023_BINARY = PENDING
BANCO_CIUDAD_9M_CONSOLIDATED = CONTROL_ONLY
BANCO_CIUDAD_9M_SEPARATED = NOT_RECOVERED
BNA_9M_AGN_ATTACHMENTS = RECOVERED_LOCAL
BNA_9M_FULL_SEPARATED_PAYLOAD = NOT_ESTABLISHED
BAPRO_9M_TARGET = PENDING
HTML_MODIFICATION = FORBIDDEN
```

## Prioridad V74

1. Si Miyu aporta Credicoop 30-09-2023: fingerprint, preservar binario, inspeccionar filing completo y extraer sólo disclosure compatible.
2. Si el filing Credicoop contiene cuatro patas 9M compatibles con FY, calcular Q4 homogéneo y correr QA/cobertura.
3. Si no, continuar ruta BNA/BCRA machine-readable y BAPRO separado 9M.
4. Ciudad sólo puede entrar al panel estricto con base individual/separada compatible; consolidado queda como control.

## Fórmula permitida

`Q4_Dec = FY_Dec - 9M_Sep * 1.532908152197`

Aplicar únicamente con misma base, definiciones y unidad monetaria.
