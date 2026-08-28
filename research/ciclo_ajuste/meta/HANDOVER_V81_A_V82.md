# Handover — Ciclo de ajuste / red de pases bancarios V81 → V82

**Fecha de corte:** 2026-08-28  
**Checkpoint formal cerrado:** V81  
**Próxima iteración sugerida:** V82

## 1. Estado congelado

Cobertura strict Q4 four-leg: **23.54332498027319%**.

Entidades exactas elegibles:
- ICBC Argentina
- Banco de Valores
- Banco Macro
- Banco Credicoop
- Banco Provincia (BAPRO)

Gate de red cerrada: **NO**.

Regla Q4 congelada:

`Q4_Dec = FY_Dec - 9M_Sep × 1.532908152197492`

Base strict permitida: `INDIVIDUAL_STANDALONE` o `SEPARATED_INDIVIDUAL`.

## 2. Qué cerró V81

### Corrección importante de `InfBanc_Anexo.xlsx`

El archivo preservado bajo `inputs/bcra/2023-09/` **no es una snapshot congelada a septiembre-2023**. Es el anexo vivo del BCRA con última fecha **enero-2026**.

Fingerprint:

`9b1b48b18039389889ee7d480a9c6d8958fb99630f169339e46ab953e7133251`

La recuperación en el directorio 2023-09 se conserva por transparencia: el path documenta el contexto de descarga, no el vintage interno.

### Control agregado bancos públicos

Fila `Bancos públicos → Primas por pases`, hoja `Estado de Resultado desde 2020`.

Q4-2023 en el XLSX vivo:
**3820525.396925 millones ARS a precios ene-2026**

Factor para volver a dic-2023:
`10413.0309 / 3533.2 = 2.947195431903091`

Q4-2023 comparable:
**1296325.773163 millones ARS de dic-2023**

La jerarquía de grupos reconcilia, pero **no existe crosswalk probado `Primas por pases ↔ four-leg Anexo Q`** y el XLSX no desagrega entidades.

Por eso:
- no promover BNA;
- no promover Ciudad;
- no repartir residual público;
- no tratarlo como hard bound individual.

### Códigos BCRA

A 7749 confirma exactamente:
- 0301060100 ingreso pase BCRA
- 0301060200 ingreso pase otras EF
- 0302030100 egreso pase BCRA
- 0302030200 egreso pase otras EF

El problema pendiente ya no es taxonomía: es recuperar el dataset entidad×cuenta.

## 3. BNA

AGN Memoria 2024 confirma trabajo 187:
**estados financieros intermedios consolidados condensados y separados condensados al 30/09/2024**.

El PDF público `BALANCE CONDENSADO SEP 2024.pdf` es resumen/control y no abre four-leg.

Todavía falta:
1. paquete separado completo BNA 30/09/2023; o
2. paquete separado completo 30/09/2024 con comparativo 30/09/2023; o
3. raw BCRA entidad×cuenta 2023-09.

## 4. Banco Ciudad

Sigue control-only consolidado. No asignar residual del grupo público.

## 5. Orden V82

1. Retomar BCRA raw entity archive 2023-09 con los códigos ya validados.
2. Buscar binario largo BNA 30/09/2024 separado/comparativo.
3. Buscar BNA 30/09/2023 directo si emerge una ruta nueva.
4. Banco Ciudad separado 9M-2023.
5. Mantener coverage exactamente **23.54332498027319%** salvo evidencia individual/separada exacta.

## 6. Regla de rescate manual

Sólo pedirle a Miyu ayuda cuando exista un **archivo concreto** bloqueado o un botón exacto visible. Dar URL + nombre/botón + archivo que NO sirve + resultado esperado. No pedir navegación vaga.

## 7. Archivos centrales V81

- `BCRA_INFBANC_ANEXO_AUDIT_V81.md`
- `BCRA_PUBLIC_BANK_PASS_AGGREGATE_CONTROL_V81.csv`
- `BCRA_PASS_AGGREGATE_RECONCILIATION_V81.csv`
- `BCRA_PUBLIC_BANK_PASS_COMPARISON_V81.csv`
- `AUDITORIA_V81.md`
- `VEREDICTO_V81.md`
- `CURRENT_STATE_V81.csv`
- `RECOVERY_QUEUE_V81.csv`
- `SOURCE_REFERENCES_V81.md`
- `USER_FILE_REQUESTS_V81.md`
- `STRICT_Q4_FOUR_LEG_COVERAGE_V81.csv`
- `FOUR_LEG_PASS_PANEL_V81.csv`

**V81 cerrado como control/auditoría, sin promoción.**
