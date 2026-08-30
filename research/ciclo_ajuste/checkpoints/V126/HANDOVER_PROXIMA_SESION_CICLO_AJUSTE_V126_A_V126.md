# Handover V126 → V126

## Estado congelado

- 298 entradas maestras; 293 copias físicas y 293 hashes válidos.
- E0: 99 fuentes primarias, 125 filas fiscales y 89 quiebres metodológicos.
- Pedidos: 6 borradores, 77 objetos, 57 claves, 7 adjuntos y 8 criterios de cierre.
- Comunicaciones Caja: 4; auditoría diferida: 15; etapas: 8.
- Presentaciones: 0; respuestas: 0.
- Panel: 30 entidades; cobertura estricta 61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%.

## Hallazgo preservado

Los Comunicados 4857, 4861 y 4873 documentan instrucciones directas de Caja para tres rondas de 2008. El Comunicado 5152 documenta el mismo circuito para el strip 2009 y confirma CVSA 5326. Los cuatro fijan 306/40000 desde subcuenta 3, matching, modalidad diferida, total sin parciales y un informe T+3 de efectuadas versus pendientes.

Esto prueba el circuito instruido, no ejecución, entrega del informe, pago ni baja de deuda.

## Prioridad V126

1. Recuperar la comunicación equivalente de la licitación del 02/10/2008 o una constancia institucional de búsqueda.
2. Buscar el detalle ONCP por oferta y las instrucciones de recepción ingresadas por Caja.
3. Recuperar asientos/matching y los informes T+3 de 02/09, 09/09, 16/09/2008 y 18/06/2009.
4. Cruzar cada informe con órdenes de pago BCRA, conciliación y baja de deuda.
5. Mantener abierta la revisión SLIQ/SCG efectiva en 2008.
6. No enviar pedidos sin autorización expresa ni completar datos personales por inferencia.

## QA

Ejecutar `build_institutional_requests_V126.py`, luego `qa_V126.py`, regresiones V98 y V100–V106, y `git diff --check`.
