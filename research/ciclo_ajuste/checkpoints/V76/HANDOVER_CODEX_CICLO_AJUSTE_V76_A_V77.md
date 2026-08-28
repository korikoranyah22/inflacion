# HANDOVER CODEX — V76 → V77

## Frozen state

```text
STRICT_Q4_FOUR_LEG_EXACT = ICBC + Banco de Valores + Banco Macro + Banco Credicoop
STRICT_Q4_FOUR_LEG_EXACT_COVERAGE = 14.564124643487498% bank assets
BCRA_TRIMANUA_DESIGN = 4401
BCRA_PASS_INCOME_BCRA = 0301060100
BCRA_PASS_INCOME_OTHER_FI = 0301060200
BCRA_PASS_EXPENSE_BCRA = 0302030100
BCRA_PASS_EXPENSE_OTHER_FI = 0302030200
BNA_9M_CONDENSED = PRIMARY_CONTROL_ONLY_NO_COUNTERPARTY_FLOW_SPLIT
BAPRO_SEP2023_DISCIPLINE = PRIMARY_STOCK_CONTROL_ONLY
BAPRO_SEPARATED_NOTE_PATTERN = CONFIRMED_IN_2024_ISSUER_FILING
CIUDAD_SEP2023_ARCHIVE = CONFIRMED; CONSOLIDATED_CONTROL_ONLY
BCRA_202309_OPEN_DATA_7Z = ENDPOINT_UNRESOLVED
HTML_MODIFICATION = FORBIDDEN
```

## V77 priority

1. Resolve the BCRA historical `.7z`/entity-quarter path and test whether reported quarterly `TRIMANUA` rows can be recovered by entity/code.
2. Search BNA 30-09-2023 separate/individual notes specifically for `0301060100`, `0301060200`, `0302030100`, `0302030200` concepts.
3. Search BAPRO 30-09-2023 historical interim full filing; target the separated pass-income/pass-expense note pattern demonstrated by its 2024 filing.
4. Search Ciudad individual/separate 30-09-2023 package; consolidated remains control-only.
5. Only bridge to Q4 after basis, unit and counterparty taxonomy compatibility are explicit.

## Hard gates
No stock→flow substitution. No consolidated→individual promotion. No FY→Q4 substitution. No inferred counterparty split. No zero from silence. Preserve primary binaries and hashes.
