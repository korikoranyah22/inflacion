# Auditoría V125

## Alcance

V125 incorpora cuatro PDFs oficiales del archivo institucional de Caja de Valores y los conecta con el circuito de las recompras objetivo sin convertir instrucciones en ejecución.

## Verificación de fuentes

- Comunicado 4857: 2 páginas; creación 28/08/2008; recepción 29/08–01/09; informe previsto 02/09.
- Comunicado 4861: 2 páginas; creación 04/09/2008; recepción 05/09–08/09; informe previsto 09/09.
- Comunicado 4873: 2 páginas; creación 11/09/2008; recepción 12/09–15/09; informe previsto 16/09.
- Comunicado 5152: 2 páginas; creación 11/06/2009; recepción 12/06–17/06; informe previsto 18/06; especie CVSA 5326.

Las ocho páginas fueron renderizadas e inspeccionadas. Los cuatro binarios finales tienen hash SHA-256 fijo y texto legible. El pie común `OYM F.89023.00` se conserva como clave documental, no como revisión SLIQ.

## Controles

- catálogo: 298 entradas; 293 copias físicas, todas con hash válido;
- E0: 99 fuentes primarias, 125 filas fiscales y 89 quiebres;
- pedidos: 6 borradores, 77 objetos, 57 claves, 7 adjuntos y 8 criterios de cierre;
- comunicaciones objetivo: 4 filas; auditoría diferida: 15; etapas: 8;
- envíos y respuestas: 0;
- panel: 30 entidades y cobertura estricta sin cambios.

## Invariantes

Una comunicación que ordena transferir no acredita una transferencia ejecutada. Una fecha de informe no acredita su entrega. Una búsqueda pública negativa no acredita inexistencia. El código del pie de página no acredita la revisión efectiva del sistema.

## QA

El control V125 fija hashes, metadatos, contenido operativo, conteos, estados no enviados, límites probatorios, manifestaciones e invariantes numéricos.
