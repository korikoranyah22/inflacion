# V110

V110 cierra la primera reconstrucción fiscal primaria de E0 2001–2003 por fases. Separa autorización, fórmula, deuda emitida/colocada, registración contable, tenencias, acreencias, financiamiento BCRA y estado de validación. No fuerza un total de caja donde las fuentes contemporáneas no lo permiten.

## Delta material

- El censo E0 sube de **28 a 31 fuentes primarias preservadas**.
- Se incorporan Cuenta de Inversión 2002, Cuenta de Inversión 2003 y Cuadro 37 del Boletín Fiscal 2003T4.
- El ledger congela **25 filas** de fase/mecanismo.
- El puente 2002–2003 contiene **12 controles** de stock, nominales e imputaciones contables.
- Se congelan **16 restricciones metodológicas**.
- Al 31/12/2002, los stocks actualizados publicados son ARS 22.035,916m compensatorios, ARS 8.120,833m de cobertura y ARS 18.078,963m para ahorristas.
- Al 31/12/2003, son ARS 17.348,345m, ARS 6.879,649m y ARS 17.664,377m, junto con ARS 7.086,660m de cuasimonedas y ARS 2.546,266m por restitución del 13%.
- El total BODEN 2003 de ARS 51.525,296m queda explícitamente prohibido como rótulo de compensación bancaria.
- El BCRA informa ARS 14.573m de compensaciones a recibir y deja pendiente la determinación definitiva del monto y de los activos a entregar.

## Estado que no cambia

- panel estricto Q4-2023: **30 entidades**;
- cobertura: **61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%**;
- `CLOSED_NETWORK_GATE`: **NO**;
- Banco Rioja: mismatch de **158,789k** sin reconciliar;
- no se identifica transferencia causal neta hogares → bancos.

## Estado de fuentes

- entradas catalogadas: **229**;
- copias locales físicas: **224**;
- copias con hash exacto: **224**;
- brecha binaria catalogada: Banco Rioja FY (P1);
- acciones discovery sin binario propio: siete.

## Leer primero

1. `VEREDICTO_V110.md`
2. `AUDITORIA_V110.md`
3. `E0_FISCAL_RECONSTRUCTION_V110.md`
4. `E0_FISCAL_MECHANISM_LEDGER_V110.csv`
5. `E0_FISCAL_STOCK_FLOW_BRIDGE_V110.csv`
6. `E0_FISCAL_METHOD_BREAKS_V110.csv`
7. `HISTORICAL_EPISODE_MATRIX_2001_2026_V110.csv`
8. `HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V110_A_V111.md`
9. `qa_v110.py`

V110 mejora la medición fiscal descriptiva; no completa entrega por beneficiario, servicios de deuda/caja, cancelaciones, auditoría AGN ni incidencia neta.
