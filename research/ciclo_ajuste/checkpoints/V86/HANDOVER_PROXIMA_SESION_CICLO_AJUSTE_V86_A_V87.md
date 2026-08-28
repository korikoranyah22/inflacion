# Handover — Ciclo de ajuste V86 → V87

**Fecha:** 2026-08-28

## Frozen strict state

- coverage = **42.60167543910082117727407474772757123255%**
- exact eligible entities = ICBC, Banco de Valores, Macro, Credicoop, BAPRO, Ciudad, Galicia, **BBVA Argentina**
- exact asset numerator = **41194838.394 million ARS**
- denominator = **96697695.5 million ARS**
- gate = **NO**
- Sep→Dec factor = **1.532908152197492**

## V86 promotion — BBVA Argentina

9M separated issuer Notes 26/27 reconcile BCRA individual raw entity `00017` exactly:

- 9M pass income total = 148,514,057k = 148,146,353 (`511108`) + 367,704 (`511027`).
- 9M pass expense total = 15,128k = `521022`.

FY raw entity values:

- BCRA income = 387,654,578k
- other-FI income = 563,648k
- BCRA expense = 0
- other-FI expense = 24,987k

The issuer FY-2024 filing comparative 2023 Exhibit-Q counterparty split validates the same mapping after a common inflation re-expression factor. This is **entity-specific**, not a universal six-digit rule.

Q4 Dec-homogeneous:

- BCRA income = **160559825.767972624453324k**
- BCRA expense = **0k**
- other-FI income = **-8.459195626598368k**
- other-FI expense = **1797.165473556341024k**

Preserve the `-8.459k` other-FI income residual; it is a source-rounding/re-expression artifact, not a reason to clamp.

## Critical methodology correction

BCRA Communication A 7809 states **Annex Q is annual**. Never again formulate the 30/09 recovery target as “Annex Q 9M”. For 9M use separated interest notes/exhibits or an explicit entity-specific regulator mapping.

## Still rejected

Do **not** mass-promote banks from six-digit IEF account names. Santander remains the counterexample proving the split can live below six-digit/presentation level.

## V87 priorities

1. BNA: recover separated 30/09/2023 interest-income / interest-expense notes or explicit subaccount→presentation mapping to resolve Sep `521007`.
2. Santander: recover separated 30/09/2023 interest notes/exhibits or explicit BCRA-vs-otherFI mapping.
3. After those, attack next large bank only with entity-specific 9M/FY validation.
4. Keep gate NO until coverage materially closes.
