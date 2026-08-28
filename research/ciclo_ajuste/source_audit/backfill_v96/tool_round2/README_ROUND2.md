# Source Backfill V96 — round 2

Generated 2026-08-28 after archaeology of V32, V48, V50 and V52–V59 plus reconciliation with historical RAW source manifests.

- actionable direct binaries: **35**
- priority: P2 historical/source-completeness; P0/P1 remain zero
- run `RUN_ALL_GAPS.cmd`; output goes to `./results/`
- `bolmetes.pdf` uses the historical `www.bcra.gob.ar` URL instead of the `web2` endpoint that returned 401
- extensionless BAPRO/Credicoop download endpoints are explicitly typed as PDF for validation

This tool only downloads. Ingest only `DOWNLOAD_OK` members after independent magic-byte, size and SHA-256 validation.
