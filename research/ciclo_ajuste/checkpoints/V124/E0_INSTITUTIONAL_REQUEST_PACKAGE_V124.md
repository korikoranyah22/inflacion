# Paquete institucional E0 con claves de sistema · V124

Estado general: **BORRADOR_NO_ENVIADO**  
Fecha de verificación de canales: 29/08/2026  
Objeto: recuperar documentos preexistentes que permitan comprobar liquidaciones, órdenes, custodia y respuestas institucionales todavía ausentes.

## Regla de uso

Cada pedido debe presentarse por separado. No conviene agrupar organismos porque cada uno custodia una parte distinta de la cadena y la Ley 27.275 prevé la remisión cuando el requerido no posee la información. Antes de enviar, completar los datos personales del solicitante y conservar la constancia o número de trámite.

Los textos piden documentos en el estado en que obren. No exigen crear análisis nuevos. Cuando un documento contenga información exceptuada, se solicita copia parcial con tachas o disociación.

Las operaciones de 2008–2009 son anteriores a GDE. Por eso los pedidos exigen el identificador original en COMDOC, papel o sistema institucional heredado y, sólo después, la referencia de una eventual digitalización o migración a GDE/GEDO/RUDO. Una respuesta negativa debe describir qué áreas, sistemas, archivos, copias, respaldos y migraciones se revisaron, además de la serie, regla histórica y acto concreto de transferencia o eliminación. El vencimiento de un plazo o la autorización para reproducir documentos no prueban destrucción.

V124 conserva la regla temporal de V123 y corrige la fecha interna del manual SLIQ: su página legal declara impresión en marzo de 2000. Una página institucional Merval archivada en 2004 publica el sistema y su clave `SCG`; la memoria de Caja del ejercicio 2006 agrega continuidad operativa; y MU-32002.03 muestra un esquema paralelo de control de revisiones 2006–2009. La Resolución CNV 16.189 mantiene probados formularios numerados de Recepción Diferida en agosto de 2009. Estas claves identifican búsquedas: no convierten una fecha de impresión en vigencia efectiva durante 2008, una publicación en instrucción ejecutada, un Código Caja en código CRyL ni un acuse técnico en pago.

## Borradores incluidos

1. `REQUEST_ECONOMIA_TESORO_SETTLEMENT_V124.md`: expedientes, constancias Caja y conciliaciones del Tesoro para cuatro rondas 2008 y el strip 2009.
2. `REQUEST_BCRA_CRYL_SETTLEMENT_V124.md`: registros CRyL y constancias de pago/liquidación en el BCRA, con alternativa disociada o agregada.
3. `REQUEST_BNA_FIRST_STAGE_BLOTTER_V124.md`: instrucciones, órdenes, blotter, ejecuciones y conciliaciones del mandato 11–22/08/2008.
4. `REQUEST_AGN_2018_REPLY_V124.md`: respuesta individual del 11/09/2018 e identificadores de los informes BODEN citados.
5. `REQUEST_CNV_CUSTODY_RECORDS_V124.md`: pedido AGN/Caja de 2014, actuaciones supervisoras y registros custodiales disponibles.
6. `REQUEST_CAJA_SETTLEMENT_HOLDINGS_V124.md`: consulta institucional voluntaria por la cuenta 0306/40000 y constancias o agregados no personales.

## Identificadores comunes

- Segunda etapa 2008: licitaciones 28/08, 04/09, 11/09 y 02/10; entregas previstas 01/09, 08/09, 15/09 y 06/10; liquidaciones T+3 previstas 02/09, 09/09, 16/09 y 07/10.
- Cuenta fiduciaria de Caja de Valores: depositante 0306 / comitente 40000.
- Especies 2008: BODEN 2012 (ISIN ARARGE034678), BODEN 2013 (ARARGE035709), unidad vinculada al PIB en pesos (ARARGE03E147) y en dólares ley argentina (ARARGE03E154).
- Códigos Caja contemporáneos por denominación: 5426, 5427, 45698 y 45701, rotulados por Banco Columbia y sujetos todavía a confirmación de vigencia y equivalencia CRyL.
- Strip 2009: cupón 15 de BODEN 2012, ISIN ARARGE03G415; licitación 12/06/2009; entrega prevista 17/06; liquidación prevista 18/06.
- Código del strip: `5326 · EXACT_CONTEMPORANEOUS_CAJA_CODE_TWO_BANK_DISCLOSURES`; no confundirlo con 5426 del título principal.
- Pedido AGN: UUID 2074c3d9-a535-497e-a97d-d74340ff49fb; nid 18814; vid 18821; ingreso 14/08/2018; respuesta 11/09/2018.

## Controles archivísticos añadidos

- `E0_DOCUMENT_SYSTEM_TEMPORAL_MAP_V124.csv`: impide pedir identificadores electrónicos anacrónicos.
- `E0_ARCHIVAL_RETENTION_AUTHORITY_MATRIX_V124.csv`: separa reglas vigentes, alcance y deducciones prohibidas.
- `E0_NEGATIVE_RESPONSE_ADEQUACY_V124.csv`: fija catorce requisitos para evaluar una respuesta de inexistencia.
- `E0_CRYL_EFFECTIVE_VERSION_CHAIN_V124.csv`: separa texto base, modificaciones, regla exacta 2008 y continuidad 2012.
- `E0_BUYBACK_MODALITY_TERM_AUDIT_V124.csv`: registra qué términos aparecen y cuáles no en los procedimientos de recompra.
- `E0_DEFERRED_MODALITY_EQUIVALENCE_AUDIT_V124.csv`: separa modalidad, canal, formulario, edición, publicación y corte temporal en once pruebas.
- `E0_SECURITY_IDENTIFIER_CROSSWALK_V124.csv`: conserva cinco ISIN y cinco Códigos Caja contemporáneos sin confundirlos con liquidación.
- `E0_CAJA_CRYL_SETTLEMENT_STAGE_MATRIX_V124.csv`: evita colapsar ocho etapas de títulos, mensajería y efectivo.

## Controles operacionales añadidos

- `E0_RECORD_PRODUCER_SYSTEM_MAP_V124.csv`: vincula 22 productores, sistemas y clases de registro con fuente y cautela.
- `E0_CRYL_CGA_RECORD_MAP_V124.csv`: descompone archivo de entrada, respuesta, validaciones y migración.
- `E0_REQUEST_SEARCH_KEY_MATRIX_V124.csv`: reúne 53 claves exactas por organismo.
- `E0_REQUEST_ATTACHMENT_MINIMUM_V124.csv`: limita los adjuntos a siete filas justificadas y excluye material innecesario.

## Secuencia sugerida

Presentar primero Economía, BCRA, BNA, AGN y CNV. La consulta a Caja es complementaria: Caja de Valores no se presume aquí sujeta al mismo canal de la Ley 27.275, por lo que su texto está formulado como consulta institucional y ofrece una respuesta agregada o derivación al emisor/supervisor.

No marcar ninguna brecha como cerrada por el solo envío. Los ocho criterios de `E0_REQUEST_CLOSURE_CRITERIA_V124.csv` exigen contenido documental o una respuesta formal que supere los controles de `E0_NEGATIVE_RESPONSE_ADEQUACY_V124.csv`.


