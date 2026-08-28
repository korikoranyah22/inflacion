# Auditoría V86

## 1. Correction of the retrieval target

BCRA Communication A 7809 makes Annex Q annual. V86 therefore removes “Annex Q 9M” from the recovery logic and replaces it with the separated 9M interest notes/exhibits or an explicit entity-specific mapping.

## 2. BBVA 9M separate issuer reconciliation

BBVA separate Note 26: accumulated 9M pass/reverse-repo income = **148,514,057k**.

BCRA raw entity 00017: `511108=148,146,353k` + `511027=367,704k` = **148,514,057k**, exact.

BBVA separate Note 27: accumulated 9M pass/reverse-repo expense = **15,128k**.

BCRA raw entity 00017: `521022=15,128k`, exact.

## 3. Annual counterparty validation

The issuer's FY-2024 filing exposes the comparative 2023 Annex-Q-style counterparty split. Re-expression ratios versus individual raw Dec-2023 are:

- BCRA income: `2.177627490832831077774605824466749880611`
- other-FI income: `2.177626816736686726467582604746224594073`
- other-FI expense: `2.177612358426381718493616680673950454236`

The ratios coincide within published-thousand rounding, and the annual issuer table explicitly gives BCRA expense = 0. This is sufficient for an **entity-specific** BBVA crosswalk. It does not revive the rejected universal six-digit mapping.

## 4. Q4 bridge

Frozen Sep→Dec factor = `1.532908152197492`.

Q4 = FY_Dec − 9M_Sep × factor:

- income BCRA = **160559825.767972624453324k**
- expense BCRA = **0k**
- income other FI = **-8.459195626598368k**
- expense other FI = **1797.165473556341024k**

The tiny negative other-FI income residual (**−8.459k**) is preserved. It is compatible with published-thousand cumulative rounding after re-expression and is not clamped to zero.

## 5. Coverage

BBVA Dec-2023 assets = **6059940.594 million ARS**.

Strict numerator = **41194838.394 million ARS**.
Strict coverage = **42.60167543910082117727407474772757123255%**.
Increment vs V85 = **6.26689246591197717727407474772757123255 pp**.
Exact entities = **8**.
Gate = **NO**.
