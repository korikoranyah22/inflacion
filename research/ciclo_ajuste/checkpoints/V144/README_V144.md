# V144 · tablas SLU y recuperación histórica 2008

V144 cierra el diccionario de base que faltaba. Los manuales oficiales identifican `BCUENTA`, `ACTA_FUE`, `ACTABAN_CTAESC`, `BGRUPMOVBCO`, `BMOVBCO`, `BMOVEXTERNO`, `AMOV_FORG`, `ACLB_MOB`, `BCODLIBBCO`, `BEMPRESA`, `BERROR_AUD` y `BPROCESO`. La cadena exacta es cuenta → código externo BNA → código interno/grupo → parametrización automática de gasto → C55/SIDIF Central → Libro Banco → extracto/conciliación → corrección o reversa.

El hallazgo decisivo es también una limitación probatoria: las tablas centrales se declaran `sin historia`. Por eso la vista vigente no puede resolver ni negar una fila de 2008. V144 transforma esa limitación en un objeto de pedido verificable: backups, dumps y snapshots 2006-2009, Consulta de Bajas y rehabilitaciones, matriz de versiones y scripts v7→v9.0, historial de correcciones y exportaciones de cada tabla.

El taller oficial preserva capturas `SLU v9.0` fechadas en 2006 y 26/11/2008; prueban versión e interfaz mostradas, no la fila target ni el despliegue de cada SAF. El manual C10 separa la rama recurso/crédito de la rama C55/gasto y la desafectación agrega controles de reversa. Ninguna consulta fue ejecutada ni enviada. Balance: 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones confirmadas; seis pedidos DRAFT_NOT_SENT.
