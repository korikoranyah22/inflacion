# Handover V122 → V123

## Estado congelado

- Checkpoint: V122.
- Estado: `E0_FOUR_HISTORICAL_SECURITY_CODES_DEFERRED_MODALITY_FIELDS_PRESERVED_STRIP_CODE_OPEN_NOT_SENT`.
- Catálogo maestro: 287 entradas; 282 copias físicas; 282 hashes válidos.
- E0: 88 fuentes primarias; 125 filas fiscales; 79 quiebres metodológicos.
- Pedidos: 6 borradores; 73 objetos trazados; 50 claves; 7 adjuntos mínimos; 8 criterios de cierre.
- Envíos: 0. Respuestas: 0. Plazos: ninguno iniciado.
- Panel bancario: 30 entidades exactas; cobertura estricta 61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%.
- CLOSED_NETWORK_GATE=NO.

## Hallazgo preservado

1. Cadena oficial por denominación/ISIN:
   - ARARGE034678 · BODEN 2012 → código histórico 5426.
   - ARARGE035709 · BODEN 2013 → 5427.
   - ARARGE03E147 · unidad PIB pesos → 45698.
   - ARARGE03E154 · unidad PIB USD ley argentina → 45701.
2. Las RG AFIP 2418 y 2575 llaman al campo `CÓDIGO`; no etiquetan universalmente esos valores como Código Caja o CRyL. Sólo 45698 tiene corroboración oficial posterior explícita como “Caja de Valores”.
3. ARARGE03G415, strip cupón 15, queda `PUBLIC_CODE_NOT_LOCATED`. Prohibido heredar 5426.
4. F-33914.01/F-33915.01 documentan en 2017 fecha de ejecución, límite de matching, Código Caja, cantidad y lados emisor/receptor. Son esquema retrospectivo, no prueba de edición/uso 2008.
5. CVSA 10290 (2020) muestra TSA y modalidad diferida coexistiendo; BYMA NSC (2023) conserva TSA y retira diferida/inmediata. Canal ≠ modalidad; código de custodia ≠ ISIN.

## Matrices rectoras

- `E0_SECURITY_IDENTIFIER_CROSSWALK_V122.csv`.
- `E0_DEFERRED_MODALITY_EQUIVALENCE_AUDIT_V122.csv`.
- `E0_CAJA_CRYL_SETTLEMENT_STAGE_MATRIX_V122.csv`.
- `E0_REQUEST_SEARCH_KEY_MATRIX_V122.csv`.
- `E0_INFORMATION_REQUEST_TRACEABILITY_V122.csv`.

## Prioridad V123

1. Buscar una tabla primaria contemporánea Caja/CRyL que vincule directamente los cinco ISIN con el tipo de código y su vigencia.
2. Priorizar el código propio de ARARGE03G415 y cualquier tabla de subespecies del strip 2009.
3. Localizar manual, boletín o edición de formularios de Caja vigente en 2008 que traduzca “modalidad diferida” a soporte, matching y estados.
4. Si no aparece públicamente, mantener la brecha abierta y dejar listos los pedidos; no enviar sin autorización expresa y datos del solicitante.
5. No colapsar adjudicación, instrucción, matching, recepción T+2, informe Caja T+3, CGA/CRyL, pago BCRA y baja contable.

## QA

Ejecutar primero `build_institutional_requests_V122.py` y `qa_V122.py`. Mantener como regresiones obligatorias V98 y V100–V106. Las QA posteriores pueden fallar por conteos congelados y deben clasificarse como superseded, no como regresión sustantiva.
