# Auditoría V102 — VOII exact + Banco Rioja mismatch falsifier

## Frozen strict state
- exact entities: **24**;
- asset numerator: **57,803,557.512 million ARS**;
- system denominator: **96,697,695.5 million ARS**;
- strict coverage: **59.7775957463226204806504411472763588249111893261199797672530882599989158997072479353967644%**;
- closed-network gate: **NO**;
- Sep→Dec factor: **1.532908152197492**.

## Banco VOII S.A.
Official issuer Annex Q directly identifies all four repo-result legs in both 9M and FY. Raw BCRA entity `00312` reconciles exactly in both periods.

9M: BCRA income/expense `0/0`; Other-FI income/expense `934,677 / 86,752k`.
FY: BCRA income/expense `0/0`; Other-FI income/expense `2,881,991 / 132,980k`.

Q4: BCRA `0/0`; Other-FI income **1449217.007028504769916k**; Other-FI expense **-2.848019436825984k**. The tiny negative residual is preserved.

VOII is analytically exact but remains outside strict because the two original issuer PDFs are not physically preserved with SHA-256. If rescued, candidate coverage becomes **59.81442386494102126766816278470669448373772258098953350961709320156445713848475323799210912942594377% / 25 entities**.

## Banco Rioja
FY Annex Q is directly BCRA-only: income **14,409,056k**, expense **7,844k**. Dec raw candidate `521108=7,844k` matches the expense, but `511108=14,250,267k` misses income by **158,789k**.

No crosswalk is accepted. This is explicitly preserved as evidence against global six-digit account semantics.

## Combined source-hold frontier
- BACS+BMR+BTF+VOII if their seven PDFs are preserved: **60.25837167339732517203576997344264528000049391042623140899981427168551291897126958935644955468457881% / 28 entities**.
- Hipotecario+Columbia+BACS+BMR+BTF+VOII if all eleven promotion-blocking PDFs are preserved: **61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549% / 30 entities**.
- closed-network gate remains **NO** in either scenario.
