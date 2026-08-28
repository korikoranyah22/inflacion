# BCRA legacy PTA route audit — V77

## Result
A legacy BCRA primary archive filename grammar was recovered from indexed BCRA binaries:

`pta_<entity code without leading zeroes>_<YYYYMM>.pdf`

Observed primary examples include Banco Galicia (`00007` → `pta_7_201712.pdf`) and BBVA Francés (`00017` → `pta_17_201709.pdf`). This is strong evidence for the archive grammar, **not proof that a 2023 candidate URL remains live**.

Applying current/2023 entity codes yields candidate September-2023 paths for BNA (`00011`), BAPRO (`00014`) and Ciudad (`00029`). Automated access cannot server-test these unindexed derived URLs, so they are frozen as `INFERRED_NOT_SERVER_VERIFIED` and routed to manual retrieval.

## Why this matters
FIX SCR independently states that BAPRO's separated and consolidated interim statements as of 30-09-2023 were publicly available at BCRA. That materially strengthens the existence hypothesis for a BCRA-hosted 9M package, although it does not prove the legacy filename survived unchanged through 2023.

## Hard gate
No candidate route changes strict coverage. Only a recovered binary whose basis and four pass-flow legs can be audited may enter the Q4 bridge.
