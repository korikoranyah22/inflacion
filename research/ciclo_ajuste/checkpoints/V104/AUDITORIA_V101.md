# Auditoría V101 — BACS + BMR + BTF exact analytical resolution

## Frozen strict state
- exact entities: **24**
- numerator: **57803557.512 million ARS**
- coverage: **59.7775957463226204806504411472763588249111893261199797672530882599989158997072479353967644%**
- closed-network gate: **NO**
- strict promotions in V101: **0**

## BACS
- 9M separated direct: BCRA income 23,876,889k; Other-FI income 386,346k; Other-FI expense 2,167k; BCRA expense 0.
- FY separated direct: BCRA income 63,177,601k; Other-FI income 610,427k; Other-FI expense 14,063k; BCRA expense 0.
- Q4: BCRA income **26576523.202785377437612k**; Other-FI income **18194.067031107755768k**; Other-FI expense **10741.188034188034836k**; BCRA expense 0.
- analytical gate: PASS.
- physical-source gate: FAIL/PENDING.

## Banco Municipal de Rosario
- 9M separated BCRA income 5,210,550k.
- FY annual separated amount 11,420,465k, independently fixed to 31/12/2023 by separated Note 6 despite a wrong nine-month label printed in annual Annex Q.
- raw income/expense totals reconcile exactly in both periods; no other repo-result account exists.
- Q4 BCRA income **3433170.427567358059400k**; other three legs 0.
- analytical gate: PASS.
- physical-source gate: FAIL/PENDING.

## Banco Provincia de Tierra del Fuego
- FY issuer Annex Q BCRA repo income 14,938,203k and Other-FI income zero.
- Dec raw 511108 matches exactly; Sep same BTF account = 7,194,047k.
- exhaustive interest reconciliations exact; no repo-expense raw account.
- Q4 BCRA income **3910389.706408089269876k**; other three legs 0.
- analytical gate: PASS.
- physical-source gate: FAIL/PENDING.

## Candidate coverage only after source preservation
- BACS alone: **59.9314924738821723005798002704211291157398885478092908636069822367173165983050754296414437%** / 25 entities.
- BMR alone: **59.9283800429349425395561779442820330707881244181253523254853576112369709989624313228850423%** / 25 entities.
- BTF alone: **59.9168625306070505061829524158618650844683263418619940120496460021635158823407534050281477%** / 25 entities.
- BACS+BMR+BTF: **60.2215435547789243850180483360123096211739606555566776666358093301199716801937642867611049%** / 27 entities.
- all five resolved source-holds (Hipotecario+Columbia+BACS+BMR+BTF): **61.8187344102735106029491674907599013049902518100857946506077799961634039148326962972969713%** / 29 entities.

No candidate coverage is substituted for strict coverage until the issuer binaries are physical and hash-verified.
