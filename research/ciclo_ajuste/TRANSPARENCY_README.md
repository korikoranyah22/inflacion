> Current research checkpoint: **V98** — 24 exact entities, strict coverage 59.777595746322620480650441147276358824911189326119979767253088259998915899707248%.

# Ciclo de ajuste — research tree transparente (checkpoint V98)

Este ZIP parte del repositorio `inflacion-backup_sources-v70-patched.zip`, **descomprimido**.
No hay que abrir otro ZIP para ver el repositorio ni para inspeccionar los checkpoints V52–V94 usados por la investigación.

## Estructura

- `research/ciclo_ajuste/checkpoints/V52` ... `V98`: archivos propios de cada iteración, reconstruidos desde la cadena de snapshots. Se omitieron los `BASE_V*.zip` redundantes porque su contenido fue descomprimido en estas carpetas.
- `research/ciclo_ajuste/inputs/`: binarios fuente recuperados manualmente y archivos BCRA usados como evidencia/control.
- `research/ciclo_ajuste/meta/`: handover y metadatos del checkpoint anterior.
- `research/ciclo_ajuste/FILE_ORIGINS.csv`: procedencia de cada archivo agregado.
- `research/ciclo_ajuste/MANIFEST_SHA256.json`: SHA-256 y tamaño de **todos** los archivos del repo final.

## Integridad de los contenedores de origen

- SHA-256 del ZIP base del repo extraído: `524ef8ab518eb5d750f4efe189f17de897a622df66e5c896de517a88f064f8eb`
- SHA-256 del bundle V80 usado para reconstruir la historia: `36a0e5a010ffd59b34691e56e8c2df356cd0f7c15be3e1641651e66a6074e32f`

## Nota sobre duplicados

`Infbanc0923.xlsx` e `Infbanc0923(1).xlsx` se conservan ambos para que el paquete refleje literalmente los archivos recuperados. El manifiesto permite comprobar si son byte-a-byte idénticos.

## Qué NO hice

No reescribí archivos de aplicación ni datos existentes del repositorio base. Todo lo añadido vive bajo `research/ciclo_ajuste/`.

## Nota V81

V81 no agrega ninguna entidad al panel strict. Formaliza el control agregado `Bancos públicos → Primas por pases` y corrige el vintage de `InfBanc_Anexo.xlsx`: el binario recuperado es un anexo vivo con última información enero-2026, aunque se haya preservado dentro del lote recuperado durante la búsqueda 2023-09.

Cobertura strict Q4 four-leg congelada: `23.54332498027319%`.

## Nota V82

V82 no agrega entidades al panel strict. Cierra una iteración de retrieval: confirma la familia `.7z` BCRA, incorpora evidencia de cobertura histórica en un archive posterior, activa un rescate manual concreto para `AGN Informe 210/2023 → Anexo`, y confirma documentalmente que Banco Ciudad tuvo estados/informe separados al 30/09/2023.

Cobertura strict Q4 four-leg congelada: `23.54332498027319%`.


## Nota V83

V83 no agrega entidades al panel strict. El rescate AGN 210/2023 recibido fue un duplicado byte-a-byte del CC2 consolidado ya preservado; además, el full pack BNA 2025 demuestra que la sección separada puede remitir aperturas de intereses a notas consolidadas, por lo que el comparator 2024 deja de ser una solución asumida. La prioridad pasa al `.7z` histórico BCRA, con junio-2024 como objetivo manual verificable.

Cobertura strict Q4 four-leg congelada: `23.54332498027319%`.

## Nota V84

V84 preserves the official BCRA Sep/Dec-2023 open-data `.7z` archives and promotes Banco Ciudad on exact individual/regulatory raw account evidence. Strict coverage rises from `23.54332498027319%` to `27.36550851928007%`. BNA remains pending because account 521007 cannot be mapped to the strict Annex-Q counterparty leg without an explicit presentation crosswalk.

## Nota V85

V85 promotes Banco Galicia from explicit compatible issuer 9M/FY presentation and raises strict coverage to `36.334782973188844%`. A tentative mass-promotion route from six-digit BCRA IEF raw was rejected after Santander demonstrated that those account codes do not universally preserve the Annex-Q BCRA/other-FI split. BNA remains pending.


