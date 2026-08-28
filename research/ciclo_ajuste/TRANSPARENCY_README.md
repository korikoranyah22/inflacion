# Ciclo de ajuste — research tree transparente (checkpoint V86)

Este ZIP parte del repositorio `inflacion-backup_sources-v70-patched.zip`, **descomprimido**.
No hay que abrir otro ZIP para ver el repositorio ni para inspeccionar los checkpoints V52–V81 usados por la investigación.

## Estructura

- `research/ciclo_ajuste/checkpoints/V52` ... `V83`: archivos propios de cada iteración, reconstruidos desde la cadena de snapshots. Se omitieron los `BASE_V*.zip` redundantes porque su contenido fue descomprimido en estas carpetas.
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
