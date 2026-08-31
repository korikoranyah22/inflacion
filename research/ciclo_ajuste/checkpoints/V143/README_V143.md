# V143 · puente SLU contemporáneo 2001-2005

V143 reduce el salto temporal que subsistía en V142. Los manuales oficiales previos a 2008 ya documentan el circuito completo: `conc_01.rep` para movimientos del Extracto, `conc_02.rep` para Libro Banco, estados N/P/T, y C55-REG Débito Directo para una comisión debitada, con estados I/X/E/C/R, aceptación central, histórico y reversa C55-DEG.

El manual versión 3 queda fechado por metadato PDF el 16/08/2005. Además aporta un control causal nuevo: el medio `Servicio de la Deuda Pública` no cobra gastos y comisiones; Carta de crédito y Transferencias al Exterior sí los tienen y usan una cuenta de gastos. Esto obliga a probar el tipo de operación antes de atribuir `COMISIONES - BANCO NACION` a deuda pública.

La cadena ahora es: rama del medio → C55 y estado → conc_01 → conc_02 → código/referencia → log y respaldo. El literal exacto 230/AUTO vigente en 2008 y la fila target siguen abiertos. Ninguna consulta fue ejecutada ni enviada. Balance: 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones confirmadas; seis pedidos DRAFT_NOT_SENT.
