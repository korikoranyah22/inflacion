# Veredicto V53 — La cuantificación mejora, pero el hogar sigue sin aparecer como contraparte dominante identificada

## Resultado

```text
COUNTERPARTY_QUANTIFICATION
= PARTIALLY_IDENTIFIED_WITH_BOUNDS

Q4_2023_STRICT_CLASSIFIED_MASS
= 66.20%

Q4_2023_MIXED_ND_REMAINDER
= 33.80%

BCRA_DIRECT_FLOOR
= 26.83%

MARKET_VALUATION_FLOOR
= 39.37%

HOUSEHOLD_DIRECT_POINT_ESTIMATE
= N/D

HOUSEHOLD_STRICT_ISOLATED_BUCKET
= [0, 2.1 pp]
= [0, 7.32%]

DIRECT_HOUSEHOLD_TO_BANK_TRANSFER
= NOT_IDENTIFIED_AT_ABNORMAL_GAP_LEVEL
```

## Qué cambió respecto de V52

V52 había dejado 33.8% del subtotal Q4 en `MIXED/N-D`:

```text
securities 7.3
interest   2.1
other      0.3
```

V53 no fuerza ese remanente. En cambio, demuestra qué puede y qué no puede ser un bound.

### Clasificación disjunta defendible

```text
Pases → BCRA             7.7 pp   26.8%
FX → valuation class    11.3 pp   39.4%
Mixed/N-D                9.7 pp   33.8%
                        ----------------
                        28.7 pp  100.0%
```

Ese es el avance más sólido.

## Títulos

La exposición pública es grande y en 2023 incluye CER, duales, pesos nominales y moneda extranjera. También coexistían instrumentos BCRA.

Pero:

```text
issuer exposure
!=
income share
```

y:

```text
market gain on Treasury bond
!=
Treasury payment to bank
```

Por eso el +7.3 pp no se reparte todavía.

## Intereses

Sí hay identidad contractual posible:

```text
hogar → interés → banco
empresa → interés → banco
```

Pero el +2.1 pp agregado no trae sector split.

El máximo **estrictamente aislado** compatible con hogares es entonces 2.1 pp, no porque sepamos que los hogares lo explicaron, sino porque no pueden explicar más que todo ese bucket sin abrir otros rubros.

## CER/UVA

V53 encuentra una razón adicional para no asignar el neto al hogar: los hogares aparecen en **ambos lados del balance**.

```text
hipoteca UVA:
hogar deudor → banco

depósito UVA:
banco → hogar depositante
```

Y Q4-vs-Q3 el CER agregado fue -0.2 pp, es decir, no fue fuente positiva de la anomalía.

## FX

El +11.3 pp sigue teniendo un mecanismo de valuación fuerte, pero sus gross legs mezclan depósitos, crédito, liquidez, BCRA y forwards.

No aparece:

```text
hogar pagador X
→ banco recibe X
```

## Frontera que queda

Para salir de `N/D` ya no hace falta más narrativa macro: hace falta **micro-contabilidad compatible**.

```text
NEXT
= V54_RAW_BCRA_MICRODATA_INGEST_AND_ACCOUNTING_BRIDGE
```

El objetivo de V54 es recuperar los XLS/XLSX oficiales por titular/emisor/UVA y, sólo si los campos permiten un bridge de devengamiento compatible, transformar los bounds en shares sectoriales.