## Nota V86

V86 promotes Banco BBVA Argentina from individual BCRA raw data after an entity-specific crosswalk is validated by the separate 9M issuer notes and the annual issuer Exhibit-Q comparator. It also corrects the retrieval strategy: BCRA Communication A 7809 defines Annex Q as annual, so 9M searches now target interim interest notes/exhibits rather than a nonexistent “Annex Q 9M”. Strict coverage rises to `42.60167543910082117727407474772757123255%`; gate remains NO.


## Nota V87

V87 promotes Banco Patagonia and Citibank N.A., and collapses Banco Supervielle's prior Q4 counterparty bound to an exact entity-specific four-leg point. Strict compatible Q4 coverage reaches `50.249885286045932707879268953208921095746278669071%`, the first majority-of-banking-assets milestone. The closed-network gate remains NO because uncovered entities remain material and bilateral other-FI cancellation is not system-wide.

The Santander and BNA non-promotions are preserved: exact 9M totals/raw data are insufficient where the entity-specific counterparty presentation is still missing.


## Nota V88

V88 promotes Banco Comafi and Banco de la Provincia de Córdoba (Bancor) through entity-specific separated issuer evidence and reconciliation. Banco Hipotecario is deliberately held after a same-period raw/presentation expense conflict. Strict Q4 four-leg asset coverage rises to `53.569372790275027805600599861244883545337437746901%` across 13 exact entities; closed-network gate remains NO.


## Nota V89

V89 promotes Nuevo Banco de Santa Fe, Nuevo Banco de Entre Ríos, Banco de San Juan and Banco de Santa Cruz from entity-specific issuer presentation evidence. Strict Q4 four-leg asset coverage rises to `56.3611969759920493658507094411572610848828346690020136002104%` across 17 exact entities. Banco de Santiago del Estero remains held because no compatible separated 2023 package was recovered. HSBC and BICE have concrete manual-recovery requests. Closed-network gate remains NO.


## Nota V90

V90 promotes BICE through an entity-specific same-year crosswalk: preserved BCRA entity `00300` Sep/Dec raw data are reconciled against the BICE FY-2023 separated issuer presentation. The user-rescued AGN `Anexo 1 SC` is preserved as a 2-page separated-condensed auditor review report, while `Anexo CC` is retained as consolidated control evidence. Strict Q4 four-leg asset coverage rises to `57.1190506613469397520440391467240292194967562593050627561233%` across 18 exact entities; gate remains NO.


## Nota V91

V91 promotes Banco Industrial S.A. using a Banco-Industrial-specific same-year crosswalk. Its FY-2023 separated Annex Q matches the preserved BCRA raw entity `00322` Dec values one-to-one for BCRA pass income, other-FI pass income and other-FI pass expense; those identities are applied only to the same entity's Sep raw data. Banco BMA / ex-Itaú is explicitly held pending recovery of CNV individual filing #3119515. Strict Q4 four-leg asset coverage rises to `57.916056198050759131069467937837256938558582298375456114153206474294932912853130%` across 19 exact entities; gate remains NO. Six-digit BCRA accounts are never mass-mapped across entities.


## Nota V92

V92 promotes Nuevo Banco del Chaco S.A. through an NBCH-specific same-year crosswalk. The official Provincia del Chaco publication of the bank's separated FY-2023 Annex Q reports pass income of 27,742,167k, split BCRA 27,741,649k and other-FI 518k, with no pass-expense line. Those income values reconcile exactly to preserved BCRA raw entity `00311` Dec data; the same entity-specific identities are applied to Sep raw only. Strict Q4 four-leg asset coverage rises to `58.272770048589213793621379529153308519125980618638424532051024938851826101688225%` across 20 exact entities; gate remains NO. The tiny negative Q4 other-FI-income differencing residual is preserved, not clamped.


## V93 — Banco de La Pampa exactification
Banco de La Pampa S.E.M. was promoted via an entity-specific, same-year reconciliation between official FY-2023 Annex Q and preserved BCRA entity raw. The CNV registry independently identifies the Sep-2023 filing as individual. Strict coverage is now `58.788884622384821983684192349754601959464483825263446945330770576636958219960888%` across 21 exact entities. The crosswalk is not generalized to any other entity.


