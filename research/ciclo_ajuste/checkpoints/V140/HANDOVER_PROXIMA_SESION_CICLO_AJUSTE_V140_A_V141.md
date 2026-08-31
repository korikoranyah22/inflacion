# Handover V140 → V141

## Estado

- QA V140: ejecutar y exigir PASS.
- Consulta principal exacta: `Formulario por Pda. Presupuestaria y Sigade` con SAF355/2008/7.2.8/83106000.
- Consultas de control: `Gastos por Beneficiarios`, `Deuda Exigible hasta 2008` y asientos 2001-2012.
- Campos probados: beneficiario, clasificador económico, observaciones OP, Debe/Haber, cuenta, asiento anual y tipo.
- Pagos: SIGADE está en EPP, PG, NPG, CMR-DP, TCE/RTCE y reportes e-SIDIF 2020; migración 2008 abierta.
- Doble prioridad documental/mecánica V139 permanece; ninguna fila target recuperada.
- Seis pedidos `DRAFT_NOT_SENT`; 10 adjudicaciones, 9 cuentas candidatas, 0/10 ejecuciones confirmadas.

## Prioridad V141

1. Mantener los seis pedidos como borradores salvo autorización expresa.
2. Si se autoriza, presentar Economía/RAIP con los nombres exactos de consulta y el runbook V140.
3. Exigir exportación sin beneficiario primero; luego filtros y observaciones.
4. Exigir definición/corte de Deuda Exigible y diccionario de todos los datasets.
5. Cruzar toda fila con Pagos por SIGADE, Conciliación Bancaria y AMIDDF.
6. Mantener cero de consulta separado de ausencia, pago, anulación o expurgo.
