# Auditoría arqueológica de fuentes y backups — V96

**Fecha:** 2026-08-28  
**Repositorio auditado:** `inflacion-backup_TRANSPARENT_RESEARCH_V96.zip`  
**Resultado:** **NO está todavía source-complete.** La integridad de lo que sí está guardado es buena, pero hay fuentes primarias/referenciadas que siguen sólo como URL.

## 1. Integridad del paquete actual

- El ZIP V96 pasa `unzip -t` sin errores.
- El manifiesto global contiene 4.331 archivos (excluyéndose a sí mismo) y todos los SHA-256 verificados coinciden.
- En `data/fuentes/FUENTES.csv` hay **136** entradas.
- **67** declaran un `archivo_local`; las **67** existen.
- Las **67** entradas locales con hash declarado coinciden byte-a-byte con su SHA-256.

**Conclusión:** no encontré corrupción ni archivos declarados-locales desaparecidos. El problema no es integridad: es **cobertura de preservación**.

## 2. Catálogo canónico `data/fuentes/FUENTES.csv`

- Entradas totales: **136**.
- Con copia local explícita: **67**.
- Sólo URL/referencia: **69**.
- Dentro de esas referencias-only hay **27** URLs que apuntan directamente a un binario (PDF/XLSX/etc.).
- **1** de esos binarios aparece en otra parte del repo por nombre equivalente.
- Quedan **26** binarios directos del catálogo sin una copia local identificable: **25 PDF + 1 XLSX**.

Esto significa que el viejo informe V195 era correcto en su sentido original —“ningún archivo *declarado local* falta”—, pero **no significaba “todas las fuentes están backupeadas”**. El propio catálogo conserva muchas como `referenced_only`.

## 3. Rama `research/ciclo_ajuste`

El problema es más importante acá porque varias promociones exactas posteriores a V70 se apoyan en PDFs de emisor que quedaron citados, pero no preservados como binario.

### Source docs V53–V96

En los archivos canónicos `FUENTES_V*.md` / `SOURCE_REFERENCES_V*.md` encontré **90** URLs directas a binarios únicas. Por comparación de nombre normalizado:

- copia local identificada: **12**;
- sin copia local identificada: **78**.

Esta cifra es un **screening heurístico**: si un PDF fue renombrado al guardarlo puede producir un falso positivo. Por eso el CSV conserva la URL, versiones y archivos que la citan para reconciliar uno por uno.

### Registros de retrieval V89–V96

Este bloque sí es más concluyente porque los propios registros guardan estados como `binary preserved`, `used_primary` o `...BINARY_NOT_CONTAINER_RETRIEVED`.

- URLs únicas registradas V89–V96: **41**.
- URLs que todavía **no están incorporadas al catálogo maestro `FUENTES.csv`**: **40**.
- URLs directas a binarios: **27**.
- Binarios con copia local identificada: **4**.
- Binarios sin copia local identificada: **23**.

Entre los huecos de prioridad alta están los paquetes que sustentan NBSF, NBER, San Juan, Santa Cruz, BICE FY, Banco Industrial, NBCH, Banco de La Pampa, BPN, Banco de Formosa y BST; además del informe anual CMF usado para el HOLD.

## 4. Qué sí está físicamente preservado

`data/fuentes/` contiene **470 archivos** (~485.6 MiB), incluidos **17 PDF, 11 XLSX, 383 XLS** y el ZIP de Estadísticas Tributarias de ARCA.

`research/ciclo_ajuste/inputs/` contiene **29 archivos** (~91.5 MiB), incluidos **15 PDF, 3 XLSX y 3 archivos 7z** BCRA.

Los rescates manuales BAPRO, Credicoop, BNA/AGN y BICE/AGN sí están dentro del repo.

## 5. Metadatos que quedaron viejos

- `data/fuentes/README.md` y el catálogo maestro siguen documentando un corte **V70 / 27-08-2026**.
- `FUENTES_VALIDACION_2026-08-27.csv` sólo valida ese catálogo histórico.
- `FILE_ORIGINS.csv` tenía sus cabeceras operativas marcadas “updated through V92” aun cuando el árbol ya llega a V96.
- Los `SOURCE_URLS_V89...V96.csv` funcionan como catálogo paralelo y todavía no fueron absorbidos por `data/fuentes/FUENTES.csv`.

