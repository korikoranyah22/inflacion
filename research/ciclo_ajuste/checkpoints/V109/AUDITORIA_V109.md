# Auditoría V109 — rama riesgo E0

## Alcance

Se siguió la prioridad de riesgo del handover V108. Se releyó de manera reproducible el detalle histórico BCRA ya preservado y se incorporó el Informe sobre Bancos de octubre de 2004 como fuente oficial posterior. Los originales XLS/PDF no fueron modificados.

## Preservación y lectura

El PDF nuevo tiene 448,224 bytes y SHA-256 `2a92bfc1de9fa86bc60c94d7ef867cf904e7d8713707a993eaf75d91c5c9f1cf`. Sus 14 páginas fueron extraídas y las páginas 11–14 se renderizaron e inspeccionaron visualmente: metodología, glosario y cuadros anualizados de bancos privados y sistema financiero son legibles.

El libro histórico `hist_bcra_baldethis.xls` se abrió en modo lectura. La reconstrucción usa las filas del cuadro I-3-2 y suma los componentes de situaciones 3 a 6. El script preservado produce 36 filas mensuales, mantiene cinco valores `PUBLISHED_AS_DOT` y audita el residuo de redondeo contra normal + riesgo potencial.

## Relojes congelados

- Irregularidad mensual total y privada: enero de 2001–diciembre de 2003, con enero–mayo de 2002 faltante.
- Irregularidad anual total, privada, comercial y consumo+vivienda: 2001–2003.
- Cobertura de previsiones e irregularidad neta sobre financiaciones/patrimonio.
- Cargos por incobrabilidad y ROA como flujos de resultados.
- Activos líquidos, depósitos, previsiones, patrimonio y activos neteados como stocks anuales.
- Liquidez contable y proxy patrimonio/activos derivados exactamente de esos stocks.

## Reconciliación y restricciones

Los cierres anuales del informe posterior difieren de los cierres del detalle mensual entre -2.217073 y +2.722136 pp. Las seis diferencias son reales en los originales preservados. La evidencia disponible no identifica una única causa; por ello se conservan dos vintages y la comparabilidad queda `WITHIN_VINTAGE_ONLY`.

También quedan congeladas siete restricciones adicionales: el hueco enero–mayo de 2002; la definición de irregularidad como situaciones 3–6; la separación stock/flujo; la definición contable de liquidez; el carácter no regulatorio del proxy patrimonial; el régimen de moneda homogénea para resultados; y las reglas de agregación/revisión del sistema.

## Integridad

El catálogo sube a 226 entradas y 221 copias físicas/hash-válidas. La única brecha binaria catalogada y las siete acciones discovery anteriores permanecen. El panel Q4-2023 se replica sin cambios.

## Límite inferencial

La evidencia muestra estrés de cartera, buffers crecientes y normalización parcial, no una ganancia bancaria homogénea ni una transferencia causal neta. Los agregados tampoco sustituyen un ledger fiscal ni estados individuales por entidad.
