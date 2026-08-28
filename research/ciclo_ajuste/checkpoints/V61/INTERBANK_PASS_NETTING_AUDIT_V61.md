# INTERBANK PASS NETTING AUDIT V61

## Accounting schema

Anexo Q separates pass/caución interest flows by counterparty on both sides:

- income from passes with BCRA;
- income from passes with other financial institutions;
- expense from passes with BCRA;
- expense from passes with other financial institutions.

Therefore the correct system identities are conceptually:

`BCRA_NET_PASS_FLOW = Σ pass_income_BCRA - Σ pass_expense_BCRA`

`INTERBANK_NET_PASS_FLOW = Σ pass_income_otherFI - Σ pass_expense_otherFI`

The generic IEF `primas por pases` component cannot be assigned to BCRA without reconciling these flows.

## Consolidation gate

BCRA historical glossary says balance-sheet consolidated assets/liabilities deduct operations between financial institutions, while `resultado consolidado` explicitly says results from permanent participations in local financial institutions are removed. That text does **not** explicitly state that interbank pass interest income/expense is removed from the published result series.

Thus:

```text
SYSTEM_INTERBANK_PASS_RESULT_NETTING_IN_IEF
= NOT_ESTABLISHED
```

Economic cancellation in a complete closed system is a hypothesis to test, not a publication convention to assume.

## Entity evidence

### Galicia Q4 reconstructed
- BCRA pass income: 228,495,363 thousand Dec-23 ARS.
- Other-FI pass income: 6,150,559.
- Other-FI pass expense: 1,422,129.
- Net other-FI pass flow: 4,728,430.

### Banco Nación FY2023
- BCRA pass income: 766,170,918 thousand ARS.
- Other-FI pass income: 3,980,009.
- Pass expenses: zero in the published A-Q table.
- Yet year-end passive-repo stock with other FIs: 199,417,218 thousand ARS.

This is a direct falsifier of `year-end pass stock counterparty = period pass-income counterparty`.
