# Banco de Formosa S.A. — official-source audit V95

## Argentina / entity / basis controls

Only Argentine issuer/regulator evidence is used in this V95 promotion. Banco de Formosa's official website identifies the institution in Formosa, República Argentina. The official FY-2023 package contains an independent-auditor report explicitly covering **estados financieros separados** at 31/12/2023.

Official FY package:
`https://www.bancoformosa.com.ar/Multimedios/pdfs/117598.pdf`

Official 9M package:
`https://www.bancoformosa.com.ar/Multimedios/pdfs/117571.pdf`

Official 2023 integrated report:
`https://www.bancoformosa.com.ar/Multimedios/pdfs/118254.pdf`

## 9M separated Annex Q — direct four-leg opening

The official 30/09/2023 **separated** Annex Q reports, accumulated at 9M:

- BCRA pass income: **3,377,992k**;
- Other-FI pass income: **1,420k**;
- BCRA pass expense: **0k**;
- Other-FI pass expense: **78,619k**.

Preserved BCRA entity `00315` raw at Sep matches one-to-one:
`511108=3,377,992k`, `511027=1,420k`, `521022=78,619k`, and no `525042`.

This establishes a **Banco-de-Formosa-specific** mapping for those three accounts at 9M; it is not generalized to any other bank.

## FY-2023 exact reconstruction

The official FY package states annual results from active pass operations of **13,951,639k** and annual negative results from passive pass operations of **126,499k**. Banco Formosa's official 2023 integrated report separately publishes **Pases = 13,949,461k** within liquidity-excess income, exactly matching Dec raw `511108` and the account already validated as BCRA pass income at 9M.

Dec raw entity `00315` contains:

- `511108=13,949,461k`;
- `511027=2,178k`;
- `521022=120,514k`;
- `525042=5,985k`.

Income reconciliation is exact:
`13,949,461 + 2,178 = 13,951,639`.
Therefore `511027=2,178k` is the Other-FI income leg under the same Formosa-specific identity validated at 9M.

Expense reconciliation is also exact:
`120,514 + 5,985 = 126,499`.
Because `521022` was directly identified by Formosa's separated 9M Annex Q as the Other-FI expense leg, the remaining `5,985k` is the BCRA expense leg **by exact entity-specific residual within the two-counterparty Annex-Q taxonomy**. This does not assert any universal meaning for account `525042`.

## Q4 homogeneous bridge

Frozen Sep→Dec factor: `1.532908152197492`.

Q4 four legs (thousand ARS, Dec-2023 homogeneous):

- BCRA income: **8771309.525142089603936**;
- BCRA expense: **5985.000000000000000**;
- Other-FI income: **1.270423879561360**;
- Other-FI expense: **-1.706017614623548**.

The tiny negative Other-FI expense differencing residual is preserved and not clamped.
