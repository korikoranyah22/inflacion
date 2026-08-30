# Handover V124 → V125

## Estado congelado

- Checkpoint: V124.
- Estado: `E0_FIVE_CAJA_CODES_DEFERRED_MANUAL_2000_SYSTEM_2004_PRACTICE_2009_TARGET_2008_REVISION_OPEN_NOT_SENT`.
- Catálogo: 294 entradas; 289 copias físicas; 289 hashes válidos.
- E0: 95 fuentes primarias; 125 filas fiscales; 85 quiebres metodológicos.
- Pedidos: 6 borradores; 74 objetos; 53 claves; 7 adjuntos; 8 criterios de cierre.
- Envíos: 0. Respuestas: 0. Plazos: ninguno.
- Panel: 30 entidades; cobertura estricta 61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%.
- `CLOSED_NETWORK_GATE=NO`.

## Hallazgo preservado

- El manual SLIQ declara `Impreso en Buenos Aires, Marzo de 2000`.
- Una página institucional Merval archivada en 2004 publica el sistema, sus funciones y la clave `SCG`.
- La memoria de Caja del ejercicio 2006 aporta continuidad operativa previa al objetivo.
- MU-32002.03 muestra un esquema paralelo de control de revisiones 00–03 con hitos 2006, 2007 y 2009.
- La CNV mantiene probados formularios de Recepción Diferida en agosto de 2009.

La cadena ubica edición, publicación y continuidad antes de 2008. No prueba cuál revisión SLIQ/SCG estuvo efectivamente vigente en cada fecha objetivo, ni instrucción, matching, recepción, pago o baja de deuda.

Los puentes de especie permanecen: ARARGE034678→5426; ARARGE035709→5427; ARARGE03E147→45698; ARARGE03E154→45701; ARARGE03G415→5326. Código Caja no equivale a código CRyL ni acredita liquidación.

## Prioridad V125

1. Buscar el registro maestro, control de cambios o tabla de vigencia SLIQ/SCG y la revisión efectiva en las fechas de 2008.
2. Buscar instrucciones y asientos Caja de 0306/40000 por fecha, ISIN/código y cantidad.
3. Buscar matching, estados rechazados/ejecutados e informe Caja T+3.
4. Buscar órdenes y pagos BCRA, conciliación Tesoro y baja de deuda.
5. Mantener edición/publicación, Código Caja, código CRyL, instrucción, recepción y pago en capas separadas.
6. No enviar pedidos sin autorización expresa y datos del solicitante.

## QA

Ejecutar `build_institutional_requests_V124.py` y `qa_V124.py`. Mantener como regresiones compatibles V98 y V100–V106; las QA intermedias con conteos congelados son superseded.
