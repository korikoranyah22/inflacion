# V109

V109 cierra la primera reconstrucción primaria de riesgo bancario para E0 2001–2003. Congela irregularidad mensual, buffers y flujos anuales, explicita ocho restricciones metodológicas y mantiene separados dos vintages oficiales que no coinciden exactamente.

## Delta material

- El censo E0 sube de **27 a 28 fuentes primarias preservadas**.
- El detalle BCRA aporta **36 meses calendario**: 31 observaciones disponibles y cinco faltantes publicados como `.` entre enero y mayo de 2002.
- La irregularidad total observada pasa de 12.545961% en diciembre de 2001 a 21.770759% en octubre de 2002 y cierra 2003 en 17.789776%.
- La irregularidad privada pasa de 18.035634% a 40.285006% y 30.777864% en las mismas fechas.
- El informe anual posterior congela cobertura, exposición neta, cargos por incobrabilidad, liquidez y patrimonio para 2001–2003.
- Cobertura sube de 66.4% a 79.2%; exposición neta sobre patrimonio baja de 21.6% a 11.9%; el peor cargo por incobrabilidad es 2002 (-4.7% de activos neteados).
- Los seis contrastes entre el detalle y el informe posterior quedan `NOT_EXACTLY_RECONCILED`; no se promedian ni se fuerza un empalme.

## Estado que no cambia

- panel estricto Q4-2023: **30 entidades**;
- cobertura: **61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%**;
- `CLOSED_NETWORK_GATE`: **NO**;
- Banco Rioja: mismatch de **158,789k** sin reconciliar;
- no se identifica transferencia causal neta hogares → bancos.

## Estado de fuentes

- entradas catalogadas: **226**;
- copias locales físicas: **221**;
- copias con hash exacto: **221**;
- brecha binaria catalogada: Banco Rioja FY (P1);
- acciones discovery sin binario propio: siete.

## Leer primero

1. `VEREDICTO_V109.md`
2. `AUDITORIA_V109.md`
3. `E0_BCRA_RISK_RECONSTRUCTION_V109.md`
4. `E0_BCRA_RISK_CLOCKS_V109.csv`
5. `E0_BCRA_RISK_METHOD_BREAKS_V109.csv`
6. `E0_BCRA_RISK_VINTAGE_RECONCILIATION_V109.csv`
7. `E0_BCRA_DEBTOR_CLASSIFICATION_MONTHLY_V109.csv`
8. `E0_BCRA_RISK_CAPITAL_LIQUIDITY_V109.csv`
9. `HISTORICAL_EPISODE_MATRIX_2001_2026_V109.csv`
10. `HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V109_A_V110.md`
11. `qa_v109.py`

V109 mejora la secuencia descriptiva de riesgo; no completa los flujos fiscales realizados, la heterogeneidad bancaria ni los buffers mensuales exactos.
