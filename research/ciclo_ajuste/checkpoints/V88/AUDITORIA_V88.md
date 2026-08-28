# Auditoría V88

## 1. Comafi promotion

The official separated 30/09/2023 package itself contains an interim Annex Q. It explicitly gives the 9M four-leg pass opening:

- BCRA income = **182,035,514k**
- other-FI income = **1,444,371k**
- BCRA expense = **0k**
- other-FI expense = **3,049k**

FY separated Annex Q gives:

- BCRA income = **415,554,305k**
- other-FI income = **3,699,870k**
- BCRA expense = **0k**
- other-FI expense = **5,328k**

Q4 Dec-homogeneous via frozen factor `1.532908152197492`:

- BCRA income = **136510581.599939314269112k**
- other-FI income = **1485781.919302356282468k**
- BCRA expense = **0k**
- other-FI expense = **654.163043949846892k**

This also nuances V86: Annex Q is annual as a required BCRA frequency, but an issuer may voluntarily publish an interim Annex Q.

## 2. Bancor promotion

FY separated Annex Q produces an exact one-to-one entity-specific mapping:

- raw `511108=96,947,854` → BCRA pass income **96,947,854k**;
- raw `511027=394,479` → other-FI pass income **394,479k**;
- raw `521022=206,308` → other-FI pass expense **206,308k**;
- BCRA pass expense = **0**;
- raw `515034=1,142` is exhausted elsewhere in the separated Annex Q and is explicitly excluded from pass.

Sep raw under the same Bancor-specific account identity:

- `511108=28,097,738`
- `511027=255,540`
- `521022=117,925`
- `515034=327` excluded.

The mapped Sep pass totals reconcile the official separated 30/09/2024 comparator for 30/09/2023 under a common re-expression factor:

- income factor = `3.0900470485282160320228228989960173211718235894982`
- expense factor = `3.0900148399406402374390502437990248039007843968624`

The tiny ratio difference is consistent with published-thousand rounding. The comparator is used only to validate the account set; the Q4 bridge still uses the frozen Sep→Dec-2023 factor.

Q4 Bancor:

- BCRA income = **53876602.361490745526904k**
- other-FI income = **2759.65078745289432k**
- BCRA expense = **0k**
- other-FI expense = **25539.8061521107559k**

## 3. Hipotecario falsification / hold

9M separated pass-active income **157,005,580k** exactly matches raw `511108+511027`. But the complete separated 9M interest-expense note contains no pass-expense line while raw has `521022=158,630k`. FY Annex Q later maps `521022` to other-FI pass expense.

Therefore an FY mapping is **not** carried backward blindly. Hipotecario remains strict N/D.

## 4. Coverage

Comafi assets = **1359542.041m ARS**.
Bancor assets = **1850325.878m ARS**.

Strict numerator: **51800348.982m ARS**.
Strict coverage: **53.569372790275027805600599861244883545337437746901%**.
Increment vs V87: **3.31948750422909509772133090803596244959115907783 pp**.
Exact entities: **13**.
Gate: **NO** — majority asset coverage is not a closed-network proof.
