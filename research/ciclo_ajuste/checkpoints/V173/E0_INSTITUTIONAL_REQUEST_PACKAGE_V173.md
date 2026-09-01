# Paquete institucional E0 · V173

Estado general: **BORRADOR_NO_ENVIADO**

No se presentó ningún pedido y no existe plazo ni respuesta en curso. Los textos sólo pueden enviarse con autorización expresa y datos reales de la persona solicitante.

## Aporte V173

Los Comunicados 4857, 4861, 4873 y 5152 permiten pedir registros con claves documentales directas: número de comunicación, código `OYM F.89023.00`, cuenta 306/40000, subcuenta 3, matching, modalidad diferida, ventanas de recepción y fechas del informe T+3.

El paquete contiene 195 objetos trazados y 248 claves exactas. Las búsquedas se concentran en comunicación de la cuarta ronda 2008, instrucciones/asientos ejecutados, informes T+3 entregados, operaciones individuales del Discount en Pesos y pagos/bajas conciliados.

## Borradores incluidos

- Economía / Tesoro: `REQUEST_ECONOMIA_TESORO_SETTLEMENT_V173.md`
- BCRA / CRyL: `REQUEST_BCRA_CRYL_SETTLEMENT_V173.md`
- Banco Nación: `REQUEST_BNA_FIRST_STAGE_BLOTTER_V173.md`
- AGN: `REQUEST_AGN_2018_REPLY_V173.md`
- CNV: `REQUEST_CNV_CUSTODY_RECORDS_V173.md`
- Caja de Valores: `REQUEST_CAJA_SETTLEMENT_HOLDINGS_V173.md`

## Adjuntos mínimos

- `E0_CAJA_TARGET_COMMUNICATION_MATRIX_V173.csv`
- `E0_INFORMATION_REQUEST_TRACEABILITY_V173.csv`
- `E0_REQUEST_SEARCH_KEY_MATRIX_V173.csv`
- `E0_REQUEST_ATTACHMENT_MINIMUM_V173.csv`
- `E0_REQUEST_CLOSURE_CRITERIA_V173.csv`
- `E0_CAJA_CRYL_SETTLEMENT_STAGE_MATRIX_V173.csv`
- `E0_DEFERRED_MODALITY_EQUIVALENCE_AUDIT_V173.csv`

## Regla de evaluación

Una respuesta sólo cierra ejecución si identifica un registro con estado ejecutado y puede conciliarse por ronda, oferta, especie, cantidad y fecha. Una copia de la comunicación, una explicación general, un acuse técnico o el silencio no cierran recepción, pago ni baja de deuda.


## Clave V173 · Discount en Pesos

Los pedidos Economía, Caja y BCRA incorporan `ARARGE03E121`, VNO ARS 2.748,50m, efectivo ARS 1.415,50m y baja actualizada ARS 4.723,53619m. El objetivo es cerrar fecha/operación/asiento/riel de pago; la especie agregada ya quedó conciliada. Estado: `DRAFT_NOT_SENT`.


## Clave V173 · GDP Units y cancelación contractual

El paquete agrega el tramo completo referencia 2006, la ventana contractual 2008 y las rutas documentales CRyL/Caja. El tercer cupón referencia 2007 y el procedimiento de excedente de capacidad de pago quedan separados como controles, no como prueba del evento. Estado: `DRAFT_NOT_SENT`.


## Clave V173 · tablas SLU y recuperación histórica

El pedido Economía/Tesoro incorpora las doce tablas exactas de cuenta, movimiento, aplicación automática y Libro Banco; incluye activas, bajas y rehabilitadas, backups/snapshots 2006-2009, versión y migración v7→v9.0, historial de correcciones, C10 de recurso y C55/cheque como controles. Adjuntos específicos: `E0_SLU_BASE_TABLE_DICTIONARY_V173.csv`, `E0_SLU_HISTORICAL_RECOVERY_STRATEGY_V173.csv`, `E0_SLU_AUTOMATIC_EXPENSE_MAPPING_CHAIN_V173.csv` y `E0_SLU_TABLE_REQUEST_FIELD_MATRIX_V173.csv`. Estado: `DRAFT_NOT_SENT`.

## Clave V173 · obligación de resguardo y consulta SICHE

El pedido Economía/Tesoro nombra inventario SICHE, planillas, logs, actas de recuperación, Acta Acuerdo, backup previo, migración, comparación entre bases e informes firmados. Adjuntos: `E0_SLU_BACKUP_RETENTION_DUTY_V173.csv`, `E0_SLU_MIGRATION_DOCUMENT_CHAIN_V173.csv`, `E0_SLU_BACKUP_AND_SICHE_REQUEST_OBJECTS_V173.csv` y `E0_SICHE_SLU_LEGAL_CUSTODY_EXPORT_ROUTE_V173.csv`. Estado: `DRAFT_NOT_SENT`.

