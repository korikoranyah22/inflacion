# Paquete institucional E0 · V150

Estado general: **BORRADOR_NO_ENVIADO**

No se presentó ningún pedido y no existe plazo ni respuesta en curso. Los textos sólo pueden enviarse con autorización expresa y datos reales de la persona solicitante.

## Aporte V150

Los Comunicados 4857, 4861, 4873 y 5152 permiten pedir registros con claves documentales directas: número de comunicación, código `OYM F.89023.00`, cuenta 306/40000, subcuenta 3, matching, modalidad diferida, ventanas de recepción y fechas del informe T+3.

El paquete contiene 195 objetos trazados y 248 claves exactas. Las búsquedas se concentran en comunicación de la cuarta ronda 2008, instrucciones/asientos ejecutados, informes T+3 entregados, operaciones individuales del Discount en Pesos y pagos/bajas conciliados.

## Borradores incluidos

- Economía / Tesoro: `REQUEST_ECONOMIA_TESORO_SETTLEMENT_V150.md`
- BCRA / CRyL: `REQUEST_BCRA_CRYL_SETTLEMENT_V150.md`
- Banco Nación: `REQUEST_BNA_FIRST_STAGE_BLOTTER_V150.md`
- AGN: `REQUEST_AGN_2018_REPLY_V150.md`
- CNV: `REQUEST_CNV_CUSTODY_RECORDS_V150.md`
- Caja de Valores: `REQUEST_CAJA_SETTLEMENT_HOLDINGS_V150.md`

## Adjuntos mínimos

- `E0_CAJA_TARGET_COMMUNICATION_MATRIX_V150.csv`
- `E0_INFORMATION_REQUEST_TRACEABILITY_V150.csv`
- `E0_REQUEST_SEARCH_KEY_MATRIX_V150.csv`
- `E0_REQUEST_ATTACHMENT_MINIMUM_V150.csv`
- `E0_REQUEST_CLOSURE_CRITERIA_V150.csv`
- `E0_CAJA_CRYL_SETTLEMENT_STAGE_MATRIX_V150.csv`
- `E0_DEFERRED_MODALITY_EQUIVALENCE_AUDIT_V150.csv`

## Regla de evaluación

Una respuesta sólo cierra ejecución si identifica un registro con estado ejecutado y puede conciliarse por ronda, oferta, especie, cantidad y fecha. Una copia de la comunicación, una explicación general, un acuse técnico o el silencio no cierran recepción, pago ni baja de deuda.


## Clave V150 · Discount en Pesos

Los pedidos Economía, Caja y BCRA incorporan `ARARGE03E121`, VNO ARS 2.748,50m, efectivo ARS 1.415,50m y baja actualizada ARS 4.723,53619m. El objetivo es cerrar fecha/operación/asiento/riel de pago; la especie agregada ya quedó conciliada. Estado: `DRAFT_NOT_SENT`.


## Clave V150 · GDP Units y cancelación contractual

El paquete agrega el tramo completo referencia 2006, la ventana contractual 2008 y las rutas documentales CRyL/Caja. El tercer cupón referencia 2007 y el procedimiento de excedente de capacidad de pago quedan separados como controles, no como prueba del evento. Estado: `DRAFT_NOT_SENT`.


## Clave V150 · tablas SLU y recuperación histórica

El pedido Economía/Tesoro incorpora las doce tablas exactas de cuenta, movimiento, aplicación automática y Libro Banco; incluye activas, bajas y rehabilitadas, backups/snapshots 2006-2009, versión y migración v7→v9.0, historial de correcciones, C10 de recurso y C55/cheque como controles. Adjuntos específicos: `E0_SLU_BASE_TABLE_DICTIONARY_V150.csv`, `E0_SLU_HISTORICAL_RECOVERY_STRATEGY_V150.csv`, `E0_SLU_AUTOMATIC_EXPENSE_MAPPING_CHAIN_V150.csv` y `E0_SLU_TABLE_REQUEST_FIELD_MATRIX_V150.csv`. Estado: `DRAFT_NOT_SENT`.

## Clave V150 · obligación de resguardo y consulta SICHE

El pedido Economía/Tesoro nombra inventario SICHE, planillas, logs, actas de recuperación, Acta Acuerdo, backup previo, migración, comparación entre bases e informes firmados. Adjuntos: `E0_SLU_BACKUP_RETENTION_DUTY_V150.csv`, `E0_SLU_MIGRATION_DOCUMENT_CHAIN_V150.csv`, `E0_SLU_BACKUP_AND_SICHE_REQUEST_OBJECTS_V150.csv` y `E0_SICHE_SLU_LEGAL_CUSTODY_EXPORT_ROUTE_V150.csv`. Estado: `DRAFT_NOT_SENT`.

## Clave V150 · ruta primaria SAF 355

El pedido Economía/Tesoro se reorienta a `SIGADE → SIDIF-Link → SIDIF Central → SICHE`, con CUT/extracto para probar liquidación. La pista REPO 2019 se mantiene como comparador, con diferencia interna publicada de $0,45 millones. SLU queda condicional. Adjuntos: `E0_SAF355_SIGADE_SIDIF_LINK_SYSTEM_CHAIN_V150.csv`, `E0_SICHE_SIDIF_CENTRAL_TARGET_ROUTE_V150.csv`, `E0_SIDIF_LINK_SICHE_REQUEST_OBJECTS_V150.csv` y `E0_REPO_COMMISSION_ACCOUNT_LEAD_V150.csv`. Estado: `DRAFT_NOT_SENT`.

## Ampliación V150 · prueba cruzada oficial

La AGN documenta una escalera de auditoría que cruza Ficha/Estado/Tabla SIGADE, reporte `mayorizado por SIGADE`, formularios individuales, mayores contables, movimientos TGN y —cuando corresponde— CRyL. Para la fila 83106000, que está en Anexo K fuera de Cuadro 1A, se priorizan los formularios 71597/152677/2876, el mayorizado, la orden y el movimiento bancario. También se piden planillas y documentos externos porque auditorías posteriores prueban que parte de los controles, ajustes y rectificaciones podía quedar fuera de la fila nativa. Estado: `DRAFT_NOT_SENT`.

