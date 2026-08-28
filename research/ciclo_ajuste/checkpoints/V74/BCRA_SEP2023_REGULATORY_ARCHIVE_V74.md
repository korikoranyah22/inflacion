# BCRA September-2023 regulatory archive — V74

## Hallazgo

Se recuperó y auditó la publicación primaria del BCRA **Información de Entidades Financieras — Septiembre 2023**, correspondiente al **30/09/2023**.

Fuente primaria:
https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/Entidades/202309e.pdf

La publicación presenta una ficha por entidad y una sección **“Evolución de estados contables (en millones)”** con columnas hasta `Set-2023`. Para los cuatro targets prioritarios se extrajeron controles de activos, ingresos/egresos financieros e ingresos/egresos por intereses.

Ver `BCRA_202309_ENTITY_LEVEL_REGULATORY_CONTROL_V74.csv`.

## Qué resuelve

- Confirma una fuente primaria regulatoria entity-level al corte 30/09/2023 para Credicoop, Ciudad, BNA y BAPRO.
- Proporciona totales 9M útiles para control cruzado de filing, período, escala y entidad.
- Refuerza que la búsqueda no depende de que exista un Anexo Q trimestral.

## Qué NO resuelve

La publicación mensual visible no abre los resultados de pases en las cuatro patas requeridas (`income_bcra`, `expense_bcra`, `income_otherfi`, `expense_otherfi`). Por ello **ninguno de estos cuatro controles es elegible para construir Q4 estricto**.

## Ruta machine-readable

La página oficial del BCRA indica además que pone a disposición los datos del total de entidades en un archivo `.7z`, con archivos `.txt` y un PDF diccionario:
https://www.bcra.gob.ar/informacion-sobre-entidades-financieras/

En V74 no se logró resolver de forma verificable el endpoint histórico exacto del paquete correspondiente a septiembre de 2023. Este gate queda abierto sin adivinar filenames.

## Archivo binario

Se intentó archivar localmente `202309e.pdf`, pero el runtime no pudo descargar el binario pese a que el documento es legible vía recuperación web. No se sustituye ni se fabrica una copia. La URL primaria queda preservada arriba.
