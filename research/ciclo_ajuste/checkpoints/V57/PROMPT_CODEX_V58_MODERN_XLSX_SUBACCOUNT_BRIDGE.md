# PROMPT CODEX V58 — Modern XLSX / entity subaccount bridge

## Base
Usar V57 como base congelada. NO modificar HTML. NO volver a usar las series de `resultados mensuales` pre-2020 como si tuvieran observaciones 2023.

## V57 congelado

```text
LEGACY_MONTHLY_RESULTS_PUBLICATION_POST2020 = DISCONTINUED
POST2020_HOMOGENEOUS_ACCUMULATED_RESULTS_SOURCE = STRONG_SUPPORT
POST2020_BROAD_QUARTER_FLOW_RECONSTRUCTION = SUPPORTED_APPROXIMATELY
FROZEN_IEF_COMPONENT_PP_RECONCILIATION = NOT_IDENTIFIED_EXACTLY
PASSES_DIRECT_BCRA = 7.7 pp = 26.83%
UNRESOLVED_COUNTERPARTY = 21.0 pp = 73.17%
DIRECT_HOUSEHOLD_POINT_ESTIMATE = N/D
```

## Misión V58

1. Materializar bytes oficiales de, en orden:
   - `Infbanc0623.xlsx`
   - `Infbanc0923.xlsx`
   - `Infbanc1223.xlsx`
   - `InfBanc_Anexo.xlsx`
   - series XLSX del IEF II-2024
   - base abierta mensual por entidad si los anteriores no contienen subcuentas suficientes.
2. Guardar cada raw file + SHA256 antes de transformarlo.
3. Identificar hojas/rangos que alimentan los componentes analíticos:
   - ingresos por intereses;
   - primas por pases;
   - títulos c/ORI;
   - CER/CVS;
   - diferencias de cotización;
   - resultado monetario.
4. Recuperar Q3-2023 y Q4-2023 en la **misma definición y denominador** del IEF Table 2.
5. Reconciliar contra targets congelados +2.1, +7.7, +7.3, -0.2, +11.3 pp.
6. Sólo después intentar sub-splits por emisor/sector/contraparte.
7. Para hogar directo, exigir flujo devengado por préstamos a personas o sector equivalente; stock o tasa promedio no basta.

## Gates

- stock != flow
- broad P24 `Por Intereses` != IEF `Ingresos por intereses` salvo reconciliación
- issuer stock != securities result share
- counterparty != accounting mode
- Q4-2023 != post-10/12 puro
- gross component != net bank profit
- household contract existence != household share
- no invented raw hashes or silent source substitution

## Outputs mínimos

- `RAW_MODERN_XLSX_MANIFEST_V58.csv`
- `MODERN_SOURCE_SHEET_MAP_V58.csv`
- `IEF_COMPONENT_RECONCILIATION_V58.csv`
- `INTEREST_FLOW_SECTOR_BRIDGE_V58.csv`
- `SECURITIES_ISSUER_RESULT_BRIDGE_V58.csv`
- `FX_CER_PASSES_BRIDGE_V58.csv`
- `COUNTERPARTY_UPDATE_V58.csv`
- `AUDITORIA_V58.md`
- `VEREDICTO_V58.md`
- `EVIDENCE_LEDGER_CICLO_AJUSTE_V58.csv`
- `README_V58.md`
- `MANIFEST_V58.json`
- QA script

No tocar HTML.
