# Handover V123 → V124

## Estado congelado

- Checkpoint: V123.
- Estado: `E0_FIVE_CONTEMPORANEOUS_CAJA_CODES_DEFERRED_2009_PRACTICE_PRESERVED_EXACT_2008_EDITION_OPEN_NOT_SENT`.
- Catálogo: 291 entradas; 286 copias físicas; 286 hashes válidos.
- E0: 92 fuentes primarias; 125 filas fiscales; 81 quiebres metodológicos.
- Pedidos: 6 borradores; 73 objetos; 50 claves; 7 adjuntos; 8 criterios de cierre.
- Envíos: 0. Respuestas: 0. Plazos: ninguno.
- Panel: 30 entidades; cobertura estricta 61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%.
- `CLOSED_NETWORK_GATE=NO`.

## Hallazgo preservado

- ARARGE034678 → 5426.
- ARARGE035709 → 5427.
- ARARGE03E147 → 45698.
- ARARGE03E154 → 45701.
- ARARGE03G415 → 5326.

Banco Columbia rotula los valores como `Identificación Caja de Valores`; Banco Patagonia corrobora independientemente 5326 para el cupón 15. Los códigos identifican especies y no acreditan liquidación.

La Resolución CNV 16.189 prueba formularios numerados de `Recepción Diferida` en agosto de 2009. El manual de Caja define inmediata/diferida, matching y procesamiento nocturno, pero no tiene fecha interna y fue reexportado en 2018. La edición exacta vigente en 2008 permanece abierta.

## Prioridad V124

1. Buscar la versión o tabla de vigencia exacta de formularios/manuales de Caja en 2008.
2. Buscar asientos Caja de las cuentas 0306/40000 por fecha, ISIN/código y cantidad.
3. Buscar matching, estados rechazados/ejecutados e informe Caja T+3.
4. Buscar órdenes y pagos BCRA, conciliación Tesoro y baja de deuda.
5. Mantener Código Caja, código CRyL, instrucción, recepción y pago en capas separadas.
6. No enviar pedidos sin autorización expresa y datos del solicitante.

## QA

Ejecutar `build_institutional_requests_V123.py` y `qa_V123.py`. Mantener como regresiones compatibles V98 y V100–V106; las QA intermedias con conteos congelados son superseded.
