# Banco Hipotecario — raw / 9M presentation conflict, V88

## 9M separated issuer evidence

Official separated Note 19 reports accumulated 9M-2023 **interest on active passes = 157,005,580k**. BCRA raw entity `00044` gives `511108=156,378,434k` plus `511027=627,146k`, exact sum **157,005,580k**.

However, separated Note 20 lists the complete accumulated 9M interest-expense opening and contains **no pass-expense line**. Its published components sum to the note total without a pass item. At the same date, BCRA raw contains `521022=158,630k`.

## FY evidence

FY separated Annex Q explicitly reports:

- pass income BCRA = 405,189,892k;
- pass income other financial institutions = 1,052,960k;
- pass expense other financial institutions = 526,688k;
- pass expense BCRA = 0.

Those values nearly/exactly reproduce the Dec raw account values at published-thousand precision.

## Decision

**DO NOT PROMOTE.**

The 9M income side is exact, but the expense side demonstrates that an FY raw→presentation mapping cannot be blindly carried backward when the 9M issuer note omits the raw pass-expense account. The four-leg Q4 point remains `N/D_STRICT` until a same-period presentation/subaccount explanation resolves `521022=158,630k`.
