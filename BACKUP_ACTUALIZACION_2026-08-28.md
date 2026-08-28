# Backup / actualización — 2026-08-28

Este snapshot del repo incorpora el árbol transparente de investigación de `research/ciclo_ajuste/` hasta **V96**.

- V90: promoción exacta de **BICE** mediante crosswalk específico de entidad y preservación de los tres PDFs AGN rescatados manualmente.
- V91: promoción exacta de **Banco Industrial S.A.** mediante crosswalk específico de entidad FY-2023 ↔ raw BCRA `00322`.
- V92: promoción exacta de **Nuevo Banco del Chaco S.A.** mediante la publicación oficial de estados separados FY-2023 de la Provincia del Chaco ↔ raw BCRA `00311`.
- Estado strict actual: **59.777595746322620480650441147276358824911189326119979767253088259998915899707248%** de activos cubiertos; **24 entidades exactas**; gate **NO**.
- Próximo blanco autónomo: **Banco Columbia S.A.**
- HSBC y Banco BMA/ex-Itaú siguen como recuperaciones manuales; Banco de Santiago del Estero queda HOLD hasta recuperar un crosswalk específico de emisor.
- Regla metodológica intacta: nunca se generalizan en masa los códigos contables BCRA de seis dígitos.

Consultar `research/ciclo_ajuste/TRANSPARENCY_README.md`, `FILE_ORIGINS.csv` y `MANIFEST_SHA256.json` para trazabilidad e integridad.


## V93
- promoted Banco de La Pampa S.E.M.
- strict exact entities: 21
- strict coverage: 58.788884622384821983684192349754601959464483825263446945330770576636958219960888%
- repo source registry added under `research/ciclo_ajuste/inputs/issuer_retrieval/v93/`
- next autonomous target: Banco de Santiago del Estero S.A.


## V94
- promoted Banco Provincia del Neuquén S.A.
- Banco de Santiago del Estero re-audited and deliberately held pending issuer counterparty crosswalk
- strict exact entities: 22
- strict coverage: 59.332775042193223725791893354893860940046911459229139540352334456615876642065374%
- repo source registry added under `research/ciclo_ajuste/inputs/issuer_retrieval/v94/`
- next autonomous target: Banco de Corrientes S.A.


## V95
- promoted Banco de Formosa S.A. via separated 9M direct crosswalk + exact FY issuer-total residual reconciliation
- Banco de Corrientes official Argentine source identified but left HOLD pending Annex-Q body
- exact entities: 23
- strict coverage: 59.609772901981929858917889103158616639421360357031466173875881044135121089829902%
- search hygiene tightened: Argentina/correct issuer only; Costa Rica/foreign ambiguous matches excluded
- next autonomous target: Banco CMF S.A.


## V96
- promoted Banco de Servicios y Transacciones S.A. via official FY Annex-Q direct split + exact 9M same-entity bridge
- Banco CMF and Banco del Chubut deliberately held pending counterparty opening
- exact entities: 24
- strict coverage: 59.777595746322620480650441147276358824911189326119979767253088259998915899707248%
- next autonomous target: Banco Columbia S.A.


## Auditoría arqueológica de fuentes (post-V96)
- verificación de integridad: ZIP original OK; manifiesto global y hashes locales OK;
- **no se declara source-complete**: el catálogo maestro conserva 69 entradas URL-only y hay binarios primarios posteriores a V70 citados pero todavía no preservados;
- cola de recuperación priorizada agregada en `research/ciclo_ajuste/source_audit/SOURCE_BACKUP_GAPS_V96.csv`;
- se pausa la expansión V97 hasta sanear primero los P0/P1 de preservación.

## Preparación de backfill físico de fuentes — post arqueología
- las tandas V60–V89 no recuperaron binarios actualmente faltantes: confirmaron que los binarios antiguos sí sobrevivieron a las consolidaciones;
- la cola activa conserva 49 gaps URL-only pendientes de backup físico;
- se agrega `research/ciclo_ajuste/source_audit/backfill_v96/` con downloader reproducible, request CSV, estado de intentos y correcciones de metadata;
- una fuente sólo pasa a preservada al existir físicamente, validar su firma y tener SHA-256;
- Banco de San Juan: la fuente oficial de marzo de 2025 se etiqueta correctamente como comparativa 2024/2023 con FY2023 como columna comparadora; impacto numérico: ninguno;
- estado strict permanece congelado en V96 (24 entidades, 59.777595746322620480650441147276358824911189326119979767253088259998915899707248%, gate NO).

