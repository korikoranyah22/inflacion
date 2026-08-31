# Lista de presentación y seguimiento · V141

Estado: **NINGÚN_PEDIDO_ENVIADO**

## Antes de presentar

- obtener autorización expresa para cada organismo;
- completar sólo datos reales de la persona solicitante;
- seleccionar las filas `REQ133_*` correspondientes;
- adjuntar la matriz de comunicaciones 4857, 4861, 4873 y 5152;
- pedir formatos originales y, como alternativa, copias testadas o certificaciones agregadas;
- conservar separados instrucción, matching, asiento, informe T+3, pago y baja de deuda.

## Claves nuevas

- Comunicados 4857, 4861, 4873 y 5152;
- código documental `OYM F.89023.00`;
- Cuenta Depositante 306 / Subcuenta Comitente 40000;
- Subcuenta Comitente emisora 3;
- fechas de informe 02/09/2008, 09/09/2008, 16/09/2008 y 18/06/2009;
- contenido: transferencias efectuadas y pendientes de ejecución;
- cuarta ronda: licitación 02/10/2008, recepción esperada 03/10–06/10 e informe 07/10;
- tramo referencia 2006: `ARARGE03E147`, `ARARGE03E154` y `ARARGE03E121`, con VNO en monedas nativas y efectivo ARS siempre separados;
- ventana contractual: cálculo 01/11/2007, compras durante 2008 y cancelación; no inventar día/modalidad;
- control negativo: tercer cupón referencia 2007 y Resolución 115/323 no prueban la recompra objetivo.

## Al recibir una respuesta

- registrar fecha, número de trámite, organismo, área productora, sistema y repositorios consultados;
- verificar ronda, oferta, especie, código, cantidad, emisor/receptor, modalidad, matching, estado y sello temporal;
- no convertir el anuncio de un informe en constancia de entrega;
- no convertir una búsqueda negativa en prueba de inexistencia sin alcance documentado;
- no convertir un acuse técnico en pago;
- no confundir CVSA 5326 del strip con 5426 del título principal;
- actualizar hashes, catálogo, censo, trazabilidad y criterio de cierre antes de cambiar el veredicto.

## Reclamo

Sólo iniciar seguimiento o reclamo después de una presentación real y de registrar su constancia. Mientras el estado sea `DRAFT_NOT_SENT`, no existe vencimiento.

## Control V141 previo a cualquier autorización

- llamar `71597`, `152677` y `2876` “referencias SIDIF” hasta recibir el tipo documental;
- comenzar por Planilla de Remisión/tejuelo del productor `SAF 355`, ejercicio 2008, subserie `Otros Gastos`;
- pedir copias o exportaciones preexistentes, no la elaboración de un cuadro certificado nuevo;
- abrir en paralelo la rama orden/Nota BCRA y la rama débito automático/regularización BNA;
- registrar por separado programación, selección, confirmación, medio, envío, rendición, conciliación y saldo;
- si el receptor no posee, pedir transferencia del artículo 10; si hay excepción parcial, tachas del artículo 12;
- no calcular plazos ni reclamos mientras los seis pedidos continúen `DRAFT_NOT_SENT`.


## Control V141 · SICHE

- [ ] Mantener los tres números rotulados como SIDIF hasta recibir el tipo.
- [ ] Solicitar búsquedas separadas en SIDIF Central y SLU dentro de SICHE.
- [ ] Pedir exportaciones existentes de `gastos_01.rep`, `pagos_04.rep`, `conc_01.rep` y `conc_02.rep` o equivalentes.
- [ ] Tratar C-41 como comparador documental y C-55 Débito Directo como comparador de mecanismo; ninguno como hecho previo a la respuesta.
- [ ] Exigir metadatos de una búsqueda sin resultados.
- [ ] Confirmar autorización expresa antes de cualquier envío.


## Control V141 · doble prioridad y consulta reproducible

- [ ] Buscar primero los tres SIDIF sin restricción de tipo.
- [ ] Tratar C-41 como comparador documental y C-55 como comparador de mecanismo, no como hechos target.
- [ ] Incluir C-42 (SLU) y C-35 (SIDIF Central) sólo como fallbacks.
- [ ] Pedir Gastos, Pagos y Conciliación Bancaria con filtros de cabecera y detalle.
- [ ] Exigir extracto externo, extracto interno/Libro Banco y aplicación para cerrar un débito.
- [ ] Exigir metadatos reproducibles para cualquier resultado cero.
- [ ] Confirmar autorización expresa antes de presentar cualquiera de los seis borradores.


## Control V141 · consultas nombradas

- [ ] Pedir `Formulario por Pda. Presupuestaria y Sigade` con 7.2.8/83106000 y sin beneficiario primero.
- [ ] Correr por separado `Gastos por Beneficiarios`, `Deuda Exigible hasta 2008` y asientos 2001-2012.
- [ ] Pedir definición y fecha de corte de Deuda Exigible antes de interpretar resultados.
- [ ] Usar SIGADE en Pagos como crosswalk posterior, sin presumir migración 2008.
- [ ] Separar asiento, orden, pago, medio posterior, débito y conciliación.
- [ ] Exigir diccionario, filtros y cobertura para todo resultado cero.
- [ ] Confirmar autorización expresa antes de presentar cualquiera de los seis borradores.


## Control V141 · repositorio CUT histórico

- [ ] Identificar la cuenta CUT histórica en Entidades Básicas antes de usar 3855/19.
- [ ] Ejecutar por separado Saldos, Extractos y Logs de Impacto para todo 2008.
- [ ] Cruzar el formulario SICHE con log, extracto, Libro Banco y conciliación.
- [ ] Pedir ambos signos y componentes; no limitar al agregado 32.270,30.
- [ ] Pedir comprobante bancario, respaldo, origen, relacionado e historial.
- [ ] No atribuir una diferencia neta íntegra al target.
- [ ] Exigir metadatos y diccionario para toda grilla vacía.
- [ ] Confirmar autorización expresa antes de presentar cualquiera de los seis borradores.
