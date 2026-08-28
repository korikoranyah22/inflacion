# Prompt Codex — V53 · cuantificación por emisor, sector y contrato

## Estado V52 congelado

```text
COUNTERPARTY_MAP = SUPPORTED
BCRA_DIRECT_COUNTERPARTY = STRONG_SUPPORT_FOR_PASSES
DIRECT_HOUSEHOLD_CONTRACT = EXISTS_AT_SPECIFIC_CONTRACT_LEVEL
DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED_AT_ABNORMAL_GAP_LEVEL
TAXPAYER_IDENTITY = REJECTED
```

## Misión

Cerrar los cuatro N/D que impiden cuantificar incidencia:

1. `securities_result`: separar BCRA / Tesoro / market valuation / ORI por episodio y ventana;
2. `interest_income`: separar hogares / empresas / sector público / otros;
3. `CER_CVS`: separar activos y pasivos por sector e instrumento;
4. `FX`: mapear activos, pasivos, derivados y ORI por contraparte/sector cuando exista evidencia.

## Prioridad cuantitativa

### Q4-2023

Congelado:

```text
gross-positive margin subcomponent gaps = 28.7 pp
passes BCRA = 7.7 pp = 26.8% floor
FX valuation = 11.3 pp
securities mixed = 7.3 pp
interest income mixed = 2.1 pp
```

Objetivo V53: reducir `mixed` y `N/D` **sin convertir este gross-positive subtotal en net profit o causal treatment effect**.

## Gates

- No asumir que un bono del Tesoro pagó una ganancia de valuación secundaria.
- No asignar interés agregado a hogares sin sector split.
- No usar stock de préstamos como proxy mecánico de ingreso por intereses sin tasa/devengamiento compatible.
- No inferir contraparte FX desde el signo neto.
- No sumar ventanas 2014/2018/2023.
- Mantener Q4-2023 como ventana contable contaminada para causalidad post-10/12.

## Output obligatorio

- `SECURITIES_ISSUER_VALUATION_SPLIT_V53.csv`
- `INTEREST_INCOME_SECTOR_SPLIT_V53.csv`
- `CER_ASSET_LIABILITY_SECTOR_MAP_V53.csv`
- `FX_GROSS_COUNTERPARTY_MAP_V53.csv`
- `HOUSEHOLD_DIRECT_FLOW_BOUND_V53.csv`
- `AUDITORIA_CUANTIFICACION_CONTRAPARTES_V53.md`
- `VEREDICTO_CUANTIFICACION_CONTRAPARTES_V53.md`
- `EVIDENCE_LEDGER_CICLO_AJUSTE_V53.csv`
- `README_V53.md`
- `MANIFEST_V53.json`
- QA script

## Pregunta final V53

```text
De los componentes anormales positivos identificados,
qué fracción mínima/máxima puede atribuirse a:
BCRA, Tesoro, valuación de mercado, hogares y empresas,
sin doble conteo y dentro de ventanas contables compatibles?
```

No tocar HTML.
