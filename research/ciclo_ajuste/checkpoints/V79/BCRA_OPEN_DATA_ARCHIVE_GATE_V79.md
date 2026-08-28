# BCRA OPEN-DATA ARCHIVE GATE — V79

The BCRA's current **Información sobre entidades financieras** page explicitly states that the monthly publication is built from entity regulatory reporting and that the complete entity-level open data are available in a compressed `.7z` containing `.txt` files plus a PDF describing the content.

The BCRA data catalog marks this dataset as **monthly**, available in **PDF/TXT**, with temporal coverage **07/2021–06/2025**. Therefore **September 2023 is explicitly inside the catalogued archive window**.

For this project the target TRIMANUA items remain frozen:

- `0301060100` — pass-interest income, BCRA
- `0301060200` — pass-interest income, other financial institutions
- `0302030100` — pass-interest expense, BCRA
- `0302030200` — pass-interest expense, other financial institutions

## Current gate
The web page exposes the archive selector dynamically and the exact historical `.7z` endpoint is not present in the crawlable HTML. Thus V79 does **not** claim the raw file was recovered.

## Consequence
The regulatory route is now **scope-confirmed but endpoint-unresolved**, not speculative. It remains the highest-leverage fallback because one September-2023 archive could potentially close both BNA and Banco Ciudad on a consistent regulatory basis.
