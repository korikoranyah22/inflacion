# HANDOVER CODEX — V79 → V80

## Frozen strict coverage
**23.543324980273%** — ICBC + Banco de Valores + Macro + Credicoop + BAPRO.

## Key new fact
BNA FY-2023 proves basis divergence:
- separated FY: BCRA income 766,170,919k; otherFI income 0; pass expenses 0.
- consolidated FY: BCRA income 766,170,918k; otherFI income 3,980,009k; pass expenses 0.

Therefore never bridge consolidated 9M to separated FY.

## Highest-leverage V80 route
1. Resolve the BCRA September-2023 open-data `.7z` endpoint. BCRA catalog coverage explicitly includes 2023-09. Extract TRIMANUA entity rows for BNA and Banco Ciudad:
   - 0301060100
   - 0301060200
   - 0302030100
   - 0302030200
2. In parallel, keep searching for the exact issuer full separated 30-09-2023 BNA package under the confirmed `Institucional_BalancesTrimestrales_...` file family.
3. Then Banco Ciudad separated 30-09-2023.

## User rescue protocol
Ask Miyu only when a **concrete target** exists and automated retrieval fails. Do not send speculative filename guesses.

## Hard gate
No pass-stock substitutions. No consolidated-to-individual promotion. No system cancellation claim until near-full exact four-leg coverage.
