# Banco de La Pampa S.E.M. — official-source audit V93

## Official FY issuer Annex Q

Banco de La Pampa's official **Memoria y Balance General 2023** contains Annex Q (page 95 of the document / PDF page index 94 in the web renderer). For 31/12/2023 it reports, in thousands of ARS:

- pass income total: **54,227,326**;
- BCRA pass income: **54,227,326**;
- other-financial-institutions pass income: **0**;
- pass expense total: **5,110**;
- other-financial-institutions pass expense: **5,110**;
- therefore BCRA pass expense: **0** in the issuer taxonomy.

Primary issuer source:
`https://www.bancodelapampa.com.ar/files/files/Dise%C3%B1o%20Memoria%20y%20Balance%20General%202023%20web.pdf`

The issuer note on operations of repo/pase also states FY-2023 positive results from active repos of **54,227,326**, providing an independent within-document control.

## CNV individual interim filing control

The CNV public registry identifies Banco de La Pampa's 30/09/2023 filing as **TIPO BALANCE: INDIVIDUAL**, filing **#3121031**, submitted 28/11/2023. Publicview:
`https://aif2.cnv.gov.ar/Presentations/publicview/15298564-F56D-495D-A7C6-0DEDC1A77882`

The attachment body is not required for V93 promotion because the strict counterparty classification comes from the same-entity/same-year FY issuer/raw one-to-one reconciliation; the CNV entry is used only to corroborate that the interim target basis is individual.

## Entity-specific BCRA raw reconciliation

Preserved BCRA raw entity `00093` matches the FY issuer Annex Q one-to-one:

- Dec `511108 = 54,227,326k` ↔ BCRA pass income `54,227,326k`;
- Dec `521022 = 5,110k` ↔ other-FI pass expense `5,110k`;
- no `511027` row ↔ other-FI pass income `0`;
- issuer Annex Q shows no BCRA pass-expense leg ↔ BCRA pass expense `0`.

For Sep-2023 the same entity raw values are `511108 = 19,150,613k` and `521022 = 3,334k`, with no `511027` row. V93 applies these identities **only to Banco de La Pampa and only within the same 2023 entity/year validation**. It does not infer a universal meaning for BCRA six-digit accounts.

## Q4 result

Using frozen Sep→Dec factor `1.532908152197492`:

- BCRA income: **24871195.212720731137404k**;
- BCRA expense: **0k**;
- other-FI income: **0k**;
- other-FI expense: **-0.715779426438328k**.

The sub-thousand negative other-FI expense differencing residual is preserved and not clamped.
