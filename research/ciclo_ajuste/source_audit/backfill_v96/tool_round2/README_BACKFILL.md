﻿# Source backfill V96 — descargador reproducible

Este paquete existe porque la capa web de esta sesión puede **leer** muchos de los documentos remotos, pero no puede exportar sus bytes crudos al sandbox. El repo no debe marcar una fuente como preservada si el binario no existe físicamente y no tiene SHA-256 verificable.

## Uso rápido en Windows

- `RUN_P0_FIRST.cmd`: descarga sólo los 20 P0 (evidencia primaria usada en V89–V96). Recomendado primero.
- `RUN_ALL_GAPS.cmd`: intenta los 49 gaps P0+P1+P2.

El script usa primero `curl.exe` de Windows con redirecciones y reintentos; si falla, prueba `Invoke-WebRequest`.

Cada descarga se valida por firma binaria antes de aceptarse:

- PDF: `%PDF`
- ZIP/XLSX: `PK`
- XLS antiguo: firma OLE/CFBF

Para cada fuente válida calcula SHA-256 y tamaño. Las respuestas HTML/bloqueos que no coinciden con el tipo esperado quedan separadas en `rejected/` y **no cuentan como preservadas**.

Al finalizar genera `SOURCE_BACKFILL_PAYLOAD_V96_<fecha>.zip`. Subí ese ZIP a la conversación. Se incorporarán únicamente los binarios `DOWNLOAD_OK` al repo acumulativo, junto con URL, SHA-256, tamaño y fecha de recuperación.

## Trazabilidad

`SOURCE_BACKFILL_REQUEST_V96.csv` es la cola completa de 49 gaps después de las dos tandas arqueológicas. `REMOTE_BINARY_BACKFILL_STATUS_V96.csv` documenta el intento desde esta sesión. `SOURCE_METADATA_CORRECTIONS_V96.csv` contiene una corrección puramente documental sobre Banco de San Juan: la fuente de marzo de 2025 es un Anexo Q comparativo 2024/2023 que aporta la columna FY2023; no es una emisión standalone FY2023. No cambia ningún número ni la promoción V89.


## Windows PowerShell 5.1 compatibility fix

This package includes the V96 parser/encoding fix: `Download-SourceBackfill.ps1` is ASCII-only, reads the request CSV explicitly as UTF-8, and normalizes comma-delimited priority arguments from `powershell.exe -File`. This avoids the UTF-8-without-BOM mojibake that turned the em dash into `aEUR`-style text and broke parsing around the progress message.


## Salida en Windows

Los launchers `.cmd` cambian primero a la carpeta de la tool. Toda la salida se escribe directamente en:

`./results/`

Ahi quedan `files/`, `rejected/`, `SOURCE_BACKFILL_RESULTS.csv`, `README_RESULT.md` y el `SOURCE_BACKFILL_PAYLOAD_V96_<fecha>.zip`.

## Windows TLS / Schannel

Esta version invoca `curl.exe` con `--ssl-no-revoke` para evitar el error `CRYPT_E_REVOCATION_OFFLINE` de Schannel cuando Windows no puede alcanzar el servidor de revocacion del certificado. El stderr de curl se captura sin abortar PowerShell; si curl falla, la herramienta continua con `Invoke-WebRequest`.

## TLS hostname mismatch fallback

If Schannel returns `SEC_E_WRONG_PRINCIPAL` / `SNI or certificate check failed`, the tool retries only that individual source with `curl.exe --insecure`. This is not enabled globally. Successful bypassed downloads are marked in `SOURCE_BACKFILL_RESULTS.csv` with `tls_validation=BYPASSED_WRONG_PRINCIPAL` and a warning, and still must pass magic-byte and SHA-256 validation before `DOWNLOAD_OK`.
