# V140 · consultas SICHE nombradas y puente SIGADE-Pagos

V140 identifica por primera vez una consulta SICHE cuyo nombre coincide exactamente con las claves target: `Formulario por Pda. Presupuestaria y Sigade`. Para `7.2.8 + 83106000`, la consulta admite beneficiario y clasificador económico e incluye observaciones de la orden de pago. Se agregan tres controles preexistentes: `Gastos por Beneficiarios`, `Deuda Exigible hasta 2008` y `Consulta detallada de asientos 2001 a 2012` con Debe/Haber, cuenta, asiento anual y tipo.

El Newsletter e-SIDIF línea 33 prueba además que el atributo SIGADE aparece en EPP, PG, NPG, CMR-DP, TCE/RTCE y consultas/reportes del entorno Nación. Se usa como crosswalk posterior, no como prueba de migración 2008. El runbook queda listo, pero ninguna consulta fue ejecutada ni enviada. Resultado estricto: 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones confirmadas; seis pedidos `DRAFT_NOT_SENT`.