## Clave V173 · ruta primaria SAF 355

El pedido Economía/Tesoro se reorienta a `SIGADE → SIDIF-Link → SIDIF Central → SICHE`, con CUT/extracto para probar liquidación. La pista REPO 2019 se mantiene como comparador, con diferencia interna publicada de $0,45 millones. SLU queda condicional. Adjuntos: `E0_SAF355_SIGADE_SIDIF_LINK_SYSTEM_CHAIN_V173.csv`, `E0_SICHE_SIDIF_CENTRAL_TARGET_ROUTE_V173.csv`, `E0_SIDIF_LINK_SICHE_REQUEST_OBJECTS_V173.csv` y `E0_REPO_COMMISSION_ACCOUNT_LEAD_V173.csv`. Estado: `DRAFT_NOT_SENT`.

## Ampliación V173 · prueba cruzada oficial

La AGN documenta una escalera de auditoría que cruza Ficha/Estado/Tabla SIGADE, reporte `mayorizado por SIGADE`, formularios individuales, mayores contables, movimientos TGN y —cuando corresponde— CRyL. Para la fila 83106000, que está en Anexo K fuera de Cuadro 1A, se priorizan los formularios 71597/152677/2876, el mayorizado, la orden y el movimiento bancario. También se piden planillas y documentos externos porque auditorías posteriores prueban que parte de los controles, ajustes y rectificaciones podía quedar fuera de la fila nativa. Estado: `DRAFT_NOT_SENT`.




## Adenda V173 · Mesa SIGEN, metadatos CGN y custodia híbrida

La Memoria SIGEN 2007 declara que la gestión documental era soportada fundamentalmente por un sistema informático de Mesa de Entradas y que la Resolución SGN Nº 41/07 aprobó el procedimiento de digitalización y publicación, mientras se clasificaba el Archivo General. Se solicita la exportación de salida de la Nota Nº 3672/09 GSEyP, el nombre y esquema del sistema, el cuerpo y anexos, y el índice del Archivo Digital/físico. La referencia a la resolución no sustituye su cuerpo ni acredita que la nota haya sido digitalizada.

La Circular CGN Nº 17/2005 exige asunto o referencia y permite consignar un número de tramitación anterior. Búsquese por separado `3672/09`, `0120/09 DAIF`, `respuesta`, `Cuenta/Cierre 2008`, `UEPEX` y `GSEyP`, incluyendo variantes. La Disposición CGN Nº 32/2009 documenta un circuito contemporáneo de original foliado, CD/disquete, nota de elevación, índice, control de recepción y respaldo en archivo oficial. Se pide soporte, contenedor, folios, índice y constancia, pero no se presume que todo ese procedimiento rigiera idénticamente para la Nota SIGEN.

Se corrige la cronología: COMDOC III ya estaba operativo en el Ministerio en 2008 para ciertos circuitos; la Circular CGN 04/2010 no lo crea, sino que fija un alcance específico y conserva actuaciones por Nota. El negativo debe abarcar Mesa CGN, sistema legado, archivo, campos asunto/referencia, COMDOC si correspondió, migraciones y disposición. Correlacionar salida SIGEN, entrada CGN, antecedente 0120/09 e IDs SISIO. Estado DRAFT_NOT_SENT; solicitudes enviadas 0; SAF355 0/5; ejecución 0/10.


## Adenda V173 · código NOT, CIDD, SPD y Archivo Digital

La Resolución SIGEN Nº 41/2007 y sus anexos fueron recuperados completos. Para Notas SIGEN, el Catálogo de Indexación (CIDD) usa el código `NOT` y registra número, fecha, número de expediente u oficio —con una clave alfanumérica y el mismo método del sistema de Mesa de Entradas—, páginas, anexos, referencia/extracto, emisor, palabras clave, área temática, nivel de acceso y número de caja. Secretaría General era responsable de cargar/revisar índices y la digitalización de notas se promovía luego de comunicar el documento.

Se solicita el registro `NOT` de la Nota 3672/09, su IdDocumento o equivalente, el formulario Solicitud Publicación/Digitalización (SPD), nombre de archivo CIDD, expediente, folios, anexos, incidencias, resultados, firmas, fechas, nivel de acceso y publicación. Asimismo, el original físico debe buscarse por fondo, serie y número de caja. La estructura SIGEN 2022 demuestra que Mesa registra ingresos/egresos en GDE y administra el archivo digital de Notas SIGEN: pídase el crosswalk legado→GDE/Archivo Digital sin inventar un ID GDE originario.

El ArchivoWeb público expone únicamente subtipos de informes; no ofrece `NOT`. Un cero allí no cierra la nota. Common Crawl no se reabrió porque el control V173 falló 2/2; cuarenta consultas siguen pendientes y los errores no son ausencia. Estado DRAFT_NOT_SENT; solicitudes 0; SAF355 0/5; ejecución 0/10.
