# Sincronización archivística de fuentes — V161

Fecha de cierre: **2026-08-31**  
Alcance: preservación local de todas las entradas del catálogo maestro `data/fuentes/FUENTES.csv`.  
Resultado QA: **PASS**.

## Resultado ejecutivo

La sincronización elevó el catálogo maestro de **542 a 577 fuentes** y cerró los seis aparentes huecos físicos que mostraba la auditoría V160. El estado verificable actual es:

- **577/577** entradas con archivo local;
- **577/577** archivos con SHA-256 coincidente con el catálogo;
- **0** huecos físicos o de hash dentro del universo catalogado;
- **43** archivos de rescate incorporados o normalizados en esta tanda, por **45.167.494 bytes**;
- archivo nuevo de la tanda: aproximadamente **39,4 MiB** dentro de `source_sync/v161`; el archivo individual más grande mide **7,55 MiB**.

“Completo” significa aquí **completo respecto del catálogo maestro**. No significa que el repositorio sea un WARC de cada recurso transitivo de Internet —por ejemplo, todos los estilos, tipografías o bibliotecas enlazados por una página—. Sí significa que cada fuente usada y catalogada tiene una copia local identificable y verificable.

## Rescates y normalizaciones

1. **Banco Rioja**: se preservó el estado financiero anual 2023 oficial, 86 páginas, y se inspeccionó visualmente el Anexo Q.
2. **Banco de Corrientes**: se preservó el estado financiero anual 2023 oficial, 142 páginas, y se inspeccionó visualmente el Anexo Q.
3. **Banco de La Pampa**: se creó una copia con la ruta Unicode canónica `Diseño...pdf`, byte-idéntica a la copia cuyo nombre había quedado mojibakeado. La copia anterior no fue eliminada.
4. **Santander / CNV**: se archivó la respuesta HTML completa del índice regulatorio 2023.
5. **Todo sobre la mora**: se archivó la respuesta HTML completa del sitio secundario, sin alterar su clasificación probatoria no oficial.
6. **Presentaciones CNV**: se archivaron seis páginas públicas completas —Banco BMA, HSBC y Mariva; septiembre y diciembre de 2023— y sus **30 adjuntos**:
   - seis estados contables;
   - seis memorias o constancias de no correspondencia;
   - seis informes de auditor independiente;
   - seis informes de comisión fiscalizadora o sindicatura;
   - seis reseñas informativas o constancias de no correspondencia.
7. Se preservaron los dos scripts públicos de la CNV que documentan el flujo `GetPublicValetKey` → `DownloadBlob`, suficiente para reproducir la recuperación sin guardar autorizaciones temporales.

## Control de los adjuntos CNV

Los 30 adjuntos tienen firma de formato válida; 29 son PDF y uno es DOCX. Los PDF son estructuralmente legibles y el DOCX contiene `word/document.xml`. Además, se renderizó e inspeccionó la primera página de los seis estados contables principales.

La CNV publica para cada adjunto una cadena de 32 bytes codificada en base64 que su frontend llama `hash`. En **30/30** casos esa cadena no coincide con el SHA-256 de los bytes que el propio servicio público de la CNV entrega. La auditoría conserva:

- la huella declarada por la CNV;
- el GUID del blob;
- el SHA-256 de los bytes efectivamente servidos;
- el nombre y tamaño publicados;
- la URL de la presentación pública;
- la copia local.

Esta diferencia se registra como **anomalía de representación o contrato de huella**, no como prueba de adulteración. No se conoce todavía si la CNV calcula ese campo sobre otra representación, sobre bytes previos a una transformación o con una semántica distinta. Por esa razón ninguna fila afirma equivalencia cuando no fue demostrada.

## Archivos de control

- `SOURCE_SYNC_FILE_MANIFEST_V161.csv`: inventario de los 43 archivos de rescate, con origen, tamaño y SHA-256.
- `SOURCE_SYNC_CNV_ATTACHMENTS_V161.csv`: manifiesto forense de los 30 adjuntos CNV.
- `extract_cnv_attachments.py`: extracción reproducible de metadatos embebidos.
- `download_cnv_attachments.py`: recuperación reproducible mediante el mecanismo público de la CNV.
- `update_source_catalog_v161.py`: promoción idempotente al catálogo y reconstrucción de auditorías.
- `qa_source_sync_v161.py`: validación estricta de catálogo, rutas, hashes, estructura PDF/DOCX y estados de resguardo.
- `research/ciclo_ajuste/source_audit/CURRENT_SOURCE_COMPLETENESS_V161.json`: resumen legible por máquina.
- `research/ciclo_ajuste/source_audit/MASTER_LOCAL_HASH_VALIDATION_V161.csv`: validación fila por fila.
- `research/ciclo_ajuste/source_audit/SOURCE_PRESERVATION_MISSING_V161.csv`: sólo encabezado; no quedan faltantes catalogados.

## Límites de la operación

La tanda fue exclusivamente archivística:

- no cambió ninguna cifra analítica ni promovió entidades;
- no altera los gates estrictos de la investigación;
- las seis solicitudes de información siguen en **DRAFT_NOT_SENT**;
- no se envió ninguna solicitud ni se produjo ningún contacto externo.

La recuperación de Mariva, HSBC y BMA elimina el bloqueo **físico** de sus adjuntos. Su eventual uso para crosswalks o promociones requiere una vuelta analítica separada y explícita.
