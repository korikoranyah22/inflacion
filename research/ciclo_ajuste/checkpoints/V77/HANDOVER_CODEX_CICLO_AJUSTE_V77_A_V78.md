# HANDOVER CODEX — V77 → V78

## Frozen state

```text
STRICT_Q4_FOUR_LEG_EXACT = ICBC + Banco de Valores + Banco Macro + Banco Credicoop
STRICT_Q4_FOUR_LEG_EXACT_COVERAGE = 14.564124643487498% bank assets
BCRA_PTA_LEGACY_FILENAME_GRAMMAR = pta_<entity_code_without_leading_zeroes>_<YYYYMM>.pdf
BNA_202309_PTA_CANDIDATE = pta_11_202309.pdf (NOT SERVER VERIFIED)
BAPRO_202309_PTA_CANDIDATE = pta_14_202309.pdf (NOT SERVER VERIFIED)
BAPRO_202309_ISSUER_CANDIDATE = EEFF_unificado_30092023 (NOT SERVER VERIFIED)
BAPRO_9M_SEPARATED_EXISTENCE = INDEPENDENTLY CORROBORATED BY FIX SCR
CIUDAD_202309_PTA_CANDIDATE = pta_29_202309.pdf (NOT SERVER VERIFIED)
BCRA_TRIMANUA_CODES = 0301060100/0200 + 0302030100/0200
HTML_MODIFICATION = FORBIDDEN
```

## V78 priority
1. Ingest any user-recovered candidate binary unchanged; fingerprint/hash it.
2. Verify target basis (separated/individual) and 9M period.
3. Extract four pass-flow legs from Note income/expense or exact TRIMANUA mapping.
4. Crosswalk 9M taxonomy to frozen FY Annex Q before Q4 bridge.
5. If no candidate URL works, mark each 404 explicitly and continue BCRA archive/UI/API discovery.

## Hard gates
No candidate URL = evidence. No stock→flow substitution. No consolidated→individual promotion. No absent-leg zero without explicit reconciliation. No HTML edits.
