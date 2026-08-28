# Handover — Ciclo de ajuste V85 → V86

**Fecha:** 2026-08-28

## Frozen strict state

- coverage = **36.334782973188844%**
- exact eligible entities = ICBC, Banco de Valores, Macro, Credicoop, BAPRO, Ciudad, **Galicia**
- exact asset numerator = 35134897.8 million ARS
- denominator = 96697695.5 million ARS
- gate = NO
- Sep→Dec factor = 1.532908152197492

## V85 promotion — Galicia

Issuer 9M Note 18: BCRA income 149,917,156; otherFI income 9,897,718; pass expense 3,419,619 entirely OtherFI, hence BCRA expense 0.
Issuer FY: BCRA income 458,304,594; otherFI income 21,322,852; pass expense 6,664,091 entirely OtherFI, hence BCRA expense 0.
Q4 Dec-homogeneous: BCRA income 228495363.41333684; BCRA expense 0; otherFI income 6150559.389648143; otherFI expense 1422129.1574905645.

## Critical rejected hypothesis

Do **not** promote the remaining banks directly from the IEF six-digit raw. Santander FY is a direct counterexample: raw 511027 does not equal Annex-Q otherFI; Annex Q splits almost all pass income to BCRA. The raw universe covers 63 banks and reconciles assets, but counterparty detail can live below the six-digit account level / presentation mapping.

The previously mentioned tentative ~58.4% shortcut is rejected and must not be cited as a result.

## BNA

Still pending. Raw 521007: Sep 2; Oct 11,898,899; Nov 27,451,638; Dec 49,898,208. Separated FY Annex Q has pass expense 0 and places 49,898,208 under other subordinated negotiable obligations. Need compatible 9M presentation or explicit BNA subaccount mapping.

## V86 priorities

1. BNA full separated 30/09/2023 Annex Q / presentation crosswalk.
2. Santander separated 30/09/2023 Annex Q split.
3. For any additional bank, require issuer/regulatory presentation validation before using raw six-digit accounts.
4. Keep closed-network gate NO until coverage materially closes.
