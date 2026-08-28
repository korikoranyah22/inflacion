# Handover — Ciclo de ajuste V88 → V89

**Fecha:** 2026-08-28

## Frozen strict state

- coverage = **53.569372790275027805600599861244883545337437746901%**
- exact asset numerator = **51800348.982 million ARS**
- denominator = **96697695.5 million ARS**
- exact eligible entities = **13**
- gate = **NO**
- frozen Sep→Dec factor = **1.532908152197492**

Exact entities: ICBC, Banco de Valores, Macro, Credicoop, BAPRO, Ciudad, Galicia, BBVA, Patagonia, Citi, Supervielle, **Comafi**, **Bancor**.

## V88 promotion — Comafi

Official separated 30/09/2023 package voluntarily contains an interim Annex Q and explicitly supplies all four legs. FY separated Annex Q supplies the same four-leg taxonomy. Q4:

- income BCRA = **136510581.599939314269112k**
- expense BCRA = **0k**
- income other-FI = **1485781.919302356282468k**
- expense other-FI = **654.163043949846892k**

Nuance: A7809 lists Annex Q as annual required frequency, but issuers may voluntarily include interim Annex Q. Do not assume quarterly availability; use it when actually published.

## V88 promotion — Bancor

FY separated Annex Q exactly maps Bancor raw:

- 511108 → BCRA pass income
- 511027 → other-FI pass income
- 521022 → other-FI pass expense
- BCRA expense = 0
- 515034 is explicitly non-pass and excluded.

The same Sep raw account set reconciles the official separated Sep-2024 filing's comparator for 9M-2023 pass-income / pass-expense totals under a common reexpression factor. This validates the set **for Bancor only**.

Q4:

- income BCRA = **53876602.361490745526904k**
- expense BCRA = **0k**
- income other-FI = **2759.65078745289432k**
- expense other-FI = **25539.8061521107559k**

## Hipotecario — do not promote

9M pass-income total is exact against raw, but the separated 9M expense note contains no pass-expense line while raw `521022=158,630k`. FY Annex Q maps a later `521022` value into pass expense. This is a direct warning not to carry FY raw mapping backward without same-period support.

## Active manual rescue — HSBC

Priority 30/09/2023 individual CNV presentation:
https://aif2.cnv.gov.ar/presentations/publicview/d483d33a-5c86-4fbb-ab9c-6528bf43f572

Optional FY individual:
https://aif2.cnv.gov.ar/presentations/publicview/39f37eb9-5637-4cb3-ab6b-715da7830bd1

If Miyu uploads the PDF, process it first in V89.

## Other pending

- BNA: Sep 521007 presentation/subaccount mapping unresolved.
- Santander: 9M pass total exact but BCRA-vs-otherFI split unresolved.
- Hipotecario: same-period expense presentation conflict.

Continue entity-by-entity; do not mass-map six-digit raw accounts.
