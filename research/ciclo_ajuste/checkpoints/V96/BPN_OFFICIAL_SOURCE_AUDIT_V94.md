# Banco Provincia del Neuquén S.A. — official-source audit V94

## Official issuer FY-2023

BPN's own `Memorias y Balances` index links **Balance 2023 General**. The first page identifies the document as Banco Provincia del Neuquén S.A. financial statements at 31/12/2023 and 2022.

Official index:
`https://www.bpn.com.ar/Institucional/MemoriayBalances`

Official Balance 2023 General:
`https://apiapp.bpn.com.ar/Resources/Files/3c8ae1e827054171978cb213a56891df.pdf`

The FY-2023 **Annex Q, page 83** reports, in thousand ARS in 2023 homogeneous currency:

- pass income — BCRA: **129,240,317**;
- pass income — Other Financial Institutions: **0** (no amount in the 2023 column);
- no `Por operaciones de pase` line appears under interest expenses, so BCRA pass expense = **0** and other-FI pass expense = **0**.

This matches preserved BCRA raw entity `00097` at Dec-2023 one-to-one: `511108=129,240,317k`, while `511027`, `521007`, and `521022` are absent from the full nonzero entity file.

## Standalone / target-basis control

BPN's official 2023 Pillar-III / public-disclosure document states: **`El BPN S.A. no forma parte de grupos económicos.`**

Official source:
`https://apiapp.bpn.com.ar/Resources/Files/06c53b4c8d1a4285ae8685e7d02644a2.pdf`

Therefore no consolidated-vs-separated group substitution is being made in this promotion.

## 2024 comparator — taxonomy control only

BPN's official Balance 2024 General repeats FY-2023 inside a 2024 homogeneous-currency comparative. Its Note 3 and Annex Q show 2023 pass results entirely against BCRA and no pass-expense category. Because those 2023 comparative figures are reexpressed to **2024** homogeneous currency, V94 uses them only as a taxonomy/control check, **not** as the nominal FY-2023 value for Q4 differencing.

Comparator:
`https://apiapp.bpn.com.ar/Resources/Files/82d95330e8d6472b90d506e198bd6549.pdf`

## Same-entity Sep bridge

Preserved BCRA raw entity `00097` at Sep-2023 contains `511108=50,821,306k` and no `511027`, `521007`, or `521022`. V94 applies the FY-validated account identity only to this same entity and same year.

It does **not** alter the global rule:

`SIX_DIGIT_RAW_ACCOUNT_NAME != UNIVERSAL_ANNEX_Q_COUNTERPARTY_CROSSWALK`

## Q4 result

Using frozen Sep→Dec factor `1.532908152197492`:

- BCRA income: **51335922.727276686635448k**;
- BCRA expense: **0k**;
- other-FI income: **0k**;
- other-FI expense: **0k**.