## V94 — Banco Provincia del Neuquén exactification
Banco Provincia del Neuquén S.A. was promoted via a BPN-specific, same-year reconciliation between official FY-2023 Annex Q and preserved BCRA entity raw. Official BPN disclosure states the bank is not part of economic groups. Banco de Santiago del Estero remains held after an exact raw re-audit because no issuer counterparty crosswalk was recovered. Strict coverage is now `59.332775042193223725791893354893860940046911459229139540352334456615876642065374%` across 22 exact entities; gate remains NO.


## V95 — Banco de Formosa exactification
Banco de Formosa S.A. was promoted using an official separated 9M Annex-Q direct crosswalk plus exact FY issuer-total/same-entity residual reconciliation. The residual method is entity-specific and does not generalize raw account `525042`. Banco de Corrientes remains HOLD after its official Argentine FY2023 source was identified but its Annex-Q body could not be recovered. Foreign ambiguous-name results (including Costa Rica) are explicitly excluded from evidentiary promotion. Strict coverage is now `59.609772901981929858917889103158616639421360357031466173875881044135121089829902%` across 23 exact entities; gate remains NO.


## V96 — BST exactification
Banco de Servicios y Transacciones S.A. is promoted from an official FY Annex-Q direct counterparty split plus an exact same-entity Sep bridge controlled by official 9M combined pass totals. Banco CMF and Banco del Chubut remain HOLD because the necessary counterparty opening is absent; totals/raw account labels are not enough. Strict coverage is `59.777595746322620480650441147276358824911189326119979767253088259998915899707248%` across 24 exact entities; gate remains NO.


## Auditoría arqueológica de preservación — post V96
Se auditó el repo como archivo de fuentes, no sólo como cadena de cálculos. Resultado: **integridad OK, preservación incompleta**. `data/fuentes/FUENTES.csv` tiene 136 entradas, 67 con copia local válida y 69 URL-only; 26 de estas últimas son binarios directos sin copia local identificada. Los registros de retrieval V89–V96 agregan 41 URLs únicas, 40 todavía fuera del catálogo maestro; 23 binarios directos de ese bloque no tienen copia local identificada.

Ver `source_audit/SOURCE_BACKUP_AUDIT_V96.md`, `SOURCE_BACKUP_CENSUS_V96.csv` y `SOURCE_BACKUP_GAPS_V96.csv`. No declarar el repo `source-complete` hasta cerrar P0/P1.


## Arqueología de backups — tanda 1
Se compararon criptográficamente 15 ZIP históricos V70–V89 y 5 carriers 7z. Los ZIP contienen 838 ocurrencias de binarios fuente / 415 SHA-256 únicos; **los 415 ya existen byte-a-byte en el repo actual**. Los 7z Sep-2023, Dic-2023 y Jun-2024 también coinciden exactamente con las copias preservadas. La tanda no cerró ninguno de los 49 gaps de preservación; ver `source_audit/ARCHAEOLOGY_BATCH1_REPORT.md`.

## Backfill remoto — paquete listo post-arqueología V96

Tras las tandas arqueológicas V60–V89, los 49 gaps de preservación siguen siendo referencias URL sin binario local identificado. La sesión pudo leer muchos P0 mediante la capa web, pero esa capa no exporta bytes crudos al sandbox y el contenedor no dispone de salida de red utilizable. Por integridad, **ninguna lectura web se marca como backup físico**.

Se incorpora `source_audit/backfill_v96/` con la cola de 49 fuentes, estado de prueba remota, correcciones de metadata y un descargador reproducible para Windows. Cada archivo recuperado debe superar validación de firma binaria y recibir SHA-256 antes de ingresar al repositorio. La corrección documental de Banco de San Juan (fuente 2024/2023 comparativa, columna FY2023) no modifica V89 ni sus cifras.

## Backfill físico V96 — corrida local 2026-08-28

Se ingirieron **47 de 49** fuentes binarias pendientes después de revalidar tamaño, firma binaria y SHA-256. La cola P0/P1 quedó en **0**; persisten únicamente **2 P2**. `data/fuentes/FUENTES.csv` ahora incorpora también los 23 binarios de issuer retrieval V89–V96 recuperados. La operación fue exclusivamente de preservación: V96 sigue en 24 entidades exactas, cobertura strict 59.777595746322620480650441147276358824911189326119979767253088259998915899707248% y gate NO.

