# Lista de presentación y seguimiento · V152

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

## Control V152 previo a cualquier autorización

- llamar `71597`, `152677` y `2876` “referencias SIDIF” hasta recibir el tipo documental;
- comenzar por Planilla de Remisión/tejuelo del productor `SAF 355`, ejercicio 2008, subserie `Otros Gastos`;
- pedir copias o exportaciones preexistentes, no la elaboración de un cuadro certificado nuevo;
- abrir en paralelo la rama orden/Nota BCRA y la rama débito automático/regularización BNA;
- registrar por separado programación, selección, confirmación, medio, envío, rendición, conciliación y saldo;
- si el receptor no posee, pedir transferencia del artículo 10; si hay excepción parcial, tachas del artículo 12;
- no calcular plazos ni reclamos mientras los seis pedidos continúen `DRAFT_NOT_SENT`.


## Control V152 · SICHE

- [ ] Mantener los tres números rotulados como SIDIF hasta recibir el tipo.
- [ ] Solicitar búsquedas separadas en SIDIF Central y SLU dentro de SICHE.
- [ ] Pedir exportaciones existentes de `gastos_01.rep`, `pagos_04.rep`, `conc_01.rep` y `conc_02.rep` o equivalentes.
- [ ] Tratar C-41 como comparador documental y C-55 Débito Directo como comparador de mecanismo; ninguno como hecho previo a la respuesta.
- [ ] Exigir metadatos de una búsqueda sin resultados.
- [ ] Confirmar autorización expresa antes de cualquier envío.


## Control V152 · doble prioridad y consulta reproducible

- [ ] Buscar primero los tres SIDIF sin restricción de tipo.
- [ ] Tratar C-41 como comparador documental y C-55 como comparador de mecanismo, no como hechos target.
- [ ] Incluir C-42 (SLU) y C-35 (SIDIF Central) sólo como fallbacks.
- [ ] Pedir Gastos, Pagos y Conciliación Bancaria con filtros de cabecera y detalle.
- [ ] Exigir extracto externo, extracto interno/Libro Banco y aplicación para cerrar un débito.
- [ ] Exigir metadatos reproducibles para cualquier resultado cero.
- [ ] Confirmar autorización expresa antes de presentar cualquiera de los seis borradores.


## Control V152 · consultas nombradas

- [ ] Pedir `Formulario por Pda. Presupuestaria y Sigade` con 7.2.8/83106000 y sin beneficiario primero.
- [ ] Correr por separado `Gastos por Beneficiarios`, `Deuda Exigible hasta 2008` y asientos 2001-2012.
- [ ] Pedir definición y fecha de corte de Deuda Exigible antes de interpretar resultados.
- [ ] Usar SIGADE en Pagos como crosswalk posterior, sin presumir migración 2008.
- [ ] Separar asiento, orden, pago, medio posterior, débito y conciliación.
- [ ] Exigir diccionario, filtros y cobertura para todo resultado cero.
- [ ] Confirmar autorización expresa antes de presentar cualquiera de los seis borradores.


## Control V152 · repositorio CUT histórico

- [ ] Identificar la cuenta CUT histórica en Entidades Básicas antes de usar 3855/19.
- [ ] Ejecutar por separado Saldos, Extractos y Logs de Impacto para todo 2008.
- [ ] Cruzar el formulario SICHE con log, extracto, Libro Banco y conciliación.
- [ ] Pedir ambos signos y componentes; no limitar al agregado 32.270,30.
- [ ] Pedir comprobante bancario, respaldo, origen, relacionado e historial.
- [ ] No atribuir una diferencia neta íntegra al target.
- [ ] Exigir metadatos y diccionario para toda grilla vacía.
- [ ] Confirmar autorización expresa antes de presentar cualquiera de los seis borradores.


## Control V152 · código, cuenta 230 y conciliación

