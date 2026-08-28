# PROMPT CODEX V59 — Entity-level real-margin / positive-income bridge

## Base congelada V58
No modificar HTML.

```text
EXACT_IEF_Q3_Q4_COMPONENT_TABLE = PASS
P24_INTEREST_INCOME_DIRECT_MAPPING = REJECTED
P24_INTEREST_EXPENSE_DIRECT_MAPPING = APPROX_SUPPORTED
P24_MONETARY_RESULT_DIRECT_MAPPING = APPROX_SUPPORTED
P24_ADMIN_EXPENSE_DIRECT_MAPPING = APPROX_SUPPORTED
PASSES_DIRECT_BCRA = 7.7 pp = 26.83%
UNRESOLVED_COUNTERPARTY = 21.0 pp = 73.17%
DIRECT_HOUSEHOLD_POINT_ESTIMATE = N/D
```

## Hallazgo que debe preservarse
El P24 broad `Ingresos financieros - Por Intereses` implica un denominador ~3.3-3.4 veces el denominador que surge consistentemente de egresos por intereses, resultado monetario y administración. No sustituir P24 `Por Intereses` por IEF `Ingresos por intereses`.

## Misión V59
1. Encontrar la fórmula/mapeo que construye el lado positivo del `Margen financiero integral real` del IEF.
2. Priorizar:
   - raw `Series de Datos` / anexo histórico si pueden materializarse;
   - régimen informativo / plan de cuentas post-NIIF;
   - base mensual por entidad y subcuentas de resultados;
   - documentación metodológica de moneda homogénea y reclasificaciones.
3. Explicar dónde se separan desde el broad P24:
   - intereses convencionales;
   - CER/CVS;
   - primas por pases;
   - títulos c/ORI;
   - diferencias de cotización;
   - otros financieros.
4. Reproducir como control al menos 3 componentes del IEF Q3/Q4 2023 con un mismo activo neteado medio.
5. Recién después buscar sector:
   - hogares;
   - empresas;
   - sector público;
   - BCRA;
   - depositantes.
6. Para hogares exigir flujo devengado por préstamos a personas/familias compatible con la línea IEF.

## Gates
- no residual = componente identificado;
- no stock × tasa = ingreso salvo identidad contractual y timing compatible;
- no usar `Por Intereses` P24 como IEF interest income;
- no usar stock de títulos para repartir resultado por títulos;
- counterparty != accounting mode;
- Q4-23 != post-10/12 puro;
- gross component != net profit;
- no hashes inventados.

## Outputs
- POSITIVE_FINANCIAL_INCOME_FORMULA_V59.csv
- POST_NIIF_SUBACCOUNT_MAP_V59.csv
- COMMON_DENOMINATOR_RECONCILIATION_V59.csv
- INTEREST_ACCRUED_SECTOR_FLOW_V59.csv
- SECURITIES_RESULT_ISSUER_FLOW_V59.csv
- FX_CER_PASSES_FLOW_V59.csv
- COUNTERPARTY_UPDATE_V59.csv
- AUDITORIA_V59.md
- VEREDICTO_V59.md
- EVIDENCE_LEDGER_CICLO_AJUSTE_V59.csv
- README_V59.md
- MANIFEST_V59.json
- QA
