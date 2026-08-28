# Handover — Ciclo de ajuste V90 → V91

**Fecha:** 2026-08-28

## Frozen strict state

- coverage = **57.1190506613469397520440391467240292194967562593050627561233%**
- exact asset numerator = **55232805.681 million ARS**
- denominator = **96697695.5 million ARS**
- exact eligible entities = **18**
- gate = **NO**
- frozen Sep→Dec factor = **1.532908152197492**

Exact entities: ICBC, Banco de Valores, Macro, Credicoop, BAPRO, Ciudad, Galicia, BBVA, Patagonia, Citi, Supervielle, Comafi, Bancor, Nuevo Banco de Santa Fe, Nuevo Banco de Entre Ríos, Banco de San Juan, Banco de Santa Cruz, **BICE**.

## V90 promotion — BICE

Q4 Dec-homogeneous (k ARS):
- BCRA income **34882023.954531658032028**
- BCRA expense **0E-15**
- other-FI income **-1.076792919412032**
- other-FI expense **44197.000000000000000**

Evidence logic: user-rescued AGN SC is report-only; BICE closes through BCRA entity 00300 Sep/Dec raw + BICE-specific FY separated issuer crosswalk. FY raw 511108/511027 matches separated Annex Q BCRA/otherFI income exactly; 521007 matches the separated pass-expense total, and BICE Note 5 / consolidated Annex Q validates that expense as other-FI. Do not generalize these account IDs to other banks.

## Active manual recovery

### HSBC
Sep individual CNV presentation:
https://aif2.cnv.gov.ar/presentations/publicview/d483d33a-5c86-4fbb-ab9c-6528bf43f572

## Holds
- BNA: Sep `521007` presentation/subaccount mapping unresolved.
- Santander: 9M pass total exact, BCRA-vs-otherFI split unresolved.
- Hipotecario: same-period expense presentation conflict.
- Banco de Santiago del Estero: compatible 2023 separated package not recovered.

## Suggested V91 order
1. Any user-rescued HSBC PDF.
2. Banco BMA / ex-Itaú individual CNV filing (Sep document id 3119515 if recoverable).
3. Banco Industrial separated 9M.
4. Nuevo Banco del Chaco / Banco de La Pampa where 9M issuer opening can be recovered.
5. Continue entity-by-entity. Never mass-map six-digit BCRA accounts.
