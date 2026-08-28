# Prompt Codex — V56 · extracción de valores de series BCRA y bridge NIIF 2023

## Estado congelado V55

```text
BCRA_SUBACCOUNT_SCHEMA = STRONG_SUPPORT
ES_SERIES_SCHEMA_BYTES = MATERIALIZED + SHA256 VERIFIED
2023_SUBACCOUNT_VALUES = NOT_MATERIALIZED
STRICT_DIRECT_COUNTERPARTY = 7.7 PP pases -> BCRA
UNRESOLVED_COUNTERPARTY = 21.0 PP
```

## Misión

Obtener observaciones mensuales Q3/Q4 2023 para las cuentas/subcuentas identificadas en V55 y demostrar compatibilidad contable con los buckets congelados.

### Prioridad A — valores de cuadro de resultados

Materializar `din1_ser.txt` o `baldethis.xls` y extraer, si existen y son continuas en 2023:

```text
1151-1162
1183-1192
```

Registrar bytes, SHA256 y cobertura. Si los códigos cambiaron post-NIIF, reconstruir equivalencias modernas usando `bolrel.xls`, layouts o metadata oficial; no empalmar por nombre.

### Prioridad B — reconciliación

Para Sep-2023 y Dec-2023 (y meses intermedios) probar:

- inversiones detalladas -> target securities +7.3 pp;
- intereses ganados detallados -> target interest-income +2.1 pp;
- legs indexados -> target CER -0.2 pp;
- resultados FX/forwards/swaps -> target FX +11.3 pp.

Primero reconciliar montos nominales/moneda homogénea/denominador; sólo después calcular gaps en pp.

### Prioridad C — sector/incidencia

Aun con valores, no asignar `1153` por hogares usando stocks salvo modelo explícito validado. Buscar cuentas de flujo por tipo de titular o, si no existen, dejar sector N/D.

## Prohibiciones

- no asumir continuidad de códigos 2021→2023;
- no usar stock como resultado;
- no usar +2.1 como ceiling sectorial;
- no llamar +11.3 valuación completa;
- no mezclar contraparte y modo contable;
- no tocar HTML.

## Output

- `SERIES_VALUE_BYTES_MANIFEST_V56.csv`
- `ACCOUNT_EQUIVALENCE_NIIF_V56.csv`
- `MONTHLY_SUBACCOUNT_VALUES_2023_V56.csv`
- `TARGET_RECONCILIATION_V56.csv`
- `COUNTERPARTY_UPDATE_V56.csv`
- `AUDITORIA_V56.md`
- `VEREDICTO_V56.md`
- ledger, README, manifest, QA.
