# Auditoría V123

## Alcance

V123 incorpora cuatro fuentes primarias: dos estados contables bancarios contemporáneos, un manual operativo de Caja y una resolución de la CNV. Cierran el puente público de los cinco Códigos Caja y documentan práctica de Recepción Diferida en 2009, sin convertir identificación o formulario en liquidación.

## Controles del paquete

- 6 instituciones con borrador separado y todos los estados `DRAFT_NOT_SENT`;
- 73 objetos, 50 claves exactas, 7 adjuntos mínimos y 8 reglas de cierre;
- 22 relaciones productor-sistema-registro;
- 9 eslabones de vigencia, 8 filas de auditoría terminológica, 8 registros CGA, 8 pruebas de equivalencia de modalidad, 5 filas de crosswalk y 8 etapas de liquidación;
- ningún formulario, correo o presentación enviado.

## Verificación visual de fuentes nuevas

- Banco Columbia: 64 páginas; página PDF 26 inspeccionada; `Identificación Caja de Valores` y códigos 5426, 5427, 45698, 45701 y 5326 legibles.
- Banco Patagonia: 81 páginas; página PDF 48 inspeccionada; cupón 15 de BODEN 2012–5326 legible.
- Caja, Sistema de Transferencias Electrónicas: 94 páginas; portada y páginas PDF 9–12 inspeccionadas; inmediata, diferida, matching, formularios y batch nocturno legibles.
- CNV Resolución 16.189: 2 páginas; página PDF 1 inspeccionada; formularios de Recepción Diferida 0102704/0102705 y movimientos remitidos por Caja legibles.
- Las imágenes temporales de revisión se excluyen del checkpoint.

## Invariantes

- 291 entradas de catálogo, 286 copias físicas y 286 hashes válidos;
- 92 fuentes primarias E0, 125 filas fiscales y 81 quiebres metodológicos;
- 30 entidades estrictas y cobertura 61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%;
- no se añadió `CASH_SETTLED`, tenedor final ni causalidad neta;
- 5326 corresponde al cupón separado y 5426 al título principal;
- Código Caja no equivale automáticamente a código CRyL ni a asiento objetivo;
- práctica 2009 y manual sin fecha interna no prueban la edición vigente en 2008;
- TSA no equivale a modalidad diferida;
- `CLOSED_NETWORK_GATE=NO`.

## QA

- `build_institutional_requests_V123.py`: PASS;
- `qa_V123.py`: PASS;
- regresiones compatibles V98 y V100–V106: PASS;
- panel y cifras fiscales: sin cambios;
- higiene de diferencias y archivos temporales: PASS.
