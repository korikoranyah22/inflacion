# AUDITORÍA V63 — Full A-Q homogeneous panel and pass legs

## 1. Regulatory schema gate
The BCRA public Annex Q template explicitly requires four pass/caucion legs:

```text
income passes BCRA
income passes other financial institutions
expense passes BCRA
expense passes other financial institutions
```

Therefore, missing legs in entity research are a retrieval/coverage issue, not absence of a regulatory concept.

## 2. First exact Q4 four-leg entity: Banco Ciudad
Using the frozen homogeneous-currency differencing rule, with Sep→Dec factor 1.532908152197:

- Q4 income BCRA = 0
- Q4 expense BCRA = 0
- Q4 income other-FI = 370,794,209.077 thousand ARS
- Q4 expense other-FI = 327,736.123 thousand ARS
- Q4 net other-FI = 370,466,472.954 thousand ARS

This is an entity net position against the rest of the financial system, NOT evidence that interbank flows fail to cancel system-wide.

## 3. Macro
- Q4 BCRA pass income exact inherited: 83,520,202.827 thousand ARS.
- Q4 other-FI income exact inherited: 647,816.041.
- Q4 other-FI expense ≈ 2,711,008.836; approximation comes from rounded quarterly investor-report values for Q1-Q3.
- Do not elevate approximate expense to exact.

## 4. Open subset is not a cancellation test
For Macro+Ciudad, observed other-FI net is large and positive, but their counterparties can be banks outside the subset.

`SUBSET_INTERBANK_NET != SYSTEM_INTERBANK_CANCELLATION_TEST`.

A valid cancellation test requires near-full closed coverage, same accounting basis, and both income and expense legs.

## 5. Household/product gate
The direct product rows remain useful contractual candidates but not a strict institutional household-sector mapping. No system household point estimate is elevated.

## 6. IEF gate
The IEF +7.7 pp pass gap remains unreconciled by counterparty. No BCRA share or floor is restored.
