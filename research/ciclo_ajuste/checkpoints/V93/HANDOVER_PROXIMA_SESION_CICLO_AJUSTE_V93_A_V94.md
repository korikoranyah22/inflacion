# Handover — Ciclo de ajuste V93 → V94

**Fecha:** 2026-08-28

## Frozen strict state

- coverage = **58.788884622384821983684192349754601959464483825263446945330770576636958219960888%**
- exact asset numerator = **56847496.640 million ARS**
- denominator = **96697695.5 million ARS**
- exact eligible entities = **21**
- gate = **NO**
- frozen Sep→Dec factor = **1.532908152197492**

Exact entities: ICBC, Banco de Valores, Macro, Credicoop, BAPRO, Ciudad, Galicia, BBVA, Patagonia, Citi, Supervielle, Comafi, Bancor, Nuevo Banco de Santa Fe, Nuevo Banco de Entre Ríos, Banco de San Juan, Banco de Santa Cruz, BICE, Banco Industrial, Nuevo Banco del Chaco, **Banco de La Pampa S.E.M.**.

## V93 promotion — Banco de La Pampa S.E.M.

Official FY-2023 issuer Annex Q: BCRA income **54,227,326k**; other-FI income **0**; BCRA expense **0**; other-FI expense **5,110k**. Preserved Dec BCRA entity `00093` raw matches `511108=54,227,326k` and `521022=5,110k` one-to-one. Sep raw: `511108=19,150,613k`, `521022=3,334k`, no `511027`. CNV identifies 30/09/2023 filing **#3121031** as individual. Crosswalk is Banco-de-La-Pampa-specific and same-year only.

Q4: BCRA income **24871195.212720731137404k**; BCRA expense **0**; other-FI income **0**; other-FI expense **-0.715779426438328k**. Tiny negative expense residual preserved.

Assets added: **499070.899 million ARS**. Coverage increment: **0.516114573795608190062812820601293440338503206625022413279745637785132118272663 pp**.

## Active manual recoveries

### HSBC
Sep individual CNV presentation:
https://aif2.cnv.gov.ar/presentations/publicview/d483d33a-5c86-4fbb-ab9c-6528bf43f572

### Banco BMA / ex-Itaú
Sep individual filing #3119515 / publicview:
https://aif2.cnv.gov.ar/presentations/publicview/9d3ded55-6d87-4ca2-9feb-920d961f3acd

## Holds
- BNA: Sep `521007` presentation/subaccount mapping unresolved.
- Santander: 9M pass total exact, BCRA-vs-otherFI split unresolved.
- Hipotecario: same-period expense presentation conflict.

## Suggested V94 order
1. Any user-rescued HSBC/BMA PDF.
2. **Banco de Santiago del Estero S.A.** — next autonomous entity; recover compatible FY/9M issuer counterparty opening.
3. Continue entity-by-entity. Never mass-map six-digit BCRA accounts.
