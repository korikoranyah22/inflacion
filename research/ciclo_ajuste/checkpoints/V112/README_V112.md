# V112

V112 lleva la reconstrucción fiscal E0 hasta el vencimiento de BODEN 2007 y BODEN 2012. Reconcilia el movimiento anual por serie, congela correcciones por propósito y agrega controles AGN de tenedores sin fabricar una imputación bancaria.

## Delta material

- El censo E0 sube de **40 a 48 fuentes primarias preservadas**: seis Cuentas de Inversión y dos informes AGN.
- El ledger fiscal alcanza **88 filas**; 30 pertenecen al tramo 2007–2012.
- El puente de servicio contiene **7 filas**: BODEN 2007 finaliza en 2007 y BODEN 2012 se reconcilia anualmente hasta cero en 2012.
- Para BODEN 2012, la reducción acumulada 2007–2012 es **USD 13285.8062125m** de nominal actualizado; las columnas contables suman **ARS 52253.64973061m** de principal y **ARS 4970.64200805m** de intereses.
- Se congelan **37 restricciones metodológicas**.
- Las correcciones por propósito continúan en 2007–2009; la cobertura sigue separada de la compensación.
- Las recompras 2008–2009 son mixtas o carecen de monto por especie: no se imputan a bancos.
- La AGN aporta distribución agregada de acreedores y una excepción auditada del FGS, no un padrón CRYL banco por banco.

## Estado que no cambia

- panel estricto Q4-2023: **30 entidades**;
- cobertura: **61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%**;
- `CLOSED_NETWORK_GATE`: **NO**;
- Banco Rioja: mismatch de **158,789k**;
- no se identifica transferencia causal neta hogares → bancos.

## Leer primero

1. `VEREDICTO_V112.md`
2. `E0_FISCAL_RECONSTRUCTION_V112.md`
3. `E0_FISCAL_BODEN_SERVICE_BRIDGE_2007_2012_V112.csv`
4. `E0_FISCAL_BODEN_STOCK_BRIDGE_2007_2012_V112.csv`
5. `E0_FISCAL_TRANSACTION_LEDGER_2007_2012_V112.csv`
6. `AUDITORIA_V112.md`
7. `HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V112_A_V113.md`
8. `qa_v112.py`