- [ ] Pedir el catálogo de cuentas de operación y movimientos vigente en 2008.
- [ ] Ejecutar cuenta 230 o equivalente sin importe y conservar el universo anual.
- [ ] Buscar `AUTO/DBAUTO/CRAUTO` y descripciones, nunca sólo el código posterior.
- [ ] Ejecutar controles `PAGO/PGTR`, créditos, rechazos, anulaciones y reversas.
- [ ] Exigir código externo/interno, referencia unívoca, formulario, Libro Banco y grupo de conciliación.
- [ ] Cruzar C-55 Débito Directo/CRG-DB o equivalente con los tres SIDIF.
- [ ] No convertir continuidad 2013-2022 en vigencia automática para 2008.
- [ ] Confirmar autorización expresa antes de presentar cualquiera de los seis borradores.


## Control V152 · reportes SLU y C55 contemporáneos

- [ ] Ejecutar `conc_01.rep` y `conc_02.rep` sobre las mismas cuentas, fechas y estados N/P/T.
- [ ] Pedir el universo C55-REG Débito Directo de 2008 sin OP original y con cuenta de débito.
- [ ] Exigir estados I/X/E/C/R e histórico de carga, autorización, envío y respuesta.
- [ ] Buscar C55-DEG, código de error y contraasiento de cada candidato.
- [ ] Distinguir Servicio de la Deuda Pública de Carta de crédito y Transferencias al Exterior.
- [ ] Exigir tipo de medio/nota y cuenta de gastos antes de atribuir la comisión.
- [ ] No contar estado E, R o un C revertido como ejecución confirmada.
- [ ] Confirmar autorización expresa antes de presentar cualquiera de los seis borradores.


## Control V152 · tablas SLU y recuperación histórica

- [ ] Pedir las doce tablas exactas con filas activas, bajas y rehabilitadas.
- [ ] Pedir `BMOVEXTERNO` con banco, contracódigo, interno, grupo y tipo automático/manual.
- [ ] Pedir `AMOV_FORG` con cuenta/subcuenta, movimiento, partida y estado temporal.
- [ ] Pedir `ACLB_MOB` y `BCODLIBBCO` para cerrar extracto→Libro Banco y signo.
- [ ] Pedir inventario y restauración de backups/snapshots 2006-2009, con hash y custodio.
- [ ] Pedir versiones por SAF/módulo y scripts de migración v7→v9.0.
- [ ] Incluir Consulta de Bajas, rehabilitaciones e historial original/corrección.
- [ ] Separar C10 de recurso de C55 de gasto; exigir marca A/M y estados/transmisiones.
- [ ] Controlar C55-DEP/REP/DEG, contraasientos y estados de cheque como reversas/alternativas.
- [ ] No aceptar cero sin tabla, versión, snapshot, filtros, cobertura, filas y diccionario.
- [ ] Mantener los seis pedidos en borrador hasta autorización expresa.

## Control V152 · SICHE, backups y migración SLU

- Mantener `DRAFT_NOT_SENT` sin autorización expresa.
- Adjuntar las matrices de deber, migración, administración/C55, ruta SICHE y objetos de pedido.
- Pedir primero exportación SICHE reproducible; usar restauración si falta cobertura.
- Exigir inventario, logs, actas y custodia; no convertir retención perpetua en presunción de hallazgo.
- Mantener 0/10 hasta cerrar C55/extracto/Libro Banco/cuenta/importe.

## Control V152 · ruta SIGADE/SIDIF-Link/SICHE

- Mantener los seis pedidos en `DRAFT_NOT_SENT` hasta autorización expresa.
- Adjuntar cadena de sistemas, ruta SICHE, objetos de pedido y matriz REPO.
- Pedir export reproducible con parámetros, universo, fecha de corte, filas y hash.
- No equiparar asiento SIDIF con liquidación bancaria ni REPO 2019 con el objetivo 2008.
- Mantener 0/10 hasta cerrar identidad, cuenta, fecha, importe, orden y extracto.

## Control V152 · rectificación de precisión y rama Anexo K

