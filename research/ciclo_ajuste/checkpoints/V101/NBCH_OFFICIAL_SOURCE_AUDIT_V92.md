# Nuevo Banco del Chaco — official-source audit V92

## Official FY issuer presentation recovered through Provincia del Chaco publication

The official Chaco bulletin publishes **Nuevo Banco del Chaco S.A. — Estado de Resultados Separado / Anexo Q** for FY-2023. The Annex Q opening gives:

- pass income total: **27,742,167k ARS**;
- BCRA pass income: **27,741,649k ARS**;
- other-financial-institutions pass income: **518k ARS**;
- no `por operaciones de pase` item appears under interest expense, hence both strict pass-expense legs are **0** in the official separated FY presentation.

Primary public source: `https://chaco.gov.ar/uploads/boletines/25-03-24-11076-660183ddcbb40676491772.pdf` (Boletín Oficial de la Provincia del Chaco, edición 11.076, separated NBCH statements/Annex Q).

NBCH's own 2023 document category independently confirms publication of FY-2023 financial-report materials: `https://www.nbch.com.ar/documentos/categoria/informes-2023`.

## Entity-specific BCRA raw reconciliation

Preserved BCRA raw entity `00311` matches the FY separated Annex Q one-to-one:

- `511108 = 27,741,649k` ↔ BCRA pass income;
- `511027 = 518k` ↔ other-FI pass income;
- no nonzero pass-expense result account ↔ FY Annex Q has no pass-expense line.

For Sep-2023 the same entity's raw values are `511108 = 10,833,268k`, `511027 = 338k`, with no nonzero pass-expense result account. V92 therefore uses this **NBCH-specific, same-year crosswalk only**. It is not a universal interpretation of six-digit BCRA accounts.

## Q4 result

Using frozen Sep→Dec factor `1.532908152197492`:

- BCRA income: **11135244.167859780236144k**;
- BCRA expense: **0k**;
- other-FI income: **-0.122955442752296k**;
- other-FI expense: **0k**.

The small negative other-FI income differencing residual is preserved and not clamped.
