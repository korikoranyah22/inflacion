# AUDITORÍA V75 — CREDICOOP 9M BINARY RECOVERY + ALTERNATE FOUR-LEG BRIDGE

**Fecha de corte:** 2026-08-28  
**Base:** V74  
**Rama:** contrapartes / pases / cobertura bancaria / incidencia distributiva

## Hallazgo principal

El binario oficial Credicoop 30/09/2023 fue recuperado manualmente por Miyu y preservado en el bundle. Es un PDF de 160 páginas que contiene tanto estados consolidados como **estados separados**. La sección separada comienza en la página PDF 80 y las notas separadas en la página 89.

SHA-256: `d0ad8cbd61bd65792d6f400045b0065d0ce0d4524ca938711a8d5b00a50bb769`.

## Disclosure 9M compatible

La Nota 6.1 separada (PDF p.131) desagrega ingresos por intereses y muestra:

- pases activos con el BCRA = **57,895,351** miles de ARS homogéneos a Sep-2023;
- pases activos con el sector financiero = **0** (`-.-`);
- otros pases activos = **0** (`-.-`).

La Nota 6.2 separada (PDF p.132) detalla exhaustivamente los egresos por intereses. Las filas visibles suman exactamente el total **763,535,485** y no existe importe de pases pasivos. El cero se acepta sólo junto con el crosswalk FY: bajo la misma taxonomía, FY Note 6 y FY Annex Q muestran pass-expense = 0.

## Crosswalk FY Note 6 ↔ Annex Q

En FY-2023 separado:

- Note 6 `Int. por pases activos con el B.C.R.A.` = **180,887,922**;
- Annex Q `Por operaciones de pase / Banco Central de la República Argentina` = **180,887,922**.

La identidad exacta prueba que el renglón 9M de Note 6 es compatible con la pata `income_bcra` del Annex Q anual. El total FY de pases coincide íntegramente con BCRA, por lo que `income_otherfi = 0`. No hay egreso por pases en FY.

## Bridge Q4

Se mantiene el factor congelado:

`Q4_Dec = FY_Dec - 9M_Sep * 1.532908152197492`

Resultado Credicoop Q4-2023, miles de ARS homogéneos a Dic-2023:

- income_bcra = **92139666.477765**
- expense_bcra = **0**
- income_otherfi = **0**
- expense_otherfi = **0**
- net_bcra = **92139666.477765**
- net_otherfi = **0**

## Cobertura estricta

Credicoop pasa de FY-control-only a **Q4 exact target-basis**.

```text
STRICT_Q4_FOUR_LEG_EXACT = ICBC + Banco de Valores + Banco Macro + Banco Credicoop
ASSET_COVERAGE = 14.564124643487%
INCREMENT_VS_V74 = 3.303156795500 pp
CLOSED_PASS_NETWORK = NOT_ACHIEVED
```

La cobertura sigue demasiado baja para interpretar el neteo interbancario del subconjunto como cancelación sistémica.

## Gate metodológico

No se promovió Credicoop por ausencia/presencia de Anexo Q trimestral. Se promovió porque apareció un **disclosure primario 9M separado alternativo**, y su semántica fue validada contra el Annex Q FY de la misma entidad y período anual.
