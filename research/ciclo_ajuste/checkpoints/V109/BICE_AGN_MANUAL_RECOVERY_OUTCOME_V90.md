# BICE AGN manual-recovery outcome — V90

The user rescued all three AGN Informe 209/2023 PDFs requested at the V89 handoff.

## What the rescued files actually contain

- `2023-209-Informe Anexo 1 SC.pdf`: 2-page independent-auditor **review report** for BICE separated condensed interim financial statements at 30/09/2023. It confirms the separated 9M package was reviewed, but it does **not** contain the financial statements, notes, or Annex Q itself.
- `2023-209-Informe Anexo CC.pdf`: 2-page independent-auditor report for the **consolidated** condensed interim statements. It is not substituted into the strict target basis.
- `2023-209-Resolucion.pdf`: 2-page AGN Resolution 209/2023 approving the review work for BICE at 30/09/2023.

SHA-256 of user-rescued binaries:
- SC: `f2851ac0049c1596bb8ae20529667ee61d79f83c81b1c2bfd831cb2768ba7ed1`
- CC: `8f998f5bc342e61fc90f4b06388a0254508d9a1a2f4e1c358a7a4484056696b9`
- Resolution: `be6b49a3f3708bd4c6e0e2a27465c86ce8f57d033f0cc7b84894ff46053489e0`

## Why BICE can nevertheless close in V90

The rescue clarified that the AGN `SC` link is report-only, so V90 does **not** pretend it contains an interim Annex Q. Instead, the strict bridge is rebuilt from target-basis BCRA raw data plus a BICE-specific same-year issuer crosswalk:

1. BCRA entity `00300` raw Sep-2023 contains `511108=26,984,941k` and `511027=68,496k`; no pass-expense result account is present.
2. BCRA entity `00300` raw Dec-2023 contains `511108=76,247,460k`, `511027=104,997k`, `521007=44,197k`.
3. BICE FY-2023 **separated** Annex Q reports BCRA pass income `76,247,460k`, other-FI pass income `104,997k`, and total pass expense `44,197k` — exact one-to-one reconciliation with those raw accounts.
4. BICE separated Note 5 explicitly refers to the repo operations detailed in consolidated Note 5; the FY consolidated Annex Q opens the same `44,197k` pass expense entirely under Other Financial Institutions, with BCRA expense zero. This is used only as a BICE-specific counterparty validation, not as a substitute target basis.
5. The same validated account identities are then used within BICE for Sep-2023. This does not create a universal six-digit mapping rule.

Frozen Sep→Dec factor: `1.532908152197492`.

Q4 Dec-homogeneous four legs (k ARS):
- BCRA income: **34882023.954531658032028**
- BCRA expense: **0E-15**
- other-FI income: **-1.076792919412032**
- other-FI expense: **44197.000000000000000**

The small negative other-FI income residual (`-1.076792919412032k`) is preserved as differencing/source-rounding residue and is not clamped.