## 6. Regla para declarar el repo “source-complete”

No volver a decir “todas las fuentes están backupeadas” hasta que:

1. cada fuente primaria que sea descargable tenga un binario/snapshot local;
2. cada archivo tenga URL de origen, fecha de recuperación, tamaño y SHA-256;
3. las fuentes V71–V96 estén incorporadas al catálogo maestro;
4. las URLs que sean sólo landing pages tengan al menos un snapshot HTML/textual o queden explícitamente justificadas como `URL_ONLY_NON_BINARY`;
5. `SOURCE_BACKUP_GAPS_V96.csv` quede en cero para P0 y P1.

## 7. Archivos de esta auditoría

- `SOURCE_BACKUP_CENSUS_V96.csv`: censo completo cruzando catálogo, source docs y registry V89–V96.
- `SOURCE_BACKUP_GAPS_V96.csv`: cola deduplicada de recuperación, priorizada.
- `MASTER_LOCAL_HASH_VALIDATION_V96.csv`: validación byte-a-byte de las copias declaradas locales.
- `SOURCE_BACKUP_SUMMARY_V96.json`: métricas machine-readable.

**Veredicto:** el repo está **íntegro pero incompleto como archivo de fuentes**. Antes de V97 conviene hacer un pass de recuperación/preservación de binarios, empezando por P0 (fuentes usadas en promociones exactas) y recién después seguir expandiendo entidades.

## Backfill físico ejecutado — 2026-08-28

La corrida local recuperó **47/49** binarios y la ingestión los revalidó por magic bytes, tamaño y SHA-256 antes de incorporarlos. P0=0, P1=0, P2=2. Se agregaron 23 fuentes V89–V96 al catálogo maestro y 24 filas URL-only existentes recibieron copia local + hash. Ver `backfill_v96/SOURCE_BACKFILL_INGEST_REPORT_V96.md`. El estado numérico V96 no cambió.

## Arqueología batch 3 — V32/V48/V50/V52–V59

Los bundles V52–V59 fueron revalidados contra los checkpoints actuales y sus miembros top-level resultaron byte-idénticos. No apareció ningún binario fuente nuevo por SHA-256. V32/V48/V50 y los `FUENTES_V57–V59` sí permitieron reconstruir una segunda capa de URLs binarias históricas y endpoints explícitos de los RAW manifests: **35** son accionables por downloader y el registro completo mantiene **68** items aún no preservados físicamente, de los cuales **33** requieren snapshot/descubrimiento manual. Ver `archaeology_batch3_v32_v59/ARCHAEOLOGY_BATCH3_REPORT.md`.


## Update 2026-08-28 — Round 2 + loose Downloads archaeology

- Round 2 payload: 34/35 valid binaries ingested after size, magic and SHA-256 validation.
- Only Round 2 failure: `bcra_boldat202505_tipo_titular` (legacy `www7.bcra.gob.ar` DNS failure).
- Loose Downloads carriers inventoried: 66 CSV + 11 XLSX.
- `Infbanc0624.xlsx` added as a recovered source; exact duplicates were not duplicated.
- `agn_bna_informe210_9m2023` reconciled against already-preserved V72/manual-recovery attachments.
- Master catalog: 189 entries; 156 local binaries; 156/156 paths and SHA-256 validated.
- Remaining physical gaps: 33 = 26 Round-3 direct binaries + 7 page/snapshot discoveries.
- P0/P1 = 0/0. Numeric V96 remains unchanged.


## Cierre final manual — 2026-08-28

Los gaps físicos requeridos quedan en 0. El catálogo maestro mantiene 189 entradas: 187 poseen copia local SHA-256 verificada y 2 son referencias web explícitamente exentas de binario propio (`santander_cnv_filings_2023` como índice de descubrimiento y `todosobrelamora_cruce` como objeto secundario de análisis). P0/P1/P2 = 0. Este cierre no cambia ninguna cifra analítica de V96.
