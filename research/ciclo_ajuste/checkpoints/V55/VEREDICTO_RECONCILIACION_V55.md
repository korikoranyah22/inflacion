# Veredicto V55 — subcuentas identificadas, valores todavía no materializados

## Estado

```text
BCRA_SUBACCOUNT_DICTIONARY = MATERIALIZED_FROM_USER_REPO_CACHE
BCRA_SUBACCOUNT_SCHEMA = STRONG_SUPPORT
2023_SUBACCOUNT_VALUES = NOT_MATERIALIZED
SHA256_GATE_ES_SERIES_SCHEMA = PASS
SHA256_GATE_RESULT_VALUES = FAIL

SECURITIES_TARGET_RECONCILIATION = NOT_RUN_VALUES_MISSING
INTEREST_SECTOR_RECONCILIATION = NOT_RUN_VALUES_MISSING
CER_GROSS_RECONCILIATION = NOT_RUN_VALUES_MISSING
FX_MODE_NUMERIC_RECONCILIATION = NOT_RUN_VALUES_MISSING

BCRA_DIRECT_COUNTERPARTY_FLOOR = 7.7 PP
BCRA_DIRECT_COUNTERPARTY_FLOOR_SHARE = 26.83%
Q4_2023_UNRESOLVED_COUNTERPARTY_MASS = 21.0 PP
Q4_2023_UNRESOLVED_COUNTERPARTY_SHARE = 73.17%

DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED_AT_ABNORMAL_GAP_LEVEL
NET_CAUSAL_BANK_BENEFIT = NOT_IDENTIFIED
```

## Avance nuevo

V55 recupera del GitHub un archivo que V54 no había explotado: el catálogo `es_series.txt`. Ese catálogo identifica el diseño de cuentas del archivo de detalle del BCRA. En particular:

- `1153`: intereses ganados por préstamos, incluyendo actualización de capital con cláusula de ajuste;
- `1154`: primas ganadas por pases activos;
- `1155`: primas ganadas por ventas de moneda extranjera a futuro;
- `1158`: intereses pagados por depósitos, incluyendo actualización de capital con cláusula de ajuste;
- `1159`: primas pagadas por pases pasivos;
- `1185`: resultado neto por inversiones en títulos públicos;
- `1192`: otros resultados netos, incluyendo venta y actualización mensual de activos/pasivos FX, forwards liquidables en pesos y swaps de tasa.

Esto demuestra que **sí existe una arquitectura contable más granular** que los buckets del Informe sobre Bancos. Pero el catálogo sólo describe las cuentas: faltan los valores mensuales 2023.

## Implicación metodológica

La granularidad recuperada no resuelve automáticamente la incidencia:

1. `1153` separa préstamos de otros ingresos, pero no hogares de empresas/sector público y además mezcla interés con indexación.
2. `1185` separa una familia de títulos públicos, pero mezcla renta, diferencias de cotización, actualización, ventas y previsión; no separa Tesoro nacional, provincias ni BCRA.
3. `1192` confirma que el resultado FX puede mezclar remeasurement, compraventa y derivados.
4. Por tanto, stock por sector/emisor sigue sin poder usarse como share de resultado.

## Veredicto

V55 no aumenta el 26,83% de masa con contraparte estrictamente identificada. Sí reduce la incertidumbre sobre **qué datos exactos hacen falta** para romper los N/D: las observaciones mensuales de las subcuentas identificadas y un bridge de equivalencias contables compatible con 2023/NIIF.
