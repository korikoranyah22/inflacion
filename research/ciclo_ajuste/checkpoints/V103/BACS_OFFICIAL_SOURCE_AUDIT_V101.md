# BACS — official separated source audit V101

## Sources
- 9M official BACS PDF: https://bacs.com.ar/wp-content/uploads/2025/04/EEFF-BACS-30-09-2023-Completos-8.pdf
- FY official BACS PDF: https://bacs.com.ar/wp-content/uploads/2025/04/Estados-Financieros-BACS-31-12-2023-8.pdf
- Both contain **separated** financial statements and auditor/review reports.

## 9M separated (30/09/2023, k ARS)
- BCRA repo-active interest: **23,876,889**.
- repo-active interest with financial sector: **386,346**.
- passive-repo premium with financial sector: **2,167**.
- no separate BCRA repo-expense leg; the issuer opening plus the BACS-specific raw repo-result account set exhaust the pass-expense presentation.

## FY separated (31/12/2023, k ARS)
- Annex-Q / Note 18: BCRA repo income **63,177,601**; Other-FI repo income **610,427**.
- Annex-Q / Note 19: Other-FI repo expense **14,063**; BCRA repo expense **0**.

## Raw same-entity control
BCRA preserved Sep/Dec archives reproduce `511108`, `511027`, `521022` exactly for BACS. This crosswalk is **BACS-only** and must not be mass-mapped.

## Consolidation warning
A BACS prospectus table shows a consolidated 2023 passive-repo expense of **14,507k**, while the separated issuer FY is **14,063k**. The strict bridge therefore uses **14,063k**. This is direct evidence that consolidated and separated values cannot be substituted casually.

## Preservation gate
The execution runtime could read the two PDFs through web retrieval but could not persist the original bytes. Until both physical binaries + SHA-256 are stored in the repo, BACS remains `ANALYTICALLY_RESOLVED_SOURCE_PRESERVATION_HOLD`.
