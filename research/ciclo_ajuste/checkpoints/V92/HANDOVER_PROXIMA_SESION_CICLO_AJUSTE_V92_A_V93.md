# Handover — Ciclo de ajuste V92 → V93

**Fecha:** 2026-08-28

## Frozen strict state

- coverage = **58.272770048589213793621379529153308519125980618638424532051024938851826101688225%**
- exact asset numerator = **56348425.741 million ARS**
- denominator = **96697695.5 million ARS**
- exact eligible entities = **20**
- gate = **NO**
- frozen Sep→Dec factor = **1.532908152197492**

Exact entities: ICBC, Banco de Valores, Macro, Credicoop, BAPRO, Ciudad, Galicia, BBVA, Patagonia, Citi, Supervielle, Comafi, Bancor, Nuevo Banco de Santa Fe, Nuevo Banco de Entre Ríos, Banco de San Juan, Banco de Santa Cruz, BICE, Banco Industrial, **Nuevo Banco del Chaco**.

## V92 promotion — Nuevo Banco del Chaco

Q4 Dec-homogeneous (k ARS):
- BCRA income **11135244.167859780236144**
- BCRA expense **0**
- other-FI income **-0.122955442752296**
- other-FI expense **0**

Evidence class: NBCH-specific same-year crosswalk. Official Provincia del Chaco FY separated Annex Q reports BCRA pass income 27,741,649k, other-FI pass income 518k and no pass-expense line; raw Dec entity 00311 matches exactly. Apply those identities to Sep raw 00311 only. Never generalize six-digit codes.

## Active manual recoveries

### HSBC
Sep individual CNV presentation:
https://aif2.cnv.gov.ar/presentations/publicview/d483d33a-5c86-4fbb-ab9c-6528bf43f572

### Banco BMA / ex-Itaú
Individual 30/09/2023 filing **#3119515**:
https://aif2.cnv.gov.ar/presentations/publicview/9d3ded55-6d87-4ca2-9feb-920d961f3acd

## Holds
- BNA: Sep `521007` presentation/subaccount mapping unresolved.
- Santander: 9M pass total exact, BCRA-vs-otherFI split unresolved.
- Hipotecario: same-period expense presentation conflict.
- Banco de Santiago del Estero: compatible 2023 separated package not recovered.

## Suggested V93 order
1. Any user-rescued HSBC/BMA PDF.
2. **Banco de La Pampa S.E.M.**
3. Banco de Santiago del Estero.
4. Continue entity-by-entity. Never mass-map six-digit BCRA accounts.
