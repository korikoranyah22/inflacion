# Source backfill ingest — V96

Date: 2026-08-28
Run: `20260828_160057`

## Result

- requested: **49**
- ingested after local SHA-256 + magic-byte revalidation: **47**
- failed / not ingested: **2**
- remaining P0: **0**
- remaining P1: **0**
- remaining P2: **2**
- issuer-registry binaries added to master `FUENTES.csv`: **23**
- existing master-catalog rows converted from URL-only to physical preservation: **24**

All `DOWNLOAD_OK` payload members were re-hashed independently and their PDF/ZIP/XLSX signatures were checked before copying into canonical repo paths. The original payload ZIP is intentionally not embedded because its binaries are now stored canonically in-tree.

## Remaining gaps

- gap 38 P2 — bcra_boldat202505_tipo_titular: curl: curl.exe : curl: (6) Could not resolve host: www7.bcra.gob.ar
En C:\Users\miyur\Downloads\SOURCE_BACKFILL_TOOL_V96_TLS_HOSTNAME_FIX\SOURCE_BACKFILL_TOOL_V96\Download-SourceBackfill.
ps1: 84 Carácter: 17
+         $meta = & $CurlCommand.Source @args 2> $stderr
+                 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (curl: (6) Could...ww7.bcra.gob.ar:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
 
curl: (6) Could not resolve host: www7.bcra.gob.ar
curl: (6) Could not resolve host: www7.bcra.gob.ar
curl: (6) Could not resolve host: www7.bcra.gob.ar
curl: (6) Could not resolve host: www7.bcra.gob.ar | IWR: No se puede resolver el nombre remoto: 'www7.bcra.gob.ar'
- gap 39 P2 — bcra_bolmetes_prestamos_titular: curl: curl.exe : curl: (22) The requested URL returned error: 401
En C:\Users\miyur\Downloads\SOURCE_BACKFILL_TOOL_V96_TLS_HOSTNAME_FIX\SOURCE_BACKFILL_TOOL_V96\Download-SourceBackfill.
ps1: 84 Carácter: 17
+         $meta = & $CurlCommand.Source @args 2> $stderr
+                 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (curl: (22) The ...rned error: 401:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError | IWR: Error en el servidor remoto: (401) No autorizado.

## TLS exception

1 source(s) required the downloader's narrowly-scoped `SEC_E_WRONG_PRINCIPAL` hostname bypass. This fact is preserved in `SOURCE_BACKFILL_RESULTS.csv`, the ingest CSV, and `FUENTES.csv`; binary integrity was still checked by magic bytes and SHA-256.

## Research state

This is a preservation-only operation. V96 remains frozen at **24 exact entities**, strict coverage **59.777595746322620480650441147276358824911189326119979767253088259998915899707248%**, closed-network gate **NO**. No promotion or numeric result changed.

P0/P1 preservation backlog is now zero, so source-preservation no longer blocks resuming V97. The repository is still not declared fully source-complete because two P2 direct-binary URLs remain unresolved.
