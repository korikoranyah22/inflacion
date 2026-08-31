# V142 · diccionario CUT y ruta de comisiones

V142 identifica un discriminante que V141 todavía no tenía: la cuenta de operación `230` concentra débitos del extracto que no son pagos CUT y cita gastos bancarios como ejemplo. El manual 2013 la denomina `Débitos Automáticos`; el de 2022 conserva el código y la función como `Débitos extracto bancario`. En paralelo, el código `AUTO` de 2013 evoluciona a `DBAUTO/CRAUTO` y queda separado de `PAGO/PGTR`.

La cadena de verificación es ahora: cuenta 230 o equivalente → código externo/interno → referencia unívoca → formulario de regularización → Libro Banco → grupo y estado de conciliación → log/respaldos. Es un crosswalk de consulta, no una atribución retroactiva: el catálogo 2008 sigue pendiente. Ninguna consulta fue ejecutada ni enviada. Balance: 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones confirmadas; seis pedidos DRAFT_NOT_SENT.
