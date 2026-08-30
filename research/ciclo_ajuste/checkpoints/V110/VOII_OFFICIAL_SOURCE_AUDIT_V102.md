# Banco VOII S.A. — official issuer / raw audit V102

## Basis
Both documents are issuer financial statements for Banco VOII S.A. itself. The 30/09/2023 document is explicitly **Estados Financieros Intermedios Condensados** and the 31/12/2023 document is the annual financial statement set. The Annex Q tables directly disclose counterparty legs; no six-digit semantic inference is needed.

## 9M 30/09/2023 — Annex Q
- repo income total: **934,677k**;
- BCRA income: **0**;
- Other-FI income: **934,677k**;
- repo expense total: **86,752k**;
- BCRA expense: **0**;
- Other-FI expense: **86,752k**.

Raw entity `00312` matches exactly: `511027=934,677k`, `521022=86,752k`.

Official URL: https://www.voii.com.ar/wp-content/uploads/2023/07/Banco-Voii-SA-ESF-2023-09.pdf

## FY 31/12/2023 — Annex Q
- repo income total: **2,881,991k**;
- BCRA income: **0**;
- Other-FI income: **2,881,991k**;
- repo expense total: **132,980k**;
- BCRA expense: **0**;
- Other-FI expense: **132,980k**.

Raw entity `00312` again matches exactly: `511027=2,881,991k`, `521022=132,980k`.

Official URL: https://www.voii.com.ar/wp-content/uploads/2023/07/Banco-Voii-SA-ESF-2023-12-Final.pdf

## Q4 bridge
Frozen factor: `1.532908152197492`.

- Q4 BCRA income = **0k**;
- Q4 BCRA expense = **0k**;
- Q4 Other-FI income = **1449217.007028504769916k**;
- Q4 Other-FI expense = **-2.848019436825984k**.

The small negative expense residual is retained exactly under the project rule forbidding aesthetic zero-clamping.

## Verdict
`EXACT_ANALYTICALLY_RESOLVED_SOURCE_PRESERVATION_HOLD`.

The two issuer PDFs were web-verified, including visual inspection of the Annex Q pages, but the execution environment could not persist their original bytes. Under the post-V96 source rule, VOII is not promoted until both binaries are physically preserved and SHA-256 recorded.
