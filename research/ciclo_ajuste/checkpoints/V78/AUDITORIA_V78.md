# AUDITORÍA V78

## Breakthrough
The user-recovered `document.pdf` is the full Banco de la Provincia de Buenos Aires interim package for the nine months ended 30-09-2023. It contains both consolidated and **separated** statements. The separated table of contents identifies Note 14 (interest income) and Note 15 (interest expense), and PDF pp. 94-95 expose the required pass counterparty split.

## 9M separated four legs
- income BCRA = **412,079,305k**
- income otherFI = **0** (pass-income total equals the BCRA subline exactly)
- expense BCRA = **0** (pass-expense total equals the otherFI subline exactly)
- expense otherFI = **1,584k**

These are on a separated/individual basis and in constant pesos at 30-09-2023.

## FY crosswalk
Inherited official BAPRO FY-2023 separated Annex Q:
- income BCRA = 1,040,489,497k
- income otherFI = 0
- expense BCRA = 0
- expense otherFI = 2,428k

The note taxonomy and annual Annex-Q taxonomy map one-for-one to the same pass-interest counterparty legs.

## Q4 bridge
Frozen method:
`Q4_Dec = FY_Dec - 9M_Sep * 1.532908152197492`

Results:
- income BCRA = **408809771.013623k**
- income otherFI = **0k**
- expense BCRA = **0k**
- expense otherFI raw residual = **-0.126513080827k**

The expense-otherFI residual is only ~126 pesos while both source tables report integer thousands of pesos. Conservative propagated rounding tolerance is ±1.266454076099k. Therefore the residual is reconciled to **0k at reported precision**, not treated as a negative flow.

## Coverage
Strict exact Q4 four-leg asset coverage rises from **14.564124643487%** to **23.543324980273%**, a gain of **8.979200336786 percentage points**.

This is still an open subset, not a closed banking-system network. No system-wide cancellation claim is permitted.
