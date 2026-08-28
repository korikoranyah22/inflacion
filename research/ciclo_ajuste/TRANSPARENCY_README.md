# Ciclo de ajuste — research tree transparente (checkpoint V80)

Este ZIP parte del repositorio `inflacion-backup_sources-v70-patched.zip`, **descomprimido**.
No hay que abrir otro ZIP para ver el repositorio ni para inspeccionar los checkpoints V52–V80 usados por la investigación.

## Estructura

- `research/ciclo_ajuste/checkpoints/V52` ... `V80`: archivos propios de cada iteración, reconstruidos desde la cadena de snapshots. Se omitieron los `BASE_V*.zip` redundantes porque su contenido fue descomprimido en estas carpetas.
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
