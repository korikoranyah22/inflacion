# AUDITORIA V64

## Inputs congelados
- Base: V63.
- IPC Sep-2023 = 2304.9.
- IPC Dec-2023 = 3533.2.
- Factor = 1.532908152197.
- Regla: Q4 = FY_Dec - 9M_Sep × factor.

## ICBC — trazabilidad
### 9M 30/09/2023 (miles de pesos constantes de septiembre)
- pass income total: 156,034,952
- BCRA income: 155,837,409
- other-FI income: 197,543
- pass expense total: 889,799
- BCRA expense: 0
- other-FI expense: 889,799

### FY 31/12/2023 (miles de pesos constantes de diciembre)
- pass income total: 438,625,589
- BCRA income: 438,280,940
- other-FI income: 344,649
- pass expense total: 2,307,851
- BCRA expense: 0
- other-FI expense: 2,307,851

### Q4 reconstruido
- BCRA net: 199,396,505.326565 thousand ARS.
- other-FI net: -902,037.134192 thousand ARS.

Identity checks:
- Sep income total = BCRA + otherFI: PASS
- Sep pass expense = otherFI expense: PASS
- FY income total = BCRA + otherFI: PASS
- FY pass expense = otherFI expense: PASS

## Basis gate
ICBC statements are labeled for Industrial and Commercial Bank of China (Argentina) S.A.U. and do not provide a consolidated label on the Annex Q used. V64 therefore marks them `INDIVIDUAL_STANDALONE`. It is not pooled with consolidated rows for a system netting claim.

## Household mapping audit
BCRA publication structure provides holder-type stock splits, including mortgage and pledged loans. That is sector evidence at stock level, not an interest-flow identity. No stock-to-flow conversion was performed.

## Forbidden inferences checked
- stock as pass-flow counterparty proxy: NOT USED.
- open subset as system cancellation: NOT USED.
- product as household institutional sector: NOT USED.
- +7.7 pp as BCRA: NOT USED.
- household cost = bank net profit: NOT USED.
- HTML modification: NOT PERFORMED.
