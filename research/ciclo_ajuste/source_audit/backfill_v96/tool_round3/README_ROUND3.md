# Source Backfill V96 — Round 3

Esta cola contiene **26** fuentes P2 todavía no preservadas físicamente.

- 25 endpoints directos fueron descubiertos desde páginas oficiales BCRA durante archaeology batch4.
- `bcra_boldat202505_tipo_titular` permanece como retry: el host legado `www7.bcra.gob.ar` no resolvió en Round 2.
- Ejecutar `RUN_ALL_GAPS.cmd`.
- Los resultados y el payload se guardan en `./results/`.
- Ingerir únicamente filas `DOWNLOAD_OK` y validar SHA-256 + magic bytes.

No cambia V96 numérico; esto es source-completeness histórica.
