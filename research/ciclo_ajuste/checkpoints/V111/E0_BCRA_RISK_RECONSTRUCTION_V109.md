# E0 · reconstrucción de riesgo, previsiones, liquidez y capital (V109)

## Resultado

V109 congela dos relojes oficiales que deben permanecer separados. El detalle histórico de BCRA permite una secuencia mensual de clasificación de deudores entre enero de 2001 y diciembre de 2003, salvo cinco faltantes publicados como `.` entre enero y mayo de 2002. El Informe sobre Bancos de octubre de 2004 aporta una tabla anual posterior y autocontenida para cartera irregular, previsiones, exposición neta, cargos por incobrabilidad, liquidez y situación patrimonial.

En el detalle mensual, la cartera irregular total pasa de 12.545961% en diciembre de 2001 a un máximo observado de 21.770759% en octubre de 2002 y cierra diciembre de 2003 en 17.789776%. Para financiaciones al sector privado no financiero y residentes en el exterior, la secuencia equivalente es 18.035634%, 40.285006% y 30.777864%. Ninguna vuelve al punto de partida dentro de la ventana.

La tabla anual posterior confirma el patrón de estrés y normalización parcial: la irregularidad total es 13.1%, 18.1% y 17.7% en 2001–2003, mientras la privada es 19.1%, 38.6% y 33.5%. Al mismo tiempo, la cobertura con previsiones aumenta de 66.4% a 79.2% y la exposición irregular neta de previsiones sobre patrimonio cae de 21.6% a 11.9%. Los cargos por incobrabilidad alcanzan su peor flujo anual en 2002 (-4.7% de activos neteados) y mejoran a -1.1% en 2003.

La liquidez contable calculada como activos líquidos sobre depósitos sube de 19.568750% a 29.138268%. En cambio, el cociente contable patrimonio/activos neteados baja de 14.947178% a 11.905343%. Este último es solo un proxy patrimonial: no es integración de capital regulatorio ni suficiencia de capital.

## Reconciliación de vintages

Los cierres anuales del informe posterior no reproducen exactamente los cierres del libro de detalle. Las diferencias van de -2.217073 a +2.722136 puntos porcentuales según año y universo. La metodología oficial admite revisiones de períodos anteriores y reglas de agregación con última información disponible; además pueden intervenir diferencias de universo y redondeo. Con la evidencia preservada no es posible asignar todo el residuo a una causa única. El estado correcto es `NOT_EXACTLY_RECONCILED`: se mantienen ambos vintages, no se promedian y la comparabilidad se limita al interior de cada uno.

## Límites interpretativos

- “Cartera irregular” significa situaciones 3 a 6 de la clasificación de deudores; no equivale a atraso de pagos puro.
- Cobertura/previsiones son stocks o buffers; cargos por incobrabilidad son un flujo de resultados.
- Enero–mayo de 2002 permanece faltante, por lo que el máximo mensual es el máximo **observado**, no una prueba sobre lo ocurrido dentro del hueco.
- La liquidez reconstruida es el coeficiente contable del informe y el cociente patrimonio/activos es un proxy descriptivo.
- Los agregados no identifican incidencia por entidad ni permiten atribuir causalmente pérdidas o ganancias finales a hogares, bancos o Estado.

## Artefactos

- `E0_BCRA_DEBTOR_CLASSIFICATION_MONTHLY_V109.csv`: componentes y suma mensual de situaciones 3–6.
- `E0_BCRA_RISK_CAPITAL_LIQUIDITY_V109.csv`: cierres anuales y cocientes derivados.
- `E0_BCRA_RISK_CLOCKS_V109.csv`: relojes resumidos y estados de recuperación.
- `E0_BCRA_RISK_VINTAGE_RECONCILIATION_V109.csv`: seis contrastes de cierre.
- `E0_BCRA_RISK_METHOD_BREAKS_V109.csv`: restricciones obligatorias de uso.
