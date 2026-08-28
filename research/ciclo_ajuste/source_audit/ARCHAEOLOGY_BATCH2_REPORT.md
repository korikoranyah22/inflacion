# Arqueología de backups — tanda 2 (V60–V69)

**Fecha:** 2026-08-28  
**Estado de investigación:** V96 sin cambios numéricos  
**Base comparada:** repo V96 auditado + arqueología tanda 1  
**Objetivo:** verificar si los frontiers V60–V69 contienen fuentes binarias que luego se perdieron y cruzarlos contra los 49 gaps de preservación pendientes.

## Tanda examinada

- **10 ZIP históricos**, uno por versión V60, V61, V62, V63, V64, V65, V66, V67, V68 y V69.
- Los diez ZIP pasan `ZipFile.testzip()` sin miembros corruptos.
- Se recorrieron de forma recursiva las cadenas `BASE_V*.zip`, hasta una profundidad máxima observada de **17** contenedores.
- Inventario recursivo total: **2.481 ocurrencias de miembros** (incluye repeticiones heredadas por las cadenas BASE).

## Resultado criptográfico de binarios

Tomando como binarios fuente `PDF/XLS/XLSX/7z`:

- Ocurrencias encontradas: **10**.
- SHA-256 únicos: **1**.
- Ese único payload es `raw_cache/Series_estadisticas.xlsx`, heredado desde V56 y repetido dentro de cada cadena histórica.
- SHA-256: `3d9a98fa443b833ebb34c814863c1259a89d4ab8d59570578ee030c00288b5d0`.
- El hash ya existe exactamente en el repo actual como `research/ciclo_ajuste/checkpoints/V56/raw_cache/Series_estadisticas.xlsx`.
- Binarios fuente nuevos respecto del repo V96 auditado: **0**.

**Conclusión criptográfica:** tampoco en V60–V69 hay un PDF/Excel/7z fuente que se haya caído durante consolidaciones posteriores. El único binario fuente transportado por esta familia ya está preservado byte-a-byte.

## Cruce contra los 49 gaps actuales

- Matches por basename normalizado de un binario faltante contra miembros históricos: **0**.
- Gaps cerrados por esta tanda: **0**.
- Gaps que sí aparecen como **referencia textual histórica**, pero sin el binario correspondiente: **15**.

Los 15 son principalmente fuentes de la capa bancaria V66–V69 (ICBC, Macro, Santander, Supervielle, Banco de Valores, BNA/Ciudad) y dos referencias BCRA. Esto es útil porque demuestra que varias fuentes ya se utilizaban/citaban en esas versiones, pero los frontiers guardaban **URL + extracción/derivado**, no el PDF original.

Ejemplos claros:

- V67 contiene las URLs oficiales de Banco Macro 9M/FY y los números exactos extraídos, pero no contiene los PDFs `banco_macro_sa_eeff_30-09-2023.pdf` ni `eeff_bm_31-12-2023.pdf`.
- V66 contiene referencias de Supervielle y Banco de Valores, pero no sus PDFs fuente.
- V68 contiene las referencias mirror de Santander, pero no los binarios.
- V69 contiene referencias de BNA y Banco Ciudad, pero no los PDFs originales.

Por lo tanto, para este subconjunto la evidencia apunta a **“nunca estuvo físicamente en estos checkpoint ZIP”**, no a “estuvo y se perdió después”.

## Impacto sobre la auditoría global

La cola permanece en **49 gaps: 20 P0, 18 P1 y 11 P2**. Tanda 2 no modifica promociones, paneles, cobertura ni gate de V96.

Combinando tandas 1 y 2 hasta ahora:

- no apareció ningún binario fuente histórico nuevo respecto del repo actual;
- todos los binarios fuente realmente contenidos en los backups examinados están preservados por SHA-256;
- los gaps restantes son, cada vez con mayor evidencia, casos donde se preservó la referencia pero no se incorporó el documento fuente al repo en el momento de uso.

## Evidencia machine-readable

- `ARCHAEOLOGY_BATCH2_CARRIER_FINGERPRINTS.csv` — hash, tamaño e integridad de los 10 carriers.
- `ARCHAEOLOGY_BATCH2_ARCHIVE_INVENTORY.csv` — inventario recursivo de todos los miembros y cadenas BASE.
- `ARCHAEOLOGY_BATCH2_SHA256_BINARY_VALIDATION.csv` — validación SHA-256 de cada ocurrencia binaria.
- `ARCHAEOLOGY_BATCH2_UNIQUE_BINARIES.csv` — deduplicación por hash.
- `ARCHAEOLOGY_BATCH2_GAP_MATCHES.csv` — matches de binarios contra gaps (vacío en esta tanda).
- `ARCHAEOLOGY_BATCH2_GAP_TEXT_CONTEXT.csv` — referencias textuales históricas a gaps actuales.
- `SOURCE_BACKUP_GAPS_V96_AFTER_BATCH2.csv` — cola conservando resultados de tanda 1 y agregando estado de tanda 2.

**Veredicto tanda 2:** integridad histórica V60–V69 = **OK**; binarios perdidos detectados = **0**; gaps recuperados = **0**; referencias históricas sin binario confirmadas = **15**.
