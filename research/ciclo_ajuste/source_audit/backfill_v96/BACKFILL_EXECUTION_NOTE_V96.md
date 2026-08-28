# Binary source backfill — execution note V96

Date: 2026-08-28

The Windows downloader completed a full 49-item run. **47/49** binaries were recovered and then independently revalidated during repository ingestion using file size, magic bytes and SHA-256. No URL-only source was promoted merely because it was web-readable.

- P0 remaining: **0**
- P1 remaining: **0**
- P2 remaining: **2**
- canonical ingest report: `SOURCE_BACKFILL_INGEST_REPORT_V96.md` / `.csv`
- remaining queue: `../../SOURCE_BACKUP_GAPS_V96_AFTER_BACKFILL.csv`
- run diagnostics: `runs/20260828_160057/SOURCE_BACKFILL_RESULTS.csv`

The two unresolved P2 items are the BCRA `www7` host that does not resolve and the BCRA methodological endpoint returning HTTP 401. They remain explicitly unpreserved.

The working downloader version under `tool/` includes PowerShell 5.1 encoding/path fixes, controlled curl→IWR fallback, Schannel revocation handling, null-safe stderr capture, and a narrowly scoped `SEC_E_WRONG_PRINCIPAL` retry that records TLS bypass metadata.

## Metadata correction

The Banco de San Juan official annex dated 14-03-2025 is a **2024/2023 comparative** source. It supplies the FY2023 comparator used in V89; it is not a standalone FY2023 issuance. This changes source-backup labeling only and has **no numerical or promotion impact**.

## Frozen research state

- checkpoint: V96
- exact entities: 24
- strict coverage: 59.777595746322620480650441147276358824911189326119979767253088259998915899707248%
- closed-network gate: NO

P0/P1 source preservation is now closed, so this audit no longer blocks resuming V97. Full `source-complete` status is still withheld until the two P2 direct-binary gaps are resolved or explicitly retired with evidence.