Ver `source_audit/backfill_v96/SOURCE_BACKFILL_INGEST_REPORT_V96.md`, `source_audit/SOURCE_BACKUP_CENSUS_V96_AFTER_BACKFILL.csv` y `source_audit/SOURCE_BACKUP_GAPS_V96_AFTER_BACKFILL.csv`.


## Source-completeness update — 2026-08-28 Round 2 / archaeology batch 4

The source-preservation catalog now contains 189 entries, 156 with a verified local binary.
Round 2 ingested 34 validated binaries. Loose pre-backup Downloads were preserved with explicit provenance and without overwriting same-name/different-hash artifacts.
Remaining physical preservation gaps: 33 (26 direct-binary Round 3 candidates; 7 page/snapshot discovery items). P0/P1 remain zero.


## Source-completeness final — 2026-08-28 manual close

Manual recovery closes the remaining binary-required preservation queue. The master catalog remains at 189 entries: 187 have verified local physical copies and 2 are explicit non-binary reference exemptions (CNV Santander discovery landing and Todo Sobre la Mora analytical secondary reference). There are **0 required physical gaps** and P0/P1/P2 are all zero. Santander's user-downloaded official CNV 9M/FY separated statements were byte-identical to the already preserved binaries, so no duplicate copy was added. V96 numeric state is unchanged: 24 exact entities, strict coverage 59.777595746322620480650441147276358824911189326119979767253088259998915899707248%, closed-network gate NO.


## V97 head note — 2026-08-28
V97 adds two Banco Columbia issuer PDFs as binary-required pending sources and two Banco Mariva CNV publicview discovery references. The prior V96 187/187 binary-required completeness remains true for the frozen V96 source universe, but the V97 head is intentionally not called source-complete until the two Columbia originals are physically preserved. Mariva also has two attachment-discovery actions before an issuer/raw crosswalk can be attempted. No V96 numeric state was modified.


## V98 head note — 2026-08-28
V98 makes no strict promotion. It corrects a stale CMF preservation statement by opening the already-preserved official annual and quarterly historical ZIPs, extracting and separately preserving exact FY-2023 and 9M-2023 separated PDFs, and verifying their hashes and exact pass-total reconciliation to BCRA raw. The flow BCRA-vs-other-FI split is still absent, so CMF remains N/D_STRICT; closing-stock counterparty is not substituted for flow. HSBC target CNV individual presentations are pinned to #3121099 (Sep) and #3163537 (FY), attachment bodies pending. Banco de Corrientes' exact FY download endpoint is identified but not physically recovered in the current environment. Columbia remains analytically resolved/source-preservation held; Mariva remains attachment held.


## V100 delta
Hipotecario analytical bridge independently revalidated against live official 2023 issuer PDFs; still no promotion without physical originals+SHA. Banco BMA/ex-Itaú ordinary FY target corrected to CNV #3171909; #3177414 excluded as special merger balance. Strict state remains 24 entities / 59.777595746322620480650441147276358824911189326119979767253088259998915899707248%.


## V161 source-archive synchronization — 2026-08-31

The master source catalogue now has **577 entries, 577 verified local copies, 577 catalogue-matching SHA-256 hashes and 0 physical/hash gaps**. V161 physically preserves the Banco Rioja and Banco de Corrientes FY2023 statements, canonicalizes the Banco La Pampa Unicode path without deleting the prior mojibake-named copy, snapshots Santander's CNV index and Todo Sobre la Mora, and archives six CNV PublicView pages plus all 30 exposed attachments for BMA, HSBC and Mariva at Sep/FY 2023.

All 30 CNV attachments pass format validation, but the CNV-declared base64 `hash` differs from the SHA-256 of the bytes served in 30/30 cases. Both values are retained; no equivalence or tampering claim is made. See `inputs/source_sync/v161/SOURCE_SYNC_REPORT_V161.md` and `inputs/source_sync/v161/SOURCE_SYNC_CNV_ATTACHMENTS_V161.csv`. This was preservation-only: no numeric state changed and all information-request drafts remain `DRAFT_NOT_SENT`.
