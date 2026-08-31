# Paquete institucional E0 · V144

Estado general: **BORRADOR_NO_ENVIADO**

No se presentó ningún pedido y no existe plazo ni respuesta en curso. Los textos sólo pueden enviarse con autorización expresa y datos reales de la persona solicitante.

## Aporte V144

Los Comunicados 4857, 4861, 4873 y 5152 permiten pedir registros con claves documentales directas: número de comunicación, código `OYM F.89023.00`, cuenta 306/40000, subcuenta 3, matching, modalidad diferida, ventanas de recepción y fechas del informe T+3.

El paquete contiene 195 objetos trazados y 248 claves exactas. Las búsquedas se concentran en comunicación de la cuarta ronda 2008, instrucciones/asientos ejecutados, informes T+3 entregados, operaciones individuales del Discount en Pesos y pagos/bajas conciliados.

## Borradores incluidos

- Economía / Tesoro: `REQUEST_ECONOMIA_TESORO_SETTLEMENT_V144.md`
- BCRA / CRyL: `REQUEST_BCRA_CRYL_SETTLEMENT_V144.md`
- Banco Nación: `REQUEST_BNA_FIRST_STAGE_BLOTTER_V144.md`
- AGN: `REQUEST_AGN_2018_REPLY_V144.md`
- CNV: `REQUEST_CNV_CUSTODY_RECORDS_V144.md`
- Caja de Valores: `REQUEST_CAJA_SETTLEMENT_HOLDINGS_V144.md`

## Adjuntos mínimos

- `E0_CAJA_TARGET_COMMUNICATION_MATRIX_V144.csv`
- `E0_INFORMATION_REQUEST_TRACEABILITY_V144.csv`
- `E0_REQUEST_SEARCH_KEY_MATRIX_V144.csv`
- `E0_REQUEST_ATTACHMENT_MINIMUM_V144.csv`
- `E0_REQUEST_CLOSURE_CRITERIA_V144.csv`
- `E0_CAJA_CRYL_SETTLEMENT_STAGE_MATRIX_V144.csv`
- `E0_DEFERRED_MODALITY_EQUIVALENCE_AUDIT_V144.csv`

## Regla de evaluación

Una respuesta sólo cierra ejecución si identifica un registro con estado ejecutado y puede conciliarse por ronda, oferta, especie, cantidad y fecha. Una copia de la comunicación, una explicación general, un acuse técnico o el silencio no cierran recepción, pago ni baja de deuda.


## Clave V144 · Discount en Pesos

Los pedidos Economía, Caja y BCRA incorporan `ARARGE03E121`, VNO ARS 2.748,50m, efectivo ARS 1.415,50m y baja actualizada ARS 4.723,53619m. El objetivo es cerrar fecha/operación/asiento/riel de pago; la especie agregada ya quedó conciliada. Estado: `DRAFT_NOT_SENT`.


## Clave V144 · GDP Units y cancelación contractual

El paquete agrega el tramo completo referencia 2006, la ventana contractual 2008 y las rutas documentales CRyL/Caja. El tercer cupón referencia 2007 y el procedimiento de excedente de capacidad de pago quedan separados como controles, no como prueba del evento. Estado: `DRAFT_NOT_SENT`.


## Clave V144 · tablas SLU y recuperación histórica

El pedido Economía/Tesoro incorpora las doce tablas exactas de cuenta, movimiento, aplicación automática y Libro Banco; incluye activas, bajas y rehabilitadas, backups/snapshots 2006-2009, versión y migración v7→v9.0, historial de correcciones, C10 de recurso y C55/cheque como controles. Adjuntos específicos: `E0_SLU_BASE_TABLE_DICTIONARY_V144.csv`, `E0_SLU_HISTORICAL_RECOVERY_STRATEGY_V144.csv`, `E0_SLU_AUTOMATIC_EXPENSE_MAPPING_CHAIN_V144.csv` y `E0_SLU_TABLE_REQUEST_FIELD_MATRIX_V144.csv`. Estado: `DRAFT_NOT_SENT`.
