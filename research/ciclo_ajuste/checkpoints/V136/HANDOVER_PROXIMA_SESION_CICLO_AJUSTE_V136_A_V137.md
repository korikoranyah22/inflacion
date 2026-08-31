# Handover V136 → V137

## Estado congelado

- Diez adjudicaciones participante-instrumento exactas; nueve cuentas BCRA candidatas; MERVAL abierta; 0/10 ejecuciones confirmadas.
- Alineación visual exacta: cuenta `83106000`, Banco Nación, ARS 32.270,30, SIDIF `71597`, `152677`, `2876`; el corrimiento de snippet es falso.
- Esquema `SDPGB/SDPAG`: identidad OB, beneficiario, importe, `P/R/A`, fecha, banco, cuenta y medio; filas target no localizadas.
- Sistema 2008: clases de archivo de instrucción TGN→BCRA, movimientos y saldos BCRA→TGN probadas; vínculos target abiertos.
- Entorno productor 2008: SIDIF Central/TRANSAF legacy probado; e-SIDIF Gastos se despliega después; nombre literal SDPGB/SDPAG 2008 abierto.
- AGAN/AMIDDF: custodio directo de respaldo financiero, originales, índices e imágenes probado; holdings target no consultados.
- Pago parcial: regla exacta 2008 probada; exigir importe original, pagos acumulados, saldo y caducidad.
- Paquete papel/listas firmadas: esquema sucesor 2009 probado, sin retroproyección automática a 2008.
- CRYL: recepción de movimientos documentada como incorporación en 2009; ruta específica 2008 abierta.
- Pago exterior: paquete documental exacto probado en 2008, sólo condicional a clasificación SAF 355/356.
- COMDOC/deuda: comparadores de remito, folios, búsqueda/reconstrucción, nota, aceptación y SIGADE; no equivalencia target.
- Bicameral: seis variantes exactas de los dos OV sin coincidencia en el índice HCDN; nota 18/05/2012 abierta.
- Seis pedidos DRAFT_NOT_SENT; ninguno enviado; panel estricto sin cambios.

## Prioridad V137

1. Si hay autorización expresa, presentar los seis pedidos; si no, mantenerlos como borradores.
2. Priorizar búsqueda AGAN/AMIDDF por OB `71597`, `152677`, `2876`, cuenta `83106000`, SAF, renglón e importe agregado.
3. Obtener extracto SIDIF Central, estado, importe original, todos los pagos parciales y saldo por OB.
4. Buscar copia papel C-41, lista diaria firmada, autorización si aplica, instrucción TGN→BCRA y movimiento bancario target.
5. Probar o descartar clasificación exterior de cada orden antes de aplicar la Disposición 47/10.
6. Verificar si existía ruta CRYL específica en 2008; no sustituirla por movimientos BCRA generales.
7. Mantener separados orden, selección, pago parcial, pago total, Caja, crédito BCRA y cancelación CRYL.
