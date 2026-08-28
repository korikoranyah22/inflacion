# Source references — V86

## Primary official sources

- BCRA Communication A 7809 — Section 12; Annex Q frequency = annual: https://www.bcra.gob.ar/archivos/Pdfs/comytexord/A7809.pdf
- BCRA Communication A 7749 — Annex Q four-leg taxonomy (`0301060100/0200`, `0302030100/0200`): https://www.bcra.gob.ar/pdfs/comytexord/A7749.pdf
- SEC / Banco BBVA Argentina 6-K — financial statements as of 30/09/2023, including separate statements and notes: https://www.sec.gov/Archives/edgar/data/913059/000129281424001417/0001292814-24-001417.txt
- SEC / Banco BBVA Argentina FY-2024 financial statements, comparative 2023, including Exhibit-Q repo counterparty split: https://www.sec.gov/Archives/edgar/data/913059/000129281425002055/ex99-1.htm
- User-recovered official BCRA IEF Sep-2023 raw archive: `sep2023.7z`
- User-recovered official BCRA IEF Dec-2023 raw archive: `dic2023.7z`
- Companion official BCRA IEF publications: `sept2023.pdf`, `dic2023.pdf`

## BBVA 9M exact issuer reconciliation

Separate Note 26 reports accumulated 9M premiums on reverse repurchase agreements = **148,514,057 thousand ARS**. Raw individual entity 00017 gives `511108=148,146,353` and `511027=367,704`; exact sum = 148,514,057.

Separate Note 27 reports accumulated 9M premiums on reverse repurchase transactions = **15,128 thousand ARS**. Raw entity 00017 gives `521022=15,128`; exact equality.

## Annual entity-specific counterparty validation

The FY-2024 issuer filing reports comparative 2023 repo/surety-bond income: BCRA **844,167,266**, other financial institutions **1,227,415**; expense: BCRA **0**, other financial institutions **54,412** (all in Dec-2024 constant-currency thousand ARS). Those three nonzero legs are proportional to the raw individual Dec-2023 entity 00017 accounts `511108=387,654,578`, `511027=563,648`, `521022=24,987`, with the common re-expression factor differing only at source rounding precision. This validates the mapping for BBVA specifically; it is not generalized to other banks.
