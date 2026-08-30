# Lista de presentación y seguimiento · V119

Estado: **NINGÚN_PEDIDO_ENVIADO**

## Antes de presentar

- completar nombre, DNI/CUIT, domicilio y correo;
- elegir un organismo por trámite y usar su borrador específico;
- adjuntar sólo las tablas identificadoras necesarias, sin datos personales de terceros;
- exportar el texto presentado y los adjuntos a PDF o conservar sus hashes;
- capturar la pantalla o descargar la constancia final;
- registrar fecha, hora, canal, número de trámite/expediente y plazo inicial;
- no anotar `ENVIADO` hasta contar con constancia.

## Durante el trámite

- el plazo general publicado es de 15 días hábiles, con posible prórroga fundada de otros 15;
- registrar toda derivación o pedido de subsanación;
- no interpretar una remisión como respuesta sustantiva;
- no interpretar silencio, respuesta ambigua o entrega parcial como cierre;
- comparar cada archivo recibido con `E0_INFORMATION_REQUEST_TRACEABILITY_V119.csv`.
- comprobar que una búsqueda de actuaciones 2008–2009 no haya sido limitada a GDE;
- evaluar toda inexistencia contra los catorce controles de `E0_NEGATIVE_RESPONSE_ADEQUACY_V119.csv`.

## Al recibir una respuesta

- preservar correo, nota, carátula, adjuntos y metadatos originales;
- calcular hash SHA-256 de cada archivo recibido;
- distinguir `DOCUMENTO_ENTREGADO`, `ENTREGA_PARCIAL`, `DERIVADO`, `INEXISTENCIA_FUNDADA`, `DENEGADO_FUNDADO`, `RESPUESTA_AMBIGUA` y `SIN_RESPUESTA`;
- no convertir `INEXISTENCIA_FUNDADA` en prueba de que la operación no ocurrió: sólo cierra la ruta documental del organismo y alcance descritos;
- no aceptar “plazo vencido” o “documento reproducible” como prueba de destrucción sin acto individualizable;
- distinguir original, copia autenticada, migración, transferencia y eliminación;
- no convertir un listado de participantes en beneficiarios finales;
- aplicar los criterios de `E0_REQUEST_CLOSURE_CRITERIA_V119.csv` antes de cambiar el estado de una brecha.

## Reclamo

Si corresponde reclamar, conservar la respuesta y la constancia del pedido original. La página nacional informa un plazo de 40 días hábiles desde el vencimiento del plazo de respuesta para el reclamo administrativo. Verificar nuevamente el canal vigente antes de presentar cualquier reclamo.
