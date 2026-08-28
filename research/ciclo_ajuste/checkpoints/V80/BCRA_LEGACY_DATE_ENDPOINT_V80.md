# BCRA legacy dated endpoint — V80

## Result
The September-2023 regulatory archive remains **in scope but the exact `.7z` href is not yet machine-resolved**.

### What is now stronger than V79
- The current official BCRA page explicitly says that total-entity open data are distributed in a `.7z` containing `.txt` files plus a PDF description.
- The official catalog gives temporal coverage **07/2021–06/2025**, therefore **2023-09 is inside the published archive family**.
- The old BCRA interface used a deterministic dated-page parameter `Entidades_financieras.asp?fecha=YYYYMM`. This pattern is independently preserved in public-sector and academic references (e.g. `fecha=202012`, `fecha=202406`).
- Therefore the page candidate for the target month is:
  `https://www.bcra.gob.ar/PublicacionesEstadisticas/Entidades_financieras.asp?fecha=202309`
  This is a **dated page route inference**, not a fabricated binary filename.

## Remaining blocker
The current indexed HTML exposes the selector but not the client-side generated `.7z` href. Automated retrieval cannot currently extract the exact historical download target.

## Manual rescue protocol
If a normal browser can open the dated page and exposes a control similar to **Datos Abiertos / Descargar / .7z**, save the `.7z` exactly as served or copy its exact href. A successful rescue should be preserved byte-for-byte and fingerprinted before extraction.

## Frozen target fields
- `0301060100` — pass income, BCRA
- `0301060200` — pass income, other financial entities
- `0302030100` — pass expense, BCRA
- `0302030200` — pass expense, other financial entities

No stock proxy and no consolidated-to-individual substitution is admissible.
