# Handover V142 → V143

## Estado

- QA V142: ejecutar y exigir PASS.
- Cuenta de operación 230: débitos del extracto no originados en pagos CUT; gastos bancarios como ejemplo.
- Código 2013 `AUTO`; evolución 2022 `DBAUTO/CRAUTO`; rutas ordinarias separadas `PAGO/PGTR`.
- Cadena: código externo/interno → referencia unívoca → formulario → Libro Banco → LIB/APL/EXB/MAN → T/P/N.
- Continuidad 2013-2022 probada sólo como crosswalk; catálogo y código exactos 2008 siguen abiertos.
- SICHE CUT-SIDIF Central 2007-2014 conserva Entidades, Saldos, Extractos y Logs para ejecutar el test.
- Ninguna fila target recuperada; seis pedidos DRAFT_NOT_SENT; 10 adjudicaciones, 9 cuentas candidatas, 0/10 ejecuciones confirmadas.

## Prioridad V143

1. Mantener los seis pedidos como borradores salvo autorización expresa.
2. Buscar catálogo o exportación histórica que confirme cuenta 230/AUTO o sus equivalentes en 2008.
3. Buscar tablas básicas de conversión de código BNA externo a interno y grupos LIB/APL/EXB/MAN.
4. Intentar localizar referencias unívocas o contracódigos en extractos/logs públicos de 2008.
5. Mantener cuenta/código, formulario, extracto, Libro Banco y conciliación como capas separadas.
