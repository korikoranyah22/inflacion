# Prompt Codex — V54 · ingestión de microdatos BCRA y bridge contable por sector/emisor

## Estado V53 congelado

```text
COUNTERPARTY_QUANTIFICATION
= PARTIALLY_IDENTIFIED_WITH_BOUNDS

Q4_2023_STRICT_CLASSIFIED_MASS
= 66.20%

Q4_2023_MIXED_ND_REMAINDER
= 33.80%

BCRA_DIRECT_FLOOR
= 26.83%

MARKET_VALUATION_FLOOR
= 39.37%

HOUSEHOLD_DIRECT_POINT_ESTIMATE
= N/D

HOUSEHOLD_STRICT_ISOLATED_BUCKET
= [0, 2.1 pp]
```

No reinterpretar estos porcentajes como utilidad neta ni efecto causal post-10/12.

## Misión V54

Dejar de trabajar con exposición agregada como proxy y recuperar los **bytes oficiales** necesarios para construir bridges contables compatibles.

### 1. Ingesta oficial BCRA

Descargar, versionar y calcular SHA256 de las series oficiales de:

- préstamos y depósitos privados por tipo de titular;
- préstamos/depósitos del sector público por jurisdicción;
- tenencias de títulos públicos por jurisdicción/emisor;
- series mensuales UVA;
- Series de Datos / Anexo Estadístico de Informes sobre Bancos 2014, 2018 y 2023;
- si está disponible, cuentas/estados que permitan separar ingresos por intereses por línea o sector.

Guardar raw bytes sin alterar.

### 2. Securities bridge

Para cada ventana compatible:

```text
2014 FY vs FY
2018 H1 vs H1
2023 Q4 vs Q3
```

intentar separar:

```text
BCRA instruments
Treasury national
provincial/municipal
private securities
coupon/accrual
sale result
mark-to-market
ORI
```

Gate:

```text
issuer stock != result share
```

Sólo asignar pp si existe un bridge de resultado compatible.

### 3. Interest-income bridge

Separar, si los datos lo permiten:

```text
personas humanas
personas jurídicas
sector público
otros
```

Ruta alternativa aceptable si no hay cuenta contable sectorial directa:

```text
same-window average stock
× compatible effective accrued rate
× accounting scaling
```

pero debe reconciliar razonablemente con el `interest_income` agregado antes de usarse.

No usar una tasa de nuevas operaciones para todo el stock sin ajuste.

### 4. CER/UVA bridge

Separar bruto:

```text
asset CER public securities
asset UVA household loans
asset indexed corporate loans
liability UVA deposits
other indexed liabilities
```

y recién luego reconciliar con el net CER/CVS.

### 5. FX bridge

Separar bruto:

```text
loans
deposits
BCRA-linked liquidity/instruments
public-sector FX assets/liabilities
forwards
trading result
translation/valuation
ORI
```

No inferir counterparty desde net mismatch.

## Output obligatorio

- `RAW_SOURCE_MANIFEST_V54.csv`
- `SECURITIES_RESULT_BRIDGE_V54.csv`
- `INTEREST_INCOME_ACCOUNTING_BRIDGE_V54.csv`
- `CER_GROSS_BRIDGE_V54.csv`
- `FX_GROSS_RESULT_BRIDGE_V54.csv`
- `Q4_2023_JOINT_COUNTERPARTY_PARTITION_V54.csv`
- `AUDITORIA_MICRODATA_BRIDGE_V54.md`
- `VEREDICTO_MICRODATA_BRIDGE_V54.md`
- `EVIDENCE_LEDGER_CICLO_AJUSTE_V54.csv`
- `README_V54.md`
- `MANIFEST_V54.json`
- QA script

## Gate principal

Una asignación sectorial sólo puede elevarse si:

```text
raw official source
+
same accounting window
+
reconcilable flow/accrual identity
+
no double count
```

Si el bridge no reconcilia, conservar V53 bound y marcar `FAILED_RECONCILIATION`.

No tocar HTML.
