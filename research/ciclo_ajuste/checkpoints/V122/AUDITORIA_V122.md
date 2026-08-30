# Auditoría V122

## Alcance

V122 incorpora seis fuentes oficiales primarias que documentan códigos históricos, campos de entrega/recepción diferida y el corte temporal entre canal TSA, modalidad e identificadores de custodia. No incorpora una respuesta institucional, un formulario completado ni una confirmación de liquidación.

## Controles del paquete

- 6 instituciones con borrador separado;
- 7 rutas oficiales verificadas al 29/08/2026;
- 73 objetos documentales trazados;
- 8 reglas de cierre;
- 6 rutas temporales de sistemas, 10 autoridades archivísticas y 14 controles de suficiencia negativa;
- 22 relaciones productor-sistema-registro, 50 claves exactas y 7 filas de adjuntos mínimos;
- 9 eslabones de vigencia, 8 filas de auditoría terminológica y 8 registros del mapa CGA;
- 6 pruebas de equivalencia de modalidad, 5 filas de crosswalk y 8 etapas de liquidación;
- 6 registros de seguimiento en `DRAFT_NOT_SENT`;
- ningún formulario, correo o presentación fue enviado.

## Verificación de fuentes nuevas

- RG AFIP 2418, Anexo III: 16 páginas; páginas 5 y 13 inspeccionadas; 5426, 5427, 45698 y 45701 legibles.
- RG AFIP 2575, Anexo III: 51 páginas; páginas 44 y 51 inspeccionadas; los cuatro códigos se repiten.
- F-33914.01 y F-33915.01: 2 páginas cada uno, ambas inspeccionadas; campos de ejecución, matching, Código Caja, cantidad y contrapartes legibles; metadatos 2017.
- Comunicado CVSA 10290: 6 páginas; páginas 2 y 6 inspeccionadas; TSA/diferida y Código CVSA/ISIN legibles.
- Instructivo NSC BYMA: 5 páginas; página 3 inspeccionada; continuidad TSA, código de custodia y retiro de modalidades legibles.
- Las imágenes temporales de revisión no forman parte del checkpoint.

## Invariantes

- 88 fuentes primarias E0;
- 125 filas del ledger fiscal;
- 79 quiebres metodológicos;
- 30 entidades estrictas y cobertura 61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%;
- no se añadió `CASH_SETTLED`, tenedor final ni causalidad neta;
- código por denominación no equivale a asiento objetivo;
- Código AFIP, ISIN, Código Caja/CVSA, código de custodia y código CRyL no se fusionan sin puente;
- formulario posterior en blanco no prueba uso histórico, matching ni ejecución;
- TSA no equivale a modalidad diferida;
- 5426 no se hereda a ARARGE03G415;
- CLOSED_NETWORK_GATE=NO.

## QA y regresiones

- `build_institutional_requests_V122.py`: PASS;
- `qa_V122.py`: PASS;
- regresiones V98 y V100–V106: PASS;
- panel estricto y cifras fiscales sin cambios;
- `git diff --check` y control de higiene de archivos nuevos: PASS.
