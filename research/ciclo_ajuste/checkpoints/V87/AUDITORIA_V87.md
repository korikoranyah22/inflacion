# Auditoría V87

## 1. Scope

V87 keeps the V85/V86 rule: **no universal six-digit BCRA raw-account mapping**. A bank can only enter strict Q4 four-leg coverage when its own issuer/regulatory presentation validates the counterparty crosswalk or directly prints the split.

Frozen Sep→Dec re-expression factor: `1.532908152197492`.

## 2. Banco Patagonia — promotion

Separated 9M:
- BCRA income 0
- other-FI income 129,800,318k
- BCRA expense 0
- other-FI expense 313,196k

Separated FY:
- BCRA income 0
- other-FI income 342,520,451k
- BCRA expense 0
- other-FI expense 982,789k

The annual separated Annex Q assigns the entire repo income/expense to Other Financial Institutions. BCRA raw entity 00034 reproduces all source totals exactly.

Q4:
- BCRA income = **0k**
- BCRA expense = **0k**
- other-FI income = **143548485.379973139597544k**
- other-FI expense = **502688.298364354295568k**

## 3. Citibank — promotion

Official 9M Note 25 directly prints:
- BCRA pass income **421,911,207k**
- other-FI pass income **1,320,406k**
- no pass-expense line.

Official FY Note 25 directly prints:
- BCRA pass income **918,291,333k**
- other-FI pass income **4,468,974k**.
FY Annex-Q expense has no pass-expense category.

Q4:
- BCRA income = **271540204.286216447907156k**
- other-FI income = **2444912.878389518378248k**
- both pass expenses = **0k**

Issuer presentation is primary; raw does not override it.

## 4. Banco Supervielle — prior bound collapsed

FY separated Annex Q is reproduced exactly by entity raw:
- `511108` = BCRA income = 219,708,132k
- `511027 + 515034` = other-FI income = 3,285,840k
- `521022 + 525042` = other-FI expense = 1,235,416k
- BCRA expense = 0.

At 9M the identical account set sums exactly to the separated published totals:
- BCRA income = 86,904,713k
- other-FI income = 1,998,572k
- other-FI expense = 420,309k
- BCRA expense = 0.

This is an entity-specific mapping, not a system rule.

Q4:
- BCRA income = **86491188.977916638420204k**
- other-FI income = **222212.688446354018576k**
- BCRA expense = **0k**
- other-FI expense = **591120.907458024334972k**

## 5. Santander and BNA

Santander: official separated 9M pass-income total is exact and reconciles raw, but accumulated BCRA/other-FI split is not printed. FY shows why naive six-digit mapping cannot be used. **No promotion.**

BNA: FY separated presentation proves `521007` cannot be mechanically treated as a strict pass-expense leg. September remains unresolved. **No promotion.**

## 6. Coverage

New exact-asset numerator = **48590481.063 million ARS**.
System denominator = **96697695.5 million ARS**.
Strict Q4 four-leg coverage = **50.2498852860459327078792689532089210957462786690712810213766%**.
Increment vs V86 = **7.6482098469451115306051942054813498631962786690712810213766 pp**.
Exact entities = **11**.

For the first time strict coverage exceeds 50% of banking assets. This is **majority compatible asset coverage**, not a closed-network proof. Gate remains **NO** because the system network remains materially open.
