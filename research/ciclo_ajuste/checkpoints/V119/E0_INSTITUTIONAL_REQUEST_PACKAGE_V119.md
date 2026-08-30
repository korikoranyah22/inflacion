# Paquete institucional E0 con alcance archivístico · V119

Estado general: **BORRADOR_NO_ENVIADO**  
Fecha de verificación de canales: 29/08/2026  
Objeto: recuperar documentos preexistentes que permitan comprobar liquidaciones, órdenes, custodia y respuestas institucionales todavía ausentes.

## Regla de uso

Cada pedido debe presentarse por separado. No conviene agrupar organismos porque cada uno custodia una parte distinta de la cadena y la Ley 27.275 prevé la remisión cuando el requerido no posee la información. Antes de enviar, completar los datos personales del solicitante y conservar la constancia o número de trámite.

Los textos piden documentos en el estado en que obren. No exigen crear análisis nuevos. Cuando un documento contenga información exceptuada, se solicita copia parcial con tachas o disociación.

Las operaciones de 2008–2009 son anteriores a GDE. Por eso los pedidos exigen el identificador original en COMDOC, papel o sistema institucional heredado y, sólo después, la referencia de una eventual digitalización o migración a GDE/GEDO/RUDO. Una respuesta negativa debe describir qué áreas, sistemas, archivos, copias, respaldos y migraciones se revisaron, además de la serie, regla histórica y acto concreto de transferencia o eliminación. El vencimiento de un plazo o la autorización para reproducir documentos no prueban destrucción.

## Borradores incluidos

1. `REQUEST_ECONOMIA_TESORO_SETTLEMENT_V119.md`: expedientes, constancias Caja y conciliaciones del Tesoro para cuatro rondas 2008 y el strip 2009.
2. `REQUEST_BCRA_CRYL_SETTLEMENT_V119.md`: registros CRyL y constancias de pago/liquidación en el BCRA, con alternativa disociada o agregada.
3. `REQUEST_BNA_FIRST_STAGE_BLOTTER_V119.md`: instrucciones, órdenes, blotter, ejecuciones y conciliaciones del mandato 11–22/08/2008.
4. `REQUEST_AGN_2018_REPLY_V119.md`: respuesta individual del 11/09/2018 e identificadores de los informes BODEN citados.
5. `REQUEST_CNV_CUSTODY_RECORDS_V119.md`: pedido AGN/Caja de 2014, actuaciones supervisoras y registros custodiales disponibles.
6. `REQUEST_CAJA_SETTLEMENT_HOLDINGS_V119.md`: consulta institucional voluntaria por la cuenta 0306/40000 y constancias o agregados no personales.

## Identificadores comunes

- Segunda etapa 2008: licitaciones 28/08, 04/09, 11/09 y 02/10; entregas previstas 01/09, 08/09, 15/09 y 06/10; liquidaciones T+3 previstas 02/09, 09/09, 16/09 y 07/10.
- Cuenta fiduciaria de Caja de Valores: depositante 0306 / comitente 40000.
- Especies 2008: BODEN 2012 (ISIN ARARGE034678), BODEN 2013 (ARARGE035709), unidad vinculada al PIB en pesos (ARARGE03E147) y en dólares ley argentina (ARARGE03E154).
- Strip 2009: cupón 15 de BODEN 2012, ISIN ARARGE03G415; licitación 12/06/2009; entrega prevista 17/06; liquidación prevista 18/06.
- Pedido AGN: UUID 2074c3d9-a535-497e-a97d-d74340ff49fb; nid 18814; vid 18821; ingreso 14/08/2018; respuesta 11/09/2018.

## Controles archivísticos añadidos

- `E0_DOCUMENT_SYSTEM_TEMPORAL_MAP_V119.csv`: impide pedir identificadores electrónicos anacrónicos.
- `E0_ARCHIVAL_RETENTION_AUTHORITY_MATRIX_V119.csv`: separa reglas vigentes, alcance y deducciones prohibidas.
- `E0_NEGATIVE_RESPONSE_ADEQUACY_V119.csv`: fija catorce requisitos para evaluar una respuesta de inexistencia.

## Secuencia sugerida

Presentar primero Economía, BCRA, BNA, AGN y CNV. La consulta a Caja es complementaria: Caja de Valores no se presume aquí sujeta al mismo canal de la Ley 27.275, por lo que su texto está formulado como consulta institucional y ofrece una respuesta agregada o derivación al emisor/supervisor.

No marcar ninguna brecha como cerrada por el solo envío. La matriz `E0_REQUEST_CLOSURE_CRITERIA_V119.csv` exige contenido documental o una respuesta formal que supere los controles de `E0_NEGATIVE_RESPONSE_ADEQUACY_V119.csv`.
