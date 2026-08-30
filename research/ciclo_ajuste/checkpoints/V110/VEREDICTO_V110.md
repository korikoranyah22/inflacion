# Veredicto V110

## Qué sabemos ahora

- La compensación por pesificación y la cobertura cambiaria son mecanismos distintos.
- Al cierre de 2002 existía stock oficial emitido y colocado por ARS 22.035,916m compensatorios y ARS 8.120,833m de cobertura, valuado a esa fecha.
- Al cierre de 2003 esos stocks eran ARS 17.348,345m y ARS 6.879,649m.
- El total BODEN incluye ahorristas, cuasimonedas y restitución del 13%; no es un total de ayuda bancaria.
- La Cuenta de Inversión registra ARS 16.183,54426211m en 2002 y tres líneas por ARS 3.923,73653360m en 2003, pero son compatibilizaciones contables y no una serie de caja.
- El sistema financiero reconocía ARS 14.573m de compensaciones a recibir al 31/12/2003.
- La determinación definitiva del monto y de los activos a entregar permanecía pendiente.
- Los adelantos BCRA para suscribir BODEN y las obligaciones del BCRA con el Tesoro no son transferencias fiscales a bancos.
- El diferimiento contable de pérdidas por amparos no fue compensación.

## Qué no sabemos todavía

- cuánto y cuándo recibió cada entidad;
- qué parte fue amortizada, rescatada, canjeada, corregida o cancelada con caja;
- cómo concilian CRYL, Tesoro y balances bancarios instrumento por instrumento;
- la ejecución posterior de la Ley 25.796;
- el resultado de una auditoría AGN específica;
- la incidencia neta después de pérdidas, fondeo, valuaciones y aportes de capital.

## Restricciones fuertes

- `monto autorizado = monto pagado` es inadmisible.
- `stock emitido = flujo de caja` es inadmisible.
- `compensaciones a recibir = activos recibidos` es inadmisible.
- `total BODEN = compensación bancaria` es inadmisible.
- `compensación bruta = ganancia bancaria neta` es inadmisible.
- Los stocks del emisor, los saldos del BCRA y las registraciones contables no se suman sin un puente transaccional.

## Estado del proyecto

La rama fiscal E0 pasa a `PRIMARY_FISCAL_LEDGER_PARTIAL`, con fases separadas y caja final abierta. El panel microbancario permanece en 30 entidades y 61.8555625288919…% de activos; `CLOSED_NETWORK_GATE` sigue en `NO`.
