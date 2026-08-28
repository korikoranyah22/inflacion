# AUDITORÍA V81 — Ciclo de ajuste / red de pases

## Objetivo

Formalizar el control agregado BCRA recibido después de V80 y reabrir retrieval individual sólo donde respete el gate de base.

## Hallazgo principal

`InfBanc_Anexo.xlsx` no es una snapshot 09/2023: es una versión viva con última información enero-2026. El archivo sigue siendo útil porque conserva series históricas y documenta balances no consolidados por grupo, pero sus valores históricos están reexpresados a precios de la última fecha del anexo.

Se creó:

- `BCRA_INFBANC_ANEXO_AUDIT_V81.md`
- `BCRA_PUBLIC_BANK_PASS_AGGREGATE_CONTROL_V81.csv`
- `BCRA_PASS_AGGREGATE_RECONCILIATION_V81.csv`
- `BCRA_PUBLIC_BANK_PASS_COMPARISON_V81.csv`

## Control de bancos públicos

`Primas por pases`, bancos públicos, Q4-2023:

- fuente viva a precios ene-2026: **3820525.396925 millones ARS**
- reexpresado a dic-2023 con el IPC congelado del proyecto: **1296325.773163 millones ARS**

El agregado reconcilia con la jerarquía de grupos del propio BCRA.

## Gate four-leg

No existe crosswalk explícito `Primas por pases ↔ cuatro patas Anexo Q`; tampoco hay filas individuales.

Resultado: **no hay nueva entidad strict**.

Cobertura strict Q4 four-leg:

**23.54332498027319%**

## Retrieval BNA

La AGN registra el trabajo 187/2024: estados financieros intermedios consolidados condensados y separados condensados al 30/09/2024 de BNA.

El PDF público fácil del BNA `BALANCE CONDENSADO SEP 2024.pdf` es un resumen y no abre contrapartes de pases. La existencia del paquete largo queda confirmada, pero todavía no se recuperó un binario con las notas comparativas necesarias.

## BCRA raw entity archive

La Comunicación A 7749 vigente en 2023 confirma exactamente:

- `0301060100` — ingresos por pases, BCRA
- `0301060200` — ingresos por pases, otras entidades financieras
- `0302030100` — egresos por pases, BCRA
- `0302030200` — egresos por pases, otras entidades financieras

La taxonomía ya no es una hipótesis. Falta el **archivo entidad×cuenta 2023-09**, no la definición de los códigos.

## Decisión

V81 cierra como iteración de **control/auditoría**, no de promoción.
