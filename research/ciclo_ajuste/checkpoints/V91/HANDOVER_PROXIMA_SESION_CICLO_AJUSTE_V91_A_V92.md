# Handover — Ciclo de ajuste V91 → V92

**Fecha:** 2026-08-28

## Frozen strict state

- coverage = **57.916056198050759131069467937837256938558582298375456114153206474294932912853130%**
- exact asset numerator = **56003491.668 million ARS**
- denominator = **96697695.5 million ARS**
- exact eligible entities = **19**
- gate = **NO**
- frozen Sep→Dec factor = **1.532908152197492**

Exact entities: ICBC, Banco de Valores, Macro, Credicoop, BAPRO, Ciudad, Galicia, BBVA, Patagonia, Citi, Supervielle, Comafi, Bancor, Nuevo Banco de Santa Fe, Nuevo Banco de Entre Ríos, Banco de San Juan, Banco de Santa Cruz, BICE, **Banco Industrial**.

## V91 promotion — Banco Industrial

Q4 Dec-homogeneous (k ARS):
- BCRA income **152115463.880168364322132**
- BCRA expense **0.000000000000000**
- other-FI income **13088.901470779662428**
- other-FI expense **1964.590567920517340**

Evidence class: Banco-Industrial-specific same-year crosswalk. FY separated Annex Q matches BCRA raw 00322 `511108/511027/521022` exactly; apply those identities to Sep raw for this entity only. Never generalize six-digit codes.

## Active manual recoveries

### HSBC
Sep individual CNV presentation:
https://aif2.cnv.gov.ar/presentations/publicview/d483d33a-5c86-4fbb-ab9c-6528bf43f572

### Banco BMA / ex-Itaú
Individual 30/09/2023 filing **#3119515**:
https://aif2.cnv.gov.ar/presentations/publicview/9d3ded55-6d87-4ca2-9feb-920d961f3acd

V91 identified/extracted raw entity 00259 Sep/Dec values but **did not promote** without the issuer attachment/crosswalk.

## Holds
- BNA: Sep `521007` presentation/subaccount mapping unresolved.
- Santander: 9M pass total exact, BCRA-vs-otherFI split unresolved.
- Hipotecario: same-period expense presentation conflict.
- Banco de Santiago del Estero: compatible 2023 separated package not recovered.

## Suggested V92 order
1. Any user-rescued HSBC/BMA PDF.
2. Nuevo Banco del Chaco.
3. Banco de La Pampa.
4. Banco de Santiago del Estero.
5. Continue entity-by-entity. Never mass-map six-digit BCRA accounts.