## Backfill físico V96 completado parcialmente
- payload local procesado: **47/49 DOWNLOAD_OK** revalidados e ingeridos;
- P0 pendientes: **0**; P1 pendientes: **0**; P2 pendientes: **2**;
- 23 fuentes issuer V89–V96 incorporadas a `FUENTES.csv`;
- 24 fuentes existentes URL-only del catálogo maestro convertidas a copia física con SHA-256;
- V96 numérico permanece congelado (24 entidades exactas, 59.777595746322620480650441147276358824911189326119979767253088259998915899707248%, gate NO);
- V97 puede reanudarse sin bloqueo P0/P1, aunque el repo todavía no se declara `source-complete` por los dos P2 restantes.

## Arqueología histórica V32/V48/V50/V52–V59
- V52–V59: contenido de checkpoint revalidado byte-a-byte, sin pérdidas;
- nuevos binarios aportados por esos carriers: **0**;
- cinco assets BCRA físicos preexistentes fueron reconciliados/incorporados al catálogo maestro y `202312e.pdf` quedó vinculado a su fila existente;
- nueva cola `SOURCE_BACKFILL_REQUEST_V96_ROUND2.csv`: **35** binarios directos P2;
- lista completa `SOURCE_PRESERVATION_MISSING_V96_COMPLETE.csv`: **68** items aún no preservados (35 accionables + 33 de snapshot/descubrimiento);
- V96 numérico sin cambios.


## Backfill Round 2 + arqueología de Downloads sueltos
- Round 2: **34/35** descargas válidas, todas revalidadas e ingeridas; `bcra_boldat202505_tipo_titular` sigue fallando por DNS del host legado `www7.bcra.gob.ar`;
- `bolmetes.pdf` sí fue recuperado usando la URL oficial alternativa;
- `csvs(1).zip`: 66 artefactos CSV históricos preservados como recuperación suelta, sin reconstruir ficticiamente checkpoints;
- `xlsxs(1).zip`: 11 XLSX auditados; duplicados exactos no duplicados, 4 hojas no clasificadas preservadas y `Infbanc0624.xlsx` agregado como fuente recuperada;
- `agn_bna_informe210_9m2023` reconciliado con los tres adjuntos oficiales ya preservados desde V72/manual recovery;
- catálogo maestro: **189** entradas, **156** con copia local y **156/156** SHA-256 verificados;
- faltantes físicos actuales: **33** = **26** directos listos para Round 3 + **7** página/snapshot/manual;
- P0/P1 permanecen en **0/0**; V96 numérico no cambia.

## Empaquetado GitHub-safe de fuentes grandes
- 4 fuentes físicas >50 MiB fueron reemplazadas por ZIP individuales trackeables, todos <=50 MiB;
- los originales están preservados byte-a-byte dentro de cada ZIP y sus SHA-256 originales quedan registrados;
- `RESTORE_LARGE_SOURCES.ps1` permite reconstruir los cuatro originales y verificar sus hashes;
- los originales restaurados quedan en `.gitignore` para evitar commits accidentales, pero la copia canónica ZIP sí permanece dentro del repo;
- V96 numérico y datos derivados: sin cambios.

## Source backfill Round 3
- payload `SOURCE_BACKFILL_PAYLOAD_V96_20260828_170012.zip`: 26 requested, 25 DOWNLOAD_OK, 1 failed;
- 25 PDFs revalidated by size, `%PDF-` magic and SHA-256 and ingested under `data/fuentes/ciclo_ajuste/backfill_v96_round3/`;
- master catalog remains 189 entries; physical local copies increase 156 -> 181;
- remaining physical gaps: 8 (1 failed legacy BCRA endpoint + 7 page/reference sources requiring exact snapshot/manual recovery);
- P0=0, P1=0; numeric V96 unchanged; GitHub-safe invariant remains 0 files >50 MiB.


## Cierre manual de source-completeness V96

- Catálogo maestro: 189 entradas.
- Copias físicas verificadas: 187/187.
- Referencias no binarias exentas: 2 (`santander_cnv_filings_2023`, `todosobrelamora_cruce`).
- Gaps físicos requeridos: 0 (P0=0, P1=0, P2=0).
- Santander 9M/FY oficial CNV: byte-idénticos a binarios ya preservados; no se duplican.
- `boldat202505`, snapshot BCRA pases, XLS BCRA préstamos/activos, snapshot Capital Humano y bundles INDEC fueron preservados manualmente.
- El XLS adjunto rotulado AUH es byte-idéntico al XLS BCRA y se trata como alias duplicado, no como evidencia de Capital Humano.
- Estado analítico V96: sin cambios.
