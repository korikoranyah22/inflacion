# Archaeology batch 4 — loose Downloads + Round 2 reconciliation

Fecha: 2026-08-28

## Round 2
- 35 requested
- 34 valid downloads
- 34 binaries ingested after SHA-256 / size / magic validation
- 1 failed: `bcra_boldat202505_tipo_titular`

## Loose Downloads carriers
- `csvs(1).zip`: 66 CSV members, preserved as recovered historical project artifacts.
- `xlsxs(1).zip`: 11 XLSX members.
  - 5 exact duplicates of already-preserved repo files.
  - 1 duplicate within the carrier.
  - 4 unique unclassified/personal XLSX preserved under recovered_loose without source promotion.
  - 1 new source-relevant file: `Infbanc0624.xlsx`, preserved and catalogued as `hist_bcra_infbanc_jun2024_xlsx`.

No loose file was used to overwrite a current artifact with the same filename but different SHA-256.

## AGN reconciliation
`agn_bna_informe210_9m2023` was a false page-only gap: its three official attachments had already been preserved under V72/manual recovery. A deterministic ZIP bundle was created and linked in `FUENTES.csv`.

## Current source completeness
- master catalog entries: **189**
- entries with local binary: **156**
- local paths existing: **156/156**
- SHA-256 matching: **156/156**
- physical gaps remaining: **33**
- Round 3 direct-binary actionable: **26**
- page/snapshot discovery remaining: **7**
- P0/P1: **0 / 0**

Numeric checkpoint remains V96 unchanged.
