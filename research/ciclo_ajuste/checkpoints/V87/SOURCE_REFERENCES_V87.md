# Source references — V87

## Frozen regulatory / raw layer

- BCRA Communication A 7809 — Annex Q frequency is annual: https://www.bcra.gob.ar/archivos/Pdfs/comytexord/A7809.pdf
- BCRA Communication A 7749 — strict four-leg Annex-Q taxonomy: https://www.bcra.gob.ar/pdfs/comytexord/A7749.pdf
- User-recovered official BCRA IEF raw archives: `sep2023.7z`, `dic2023.7z`.
- Companion official BCRA IEF publications: `sept2023.pdf`, `dic2023.pdf`.

## Banco Patagonia — primary issuer

- 30/09/2023 official Banco Patagonia financial statements:
  https://bp.bancopatagonia.com.ar/uploads/relacioninversores/20230930_EEFF.pdf
  - separated Note 21: pass income with financial sector = **129,800,318k**
  - separated Note 22: pass expense with financial sector = **313,196k**
- FY-2023 official Banco Patagonia financial statements:
  https://www.bancopatagonia.com.ar/relacionconinversores/espanol/docs/info_financiera_gestion/estados_contables/20231231_EEFF_Banco_Patagonia_SA_NIIF.pdf
  - separated Note 21: **342,520,451k**
  - separated Note 22: **982,789k**
  - separated Annex Q maps both totals entirely to **Otras Entidades financieras**, BCRA zero.
- BCRA raw entity 00034 reproduces all four 9M/FY nonzero source totals exactly.

## Citibank N.A. Argentina — primary issuer

- Citi official financial reports index:
  https://www.citibank.com/icg/sa/latam/argentina/institutional-info/financial-reports.html
- 30/09/2023 official Citi balance:
  https://www.citibank.com/icg/sa/latam/argentina/assets/docs/BalanceCitibankArgentinaSeptiembre2023.pdf
  - Note 25 explicitly reports pass income BCRA **421,911,207k**, other financial institutions **1,320,406k**; no pass-expense line.
- FY-2023 official Citi balance:
  https://www.citibank.com/icg/sa/latam/argentina/assets/docs/BalanceCitibankArgentinaDiciembre2023.pdf
  - Note 25 reports pass income total **922,760,307k**, BCRA **918,291,333k**, other FI **4,468,974k**.
  - FY Annex Q expense section contains deposits and other financial obligations but no pass-expense category, supporting zero pass expenses.
- Issuer values are primary; raw is control only where it does not exactly reproduce the issuer presentation.

## Banco Supervielle — primary issuer + entity-specific raw mapping

- 30/09/2023 official Banco Supervielle interim financial statements:
  https://content-us-7.content-cms.com/8ba19f21-9a97-4525-8886-f54d823a5cea/dxdam/02/025e5bb4-d630-480e-a03d-397a022080ff/EECC%20Banco%20Supervielle%2030.09.23.pdf
  - separated 9M pass totals: income **88,903,285k**, expense **420,309k**.
- FY-2023 official Banco Supervielle financial statements:
  https://content-us-7.content-cms.com/8ba19f21-9a97-4525-8886-f54d823a5cea/dxdam/08/08afb7e5-b4c1-4396-925e-b66a2f5c13b1/EECC%20Banco%20Supervielle%2031.12.2023.pdf
  - separated Annex Q: BCRA income **219,708,132k**, other-FI income **3,285,840k**, BCRA expense **0**, other-FI expense **1,235,416k**.
- BCRA raw FY entity 00027 exactly reconstructs those four FY legs:
  - `511108 = 219,708,132`
  - `511027 + 515034 = 3,285,840`
  - `521022 + 525042 = 1,235,416`
- The identical account set at 9M exactly reconstructs published totals:
  - BCRA income = `86,904,713`
  - other-FI income = `1,926,107 + 72,465 = 1,998,572`
  - other-FI expense = `155,204 + 265,105 = 420,309`
- This mapping is **Supervielle-specific** and is not generalized.

## Pending top two

- Santander separated 9M recovered via:
  https://financialfilings.com/filings/banco-santander-argentina-sa/interim-quarterly-report/2023/45095316/
  Total pass income reconciles raw exactly, but accumulated 9M counterparty split remains missing.
- BNA remains pending because `521007` cannot be mapped to the strict pass-expense leg from the FY presentation.
