# Handover — Ciclo de ajuste V94 → V95

**Fecha:** 2026-08-28

## Frozen strict state

- coverage = **59.332775042193223725791893354893860940046911459229139540352334456615876642065374%**
- exact asset numerator = **57373426.142 million ARS**
- denominator = **96697695.5 million ARS**
- exact eligible entities = **22**
- gate = **NO**
- frozen Sep→Dec factor = **1.532908152197492**

Exact entities: ICBC, Banco de Valores, Macro, Credicoop, BAPRO, Ciudad, Galicia, BBVA, Patagonia, Citi, Supervielle, Comafi, Bancor, Nuevo Banco de Santa Fe, Nuevo Banco de Entre Ríos, Banco de San Juan, Banco de Santa Cruz, BICE, Banco Industrial, Nuevo Banco del Chaco, Banco de La Pampa, **Banco Provincia del Neuquén S.A.**

## V94 promotion — Banco Provincia del Neuquén

Official BPN FY-2023 Annex Q page 83: BCRA pass income **129,240,317k**; other-FI pass income **0**; no pass-expense line, so both expense legs **0**. Preserved Dec BCRA entity `00097` raw matches `511108=129,240,317k` one-to-one and contains no `511027/521007/521022`. Sep raw: `511108=50,821,306k`; no other candidate repo-result accounts. Official BPN disclosure says the bank is not part of economic groups.

Q4: BCRA income **51335922.727276686635448k**; the other three strict legs are **0**.

Assets added: **525929.502 million ARS**. Coverage increment: **0.543890419808401742107701005139258980582427633965692595021563879978918422104486 pp**.

## V94 hold — Banco de Santiago del Estero

BSE raw entity `00321` is now documented exactly:
- Sep `511108=95,939,845k`; Dec `511108=212,143,831k`; no 511027/521007/521022 in either full nonzero file.
- Official BCRA IEF confirms the entity but not the Annex-Q counterparty split.
- No compatible issuer FY/9M opening recovered.

Therefore BSE remains **N/D_STRICT**; do not classify `511108` by account name alone.

## Active manual recoveries

### HSBC
https://aif2.cnv.gov.ar/presentations/publicview/d483d33a-5c86-4fbb-ab9c-6528bf43f572

### Banco BMA / ex-Itaú
https://aif2.cnv.gov.ar/presentations/publicview/9d3ded55-6d87-4ca2-9feb-920d961f3acd

### BSE
Official FY-2023 Annex Q / separated or standalone issuer package still needed.

## Holds
- BNA: Sep `521007` presentation/subaccount mapping unresolved.
- Santander: 9M pass total exact, BCRA-vs-otherFI split unresolved.
- Hipotecario: same-period expense presentation conflict.
- BSE: raw exact, issuer counterparty crosswalk unresolved.

## Suggested V95 order
1. Any user-rescued HSBC/BMA/BSE PDF.
2. **Banco de Corrientes S.A.** — next autonomous target (BCRA raw sweep code `00094`, Dec assets 349,527.560m ARS).
3. Continue entity-by-entity. Never mass-map six-digit BCRA accounts.
