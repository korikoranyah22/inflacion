# Handover V143 → V144

## Estado

- QA V143: ejecutar y exigir PASS.
- Manual SLU versión 3 fechado por metadato PDF el 16/08/2005; diseño inequívocamente pre-2008.
- Rama Servicio de la Deuda Pública: no cobra gastos/comisiones; Carta de crédito y Transferencias al Exterior: sí.
- C55-REG Débito Directo: comisión debitada, sin OP original, cuenta de débito obligatoria, +débito, estados I/X/E/C/R e histórico.
- Reportes contemporáneos: `conc_01.rep` (Extracto) y `conc_02.rep` (Libro Banco), ambos con estado N/P/T.
- Cadena: tipo de medio → C55/estado → conc_01 → conc_02 → cuenta/código/referencia → log/respaldo → reversa.
- Cuenta 230 y AUTO/DBAUTO quedan como crosswalk posterior; catálogo/código exacto 2008 siguen abiertos.
- SICHE CUT-SIDIF Central 2007-2014 conserva Entidades, Saldos, Extractos y Logs para ejecutar el test.
- Ninguna fila target recuperada; seis pedidos DRAFT_NOT_SENT; 10 adjudicaciones, 9 cuentas candidatas, 0/10 ejecuciones confirmadas.

## Prioridad V144

1. Mantener los seis pedidos como borradores salvo autorización expresa.
2. Localizar un catálogo/exportación 2008 que confirme 230/AUTO o equivalentes y versión de los módulos SLU.
3. Buscar una salida histórica de `conc_01.rep`, `conc_02.rep` o C55-REG con SAF 355.
4. Buscar tabla BNA externo→interno, referencia unívoca y grupos LIB/APL/EXB/MAN.
5. Aplicar siempre la prueba de rama del medio y controlar C55-DEG/contraasiento.