- Mantener los seis pedidos en `DRAFT_NOT_SENT` hasta autorización expresa.
- No llamar error aritmético al 0,45 sin componentes fuente no redondeados.
- Adjuntar fila Anexo K, escalera oficial AGN, tabla de estados y objetos V152.
- Exigir los tres formularios SIDIF individualmente y el `mayorizado por SIGADE`.
- No cerrar pago sin movimiento TGN/CUT o extracto bancario conciliado.
- Mantener CRyL como rama condicional y el resultado estricto en 0/10.

## Control V152 · vía especial y custodia

- Mantener seis pedidos `DRAFT_NOT_SENT` hasta autorización.
- No usar Caja y Bancos como universo exclusivo de SAF355.
- Pedir listados, consultas, versiones y regularizaciones que produjeron Anexo K.
- Aplicar custodia TGN antes de cancelación y CGN después; pedir ruta TGN→BNA.
- Ejecutar ramas orden y débito/regularización en paralelo hasta recuperar el tipo.
- No cerrar sin formulario, orden/imputación y movimiento conciliados; mantener 0/10.

## Control V152 · dos cortes, dos fechas y dos custodias

- Mantener seis pedidos `DRAFT_NOT_SENT` hasta autorización.
- Pedir paquetes 30/6 y 31/12 más enero 2009; no asignar tipo por magnitud.
- Pedir listados, conformidades, ajustes, notas, comunicaciones y originales.
- Distinguir número interno/SIDIF y fecha extracto/proceso.
- Consultar 3855/19 como candidata y el universo completo de cuentas 2008.
- Pedir copias TGN/SAF, snapshot UAI y legajo DADP; custodia no es pago.
- Mantener 0/10 hasta cuerpo y puente bancario conciliado.

## Control V152 · tercera rama sin anticipar el tipo

- Mantener seis pedidos DRAFT_NOT_SENT hasta autorización expresa.
- Buscar C-41, C-42 y C-55 sin clasificar por magnitud o cantidad de dígitos.
- Consultar cada ID crudo y rellenado a siete dígitos.
- Separar SAF, SIDIF/TRANSAF, papel CGN, aprobación TGN y movimiento bancario.
- Distinguir cuenta beneficiaria de cuenta responsable/pagadora.
- Buscar caducidad, reemisión y regularización sin doble conteo.
- Usar e-SIDIF 2012 sólo como comparador; pedir sistemas legados 2008.
- Mantener 0/10 hasta cuerpo y puente bancario conciliado.

## Control V152 · búsqueda dual y tres fuentes

- Mantener los seis pedidos DRAFT_NOT_SENT salvo autorización expresa.
- Ejecutar consultas separadas en SAF355 local, SIDIF Central y TRANSAF.
- No cerrar por un cero unilateral ni contar local y central como dos eventos.
- Pedir por nombre los listados parametrizados local y central y la consulta específica.
- No imponer a 2008 el formato de lote ni la ventana de interfaz de 2022.
- Pedir backend, backups, migraciones, inventarios y disposición documental.
- Triangular sistema local, SIDIF Central, extracto, transferencia TGN y acta.
- Tratar UAI, autenticación, transmisión, recepción y aprobación como etapas no bancarias.
- Mantener cuerpos 0/3 y ejecución 0/10 hasta evidencia individual conciliada.

## Control previo V152

- Pedir Instructivo SGN 02/2008 íntegro, anexos, versiones y distribución.
- Pedir certificaciones UAI Economía/SAF355 de Anexos IV/V y universo completo.
- Pedir por separado informe 1/2009 GNyPE, papeles y seguimiento SIGEN.
- Pedir Informe SIGEN Cuenta 2008 completo, anexos, base y metodología.
- Pedir listados finales art.8, conformidad/discrepancia, ajustes y avisos.
- Pedir índice/legajo/caja/folio de originales cuyo archivo fue certificado.
- Pedir detalle AXT 30/06, explicaciones y razones extrapresupuestarias; cruzar 31/12.
- Pedir `param355`/`inconsis355`, cabeceras, adjuntos, acuses, respuestas y backups.
- Pedir planillas Anexo I con tipo, N° SIDIF, N° SAF, imputación y firma.
- Mantener seis pedidos `DRAFT_NOT_SENT`; ningún hallazgo eleva 0/10.
