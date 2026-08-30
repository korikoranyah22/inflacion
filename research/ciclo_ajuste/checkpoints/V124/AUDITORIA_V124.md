# Auditoría V124

## Alcance

V124 corrige la fecha interna del manual SLIQ y preserva tres fuentes primarias nuevas: página institucional Merval de 2004, memoria de Caja del ejercicio 2006 y manual MU-32002.03 con control de revisiones. La mejora fecha y encadena el sistema antes de 2008 sin convertir continuidad contextual en vigencia o liquidación objetivo.

## Controles del paquete

- 6 instituciones con borrador separado y todos los estados `DRAFT_NOT_SENT`;
- 74 objetos, 53 claves exactas, 7 adjuntos mínimos y 8 reglas de cierre;
- 22 relaciones productor-sistema-registro;
- 9 eslabones CRyL, 8 filas terminológicas, 8 registros CGA, 11 pruebas de modalidad, 5 filas de crosswalk y 8 etapas de liquidación;
- ningún formulario, correo o presentación enviado.

## Verificación de fuentes

- Manual SLIQ: 94 páginas; página PDF 2 revalidada visualmente; `Impreso en Buenos Aires, Marzo de 2000` legible. Se mantienen las páginas 9–12 inspeccionadas en V123 para modalidad, matching y batch.
- Merval 2004: HTML institucional archivado preservado; sección `Sistemas de Custodia y Garantía`, descripción funcional y clave `SCG` verificadas.
- Caja MU-32002.03: 24 páginas; páginas PDF 3 y 22 inspeccionadas; vigencia desde mayo de 2009 y control de cambios 00–03 legibles.
- Caja Memoria 2006: 76 páginas; páginas PDF 20 y 44–45 inspeccionadas; continuidad de sistemas e ingresos por transferencias legibles.
- Las imágenes temporales de revisión se excluyen del checkpoint.

## Invariantes

- 294 entradas de catálogo, 289 copias físicas y 289 hashes válidos;
- 95 fuentes primarias E0, 125 filas fiscales y 85 quiebres metodológicos;
- 30 entidades estrictas y cobertura 61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%;
- no se añadió `CASH_SETTLED`, tenedor final ni causalidad neta;
- fecha de impresión 2000 no equivale a revisión efectiva 2008;
- página pública 2004 y actividad 2006 no equivalen a instrucción objetivo;
- el control de revisiones MU-32002 no rige automáticamente SLIQ;
- Código Caja no equivale automáticamente a código CRyL ni a asiento objetivo;
- `CLOSED_NETWORK_GATE=NO`.

## QA

- `build_institutional_requests_V124.py`: PASS;
- `qa_V124.py`: PASS;
- regresiones compatibles V98 y V100–V106: PASS;
- panel y cifras fiscales: sin cambios;
- higiene de diferencias y archivos temporales: PASS.
