# Checkpoint V122 · códigos históricos y modalidad diferida delimitados

V122 preserva seis fuentes primarias oficiales y avanza dos brechas operativas sin confundirlas con liquidación. Las tablas AFIP contemporáneas permiten enlazar por denominación exacta cuatro especies 2008 con los códigos 5426, 5427, 45698 y 45701. Los formularios y manuales posteriores de Caja/BYMA muestran los campos de una transferencia diferida y separan modalidad, canal TSA e identificador de custodia. Ningún pedido fue enviado.

## Resultado

- 6 borradores: Economía/Tesoro, BCRA/CRyL, BNA, AGN, CNV y Caja de Valores;
- 7 rutas oficiales verificadas al 29/08/2026, incluido el trámite nacional;
- 73 objetos documentales enlazados con sus brechas y alternativas testadas/agregadas;
- 8 criterios explícitos de cierre;
- 6 rutas temporales de sistemas documentales, 10 reglas de autoridad archivística y 14 controles de suficiencia negativa;
- 22 relaciones productor-sistema-registro, 50 claves exactas de búsqueda y 7 adjuntos mínimos;
- registro de seguimiento inicializado con todos los estados `DRAFT_NOT_SENT`;
- 88 fuentes primarias E0, 125 filas fiscales y 79 quiebres metodológicos;
- catálogo maestro de 287 entradas, con 282 copias físicas y 282 hashes válidos;
- panel bancario intacto: 30 entidades y cobertura 61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%;
- CLOSED_NETWORK_GATE=NO.

## Hallazgo y límite

El puente `ISIN → código histórico` queda documentado para cuatro instrumentos mediante llamados oficiales por nombre/ISIN y dos tablas AFIP por denominación/código. Sólo 45698 tiene, además, una corroboración oficial posterior que lo llama expresamente código de Caja de Valores. Para 5426, 5427 y 45701 aún se requiere confirmación institucional de la etiqueta operativa Caja/CRyL. El strip ARARGE03G415 permanece `PUBLIC_CODE_NOT_LOCATED`; está prohibido heredarle 5426 del BODEN 2012 principal.

Los formularios F-33914.01/F-33915.01 son de 2017 y se usan únicamente como diccionario retrospectivo. El Comunicado 10290 de 2020 demuestra que TSA y modalidad diferida coexistían como capas distintas; el instructivo NSC de 2023 documenta luego el retiro de los tipos diferida/inmediata. Ninguna fuente posterior identifica por sí sola el formulario, archivo o lote usado en 2008.

## Leer primero

1. `VEREDICTO_V122.md`
2. `E0_SECURITY_IDENTIFIER_CROSSWALK_V122.csv`
3. `E0_DEFERRED_MODALITY_EQUIVALENCE_AUDIT_V122.csv`
4. `E0_CAJA_CRYL_SETTLEMENT_STAGE_MATRIX_V122.csv`
5. `E0_INSTITUTIONAL_REQUEST_PACKAGE_V122.md`
6. `E0_REQUEST_SEARCH_KEY_MATRIX_V122.csv`
7. `E0_INFORMATION_REQUEST_TRACEABILITY_V122.csv`
8. `E0_REQUEST_CLOSURE_CRITERIA_V122.csv`
9. `REQUEST_SUBMISSION_CHECKLIST_V122.md`
10. `HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V122_A_V123.md`

## Límite operativo

Los borradores contienen campos personales vacíos y no autorizan presentación externa. El envío requiere instrucción expresa del usuario y, cuando corresponda, autenticación o captcha.
