# Veredicto V144

La ruta de prueba ya no depende de adivinar `230/AUTO`. El esquema contemporáneo permite pedir las tablas concretas que codificaban cuenta, movimiento bancario, grupo, partida automática y Libro Banco. `BMOVEXTERNO` vincula la codificación BNA con el movimiento interno; `AMOV_FORG` vincula cuenta y movimiento con gasto; la relación genera C55 y lo envía a SIDIF Central; `ACLB_MOB` y `BCODLIBBCO` cierran el lado Libro Banco.

Pero ese cierre de esquema no confirma la ejecución: los manuales dicen que esas tablas son `sin historia`. Una respuesta basada sólo en datos activos actuales sería metodológicamente insuficiente. La respuesta idónea debe restaurar o exportar el estado 2008, incluir bajas y rehabilitaciones, y documentar versión/migración. También debe separar C10 de recurso, C55 de gasto, C55-DEP/REP/DEG y ruta cheque.

La captura `SLU v9.0` del 26/11/2008 reduce el salto de versión, con el límite explícito de no probar la fila target. No se recuperó código BNA, fila AMOV_FORG, C55, extracto, Libro Banco, log ni respaldo individual. Permanecen 10 adjudicaciones exactas, 9 cuentas candidatas y 0/10 ejecuciones confirmadas; los seis pedidos siguen sin enviar.
