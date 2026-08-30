# Auditoría V121

## Alcance

V121 incorpora cuatro fuentes oficiales primarias que reconstruyen modificaciones CRyL, la regla CGA/X-400 vigente desde enero de 2008 y la continuidad de códigos en 2012. No incorpora una respuesta institucional ni una confirmación de liquidación.

## Controles del paquete

- 6 instituciones con borrador separado;
- 7 rutas oficiales verificadas al 29/08/2026;
- 67 objetos documentales trazados;
- 6 reglas de cierre;
- 6 rutas temporales de sistemas, 10 autoridades archivísticas y 14 controles de suficiencia negativa;
- 22 relaciones productor-sistema-registro, 43 claves exactas y 7 filas de adjuntos mínimos;
- 9 eslabones de vigencia, 8 filas de auditoría terminológica y 8 registros del mapa CGA;
- 6 registros de seguimiento en `DRAFT_NOT_SENT`;
- todos los borradores piden documentos preexistentes y una alternativa de tacha, disociación o agregado;
- todos piden sistemas históricos, migraciones, reproducciones, respaldos y disposición concreta ante inexistencia;
- ningún formulario, correo o presentación fue enviado.

## Verificación de fuentes nuevas

- Comunicación A 3253: 5 páginas renderizadas e inspeccionadas; modificación de cuentas y tabla de origen legibles.
- Comunicación A 3621: 1 página renderizada e inspeccionada; cambio de denominación y alcance legible.
- Comunicación B 9173: 8 páginas renderizadas e inspeccionadas; CGA, X-400/MCT, archivos de entrada/respuesta, dos etapas y rechazos legibles.
- Comunicación B 10469: 2 páginas renderizadas e inspeccionadas; tabla CG1-CG7/CGA e IDEAR legible.
- Auditoría del HTML visible 2008/2009 replicada por QA; scripts y estilos excluidos para evitar falsos positivos.
- Las imágenes temporales de revisión no forman parte del checkpoint.

## Invariantes

- 82 fuentes primarias E0;
- 125 filas del ledger fiscal;
- 73 quiebres metodológicos;
- 30 entidades estrictas y cobertura 61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%;
- no se añadió `CASH_SETTLED`, tenedor final ni causalidad neta;
- no producción no equivale a cero;
- diseño de archivo no equivale a registro objetivo;
- procedimiento BOCON vecino no prueba uso en recompra;
- validación CGA satisfactoria no equivale a segunda etapa, liquidación ni pago;
- continuidad de código en 2012 no prueba preservación de lotes 2008-2009;
- CLOSED_NETWORK_GATE=NO.

## QA y regresiones

- `qa_V121.py`: PASS;
- regresiones V98 y V100-V106: PASS;
- `qa_V120.py`: fallo esperado por aserción congelada del catálogo anterior (277 frente a 281), clasificado `EXPECTED_SUPERSEDED_ASSERTION`;
- `git diff --check`: sin errores;
- panel estricto y cifras fiscales sin cambios.


