# Veredicto V52 — Los grandes canales no identifican al hogar como contraparte directa

## Resultado

```text
COUNTERPARTY_MAP = SUPPORTED
BCRA_DIRECT_COUNTERPARTY = STRONG_SUPPORT_FOR_PASSES
TREASURY_DIRECT_COUNTERPARTY = CONDITIONAL_ON_IDENTIFIED_TREASURY_FLOW
MARKET_VALUATION_CHANNEL = STRONG_SUPPORT_FOR_FX_AND_PART_OF_SECURITIES
DIRECT_HOUSEHOLD_CONTRACT = REAL_BUT_PARTIAL_AND_UNQUANTIFIED
DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED_AT_ABNORMAL_GAP_LEVEL
TAXPAYER_IDENTITY = REJECTED
```

V52 rompe la versión más fuerte de la narrativa distributiva.

La mayor parte de los grandes componentes anormales ya identificados no puede describirse como:

```text
hogar perdió → banco recibió ese mismo dinero
```

Los grandes canales visibles se reparten entre:

- **BCRA**: pases y títulos propios del Central;
- **Tesoro**: sólo para flujos contractuales de títulos/créditos públicos identificados;
- **mercado/valuación**: FX y parte de títulos/ORI;
- **contratos privados mixtos**: intereses, CER/UVA, depósitos;
- **sin contraparte bilateral**: resultado monetario.

El canal donde sí existe una identidad contractual hogar→banco es el crédito/fee específico:

```text
hogar prestatario
→ interés/comisión contractual
→ ingreso bruto bancario
```

Pero el abnormal gap disponible no está desagregado por sector suficiente para medir cuánto de los +2,1 pp de `interest_income` de Q4-2023, o de los subcomponentes 2018, provino efectivamente de hogares.

### Q4-2023 como diagnóstico

Dentro de los impulsores positivos brutos del margen de la misma ventana Q4-vs-Q3:

```text
FX valuation     11.3 pp    39.4%
Pases BCRA        7.7 pp    26.8%
Títulos mixed     7.3 pp    25.4%
Interest mixed    2.1 pp     7.3%
Other N/D         0.3 pp     1.0%
TOTAL            28.7 pp  100.0%
```

Por lo tanto:

```text
KNOWN_BCRA_FLOOR_WITHIN_Q4_GROSS_POSITIVE = 26.8%
KNOWN_DIRECT_HOUSEHOLD_SHARE = 0% IDENTIFIED, NOT 0% TRUE
POTENTIAL_HOUSEHOLD_CONTRACT_BUCKET = <= 7.3% OF THIS GROSS-POSITIVE SUBTOTAL, SHARE N/D
```

Ese 0% significa **cero identificado con los datos agregados actuales**, no que los hogares no hayan pagado intereses.

## Corrección central

```text
bank abnormal gain
!= household transfer
```

y también:

```text
BCRA payment to bank
!= direct taxpayer payment
```

El siguiente cuello de botella ya es cuantitativo: separar por emisor/sector/contrato los rubros `securities_result`, `interest_income`, `CER/CVS` y la composición bruta de FX.

```text
NEXT = V53_COUNTERPARTY_QUANTIFICATION
```
