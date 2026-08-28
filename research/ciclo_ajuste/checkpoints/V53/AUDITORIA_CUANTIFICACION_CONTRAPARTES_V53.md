# Auditoría V53 — Cuantificación por emisor, sector y contrato

## 1. Objetivo

V53 toma los `MIXED`/`N/D` de V52 y pregunta cuánto puede cuantificarse **sin fabricar una asignación sectorial**.

La unidad prioritaria sigue siendo la ventana homogénea:

```text
Q4-2023 vs Q3-2023
gross-positive margin subcomponent gaps = 28.7 pp
```

Componentes congelados:

```text
FX                  +11.3 pp
pases                +7.7 pp
títulos              +7.3 pp
interest income      +2.1 pp
otros                +0.3 pp
TOTAL                28.7 pp
```

Esto **no** es utilidad neta, no es el ROA de +9.0 pp y no es un treatment effect post-10/12.

---

## 2. Resultado cuantitativo nuevo

### 2.1 Masa que puede clasificarse sin solapamiento

Dos buckets tienen clasificación primaria suficientemente fuerte para no mezclarlos entre sí:

```text
pases → BCRA counterparty          7.7 pp
FX    → valuation-class channel   11.3 pp
                                   ------
                                   19.0 pp
```

Sobre 28.7 pp:

```text
STRICTLY_CLASSIFIED_MASS = 66.20%
UNRESOLVED_MIXED_MASS    = 33.80%
```

El remanente exacto es:

```text
títulos     7.3
intereses   2.1
otros       0.3
           ----
            9.7 pp
```

La mejora de V53 no consiste en repartir artificialmente esos 9.7 pp, sino en construir **bounds**.

---

## 3. Securities: por qué todavía no hay split BCRA/Tesoro/mercado

### 2014

La anomalía anual de títulos es +1.4 pp. BCRA documenta que durante 2014 aumentó la participación de instrumentos de regulación monetaria en la liquidez bancaria y que las ganancias anuales mayores fueron fundamentalmente por títulos.

Eso prueba:

```text
BCRA_INSTRUMENT_PRESENCE = SUPPORTED
SECURITIES_LED_ABNORMALITY = STRONG_SUPPORT
```

pero no prueba:

```text
+1.4 pp = LEBAC/NOBAC
```

El bucket conserva una envolvente individual 0–1.4 pp para BCRA, Tesoro y valuación. Las envolventes se superponen y no son sumables.

### 2018

La composición cambia dentro del semestre: el BCRA documenta una reducción de LEBAC/LELIQ y un aumento de activos del sector público admitidos como encaje, incluidos Bonos del Tesoro 2020.

Esto mejora la identificación institucional, pero no permite asignar el abnormal H1 porque no existe un sub-gap exacto congelado por instrumento.

### Q4-2023

El +7.3 pp de títulos sigue siendo el principal bloqueo.

La evidencia estructural es fuerte: a septiembre de 2023 la exposición al sector público no financiero era 17.7% del activo; dentro de ella 8.6% del activo eran instrumentos CER, 5.6% bonos duales, 2.1% títulos en pesos sin CER y 1.4% instrumentos en moneda extranjera.

Pero:

```text
stock/exposure share
!=
result contribution share
```

y además:

```text
Treasury-issued security
+
market appreciation
!=
Treasury payment
```

Por eso V53 deja:

```text
BCRA-linked securities       = [0, 7.3] pp bucket capacity
Treasury/public securities   = [0, 7.3] pp bucket capacity
market valuation securities  = [0, 7.3] pp bucket capacity
```

**No son bounds conjuntos.**

---

## 4. Interest income: contrato directo existe, sector share no

La cuenta Q4 aumenta +2.1 pp.

Existen contratos directos:

```text
hogar → interés → banco
empresa → interés → banco
sector público → interés → banco
```

La exposición a septiembre muestra que el crédito a familias era 11.8% del activo y el crédito a empresas cerca de 15%.

Eso no habilita un prorrateo por stocks porque el ingreso depende de:

- tasa efectiva;
- devengamiento;
- moneda;
- duración;
- atrasos;
- líneas/productos;
- reprecificación.

Entonces cada sector recibe sólo una **envolvente individual**:

```text
household interest contribution = [0, 2.1] pp
corporate interest contribution = [0, 2.1] pp
public/other contribution        = [0, 2.1] pp
```

Nuevamente: no son sumables.

### Techo estricto del canal hogar identificado

Dentro de los buckets positivos explícitamente aislados de la tabla congelada:

```text
HOUSEHOLD_DIRECT_REVENUE_STRICT_CEILING
= 2.1 pp
= 7.32% del gross-positive subtotal
```

Esto es un **techo contable de bucket**, no una estimación de cuánto pagaron los hogares.

---

## 5. CER/UVA: V53 encuentra un falsificador interno de signo único

Q4-2023:

```text
CER/CVS abnormal gap = -0.2 pp
```

Por tanto no pertenece al subtotal positivo.

A la vez, la estructura muestra hogares en ambos lados:

### Activo del banco

A marzo de 2023 los hipotecarios UVA a personas humanas representaban aproximadamente:

```text
22% del financiamiento a personas humanas
3.2% del activo total del sistema
~95 mil deudores
```

### Pasivo del banco

Al cierre de diciembre los depósitos UVA llegaron a ARS 588,217 millones; el informe monetario del BCRA atribuye 83% del total a personas físicas.

Entonces:

```text
HOUSEHOLD_CER_POSITION_HAS_SINGLE_SIGN = REJECTED
```

Un hogar puede estar:

```text
deudor UVA → banco
```

o:

```text
banco → depositante UVA
```

El neto CER/CVS agregado no puede llamarse transferencia hogar→banco.

---

## 6. FX: se mejora el mapa bruto, no aparece un pagador

Q4-2023:

```text
FX abnormal gap = +11.3 pp
```

V53 conserva `MARKET_VALUATION` como clasificación primaria de este canal, pero documenta mejor los gross legs:

- depósitos privados en moneda extranjera;
- crédito privado en moneda extranjera;
- liquidez en moneda extranjera;
- posiciones vinculadas al BCRA;
- forwards/derivados.

A septiembre de 2023, aproximadamente:

```text
private FX deposits = 8.4% del fondeo
private FX credit   = 2.4% del activo
FX liquidity        = 8.6% del activo
```

Y el informe de diciembre incorpora forwards en la medición del descalce.

Conclusión:

```text
FX_GROSS_COUNTERPARTIES = MIXED
FX_ACCOUNTING_VALUATION_CHANNEL = STRONG_SUPPORT
DIRECT_HOUSEHOLD_PAYER = NOT_IDENTIFIED
```

Una revaluación de posición neta puede generar resultado sin que exista un pagador bilateral equivalente.

---

## 7. Bounds Q4-2023

### BCRA

Piso directo identificado:

```text
7.7 / 28.7 = 26.83%
```

Envolvente BCRA-linked si todo el bucket títulos fuera BCRA-compatible:

```text
(7.7 + 7.3) / 28.7 = 52.26%
```

El extremo superior **no es direct cashflow** ni estimación.

### Tesoro / sector público

No hay un pp positivo directamente identificado como pago Tesoro.

Capacidad máxima marginal de buckets compatibles:

```text
títulos 7.3 + interés 2.1 = 9.4 pp
9.4 / 28.7 = 32.75%
```

Pero el componente de títulos puede ser valuación, por lo que:

```text
DIRECT_TREASURY_FLOW = N/D
```

### Valuación de mercado

Piso:

```text
FX = 11.3 pp = 39.37%
```

Capacidad marginal si todo títulos fuera también valuación:

```text
11.3 + 7.3 = 18.6 pp = 64.81%
```

### Hogares

Techo estricto aislado:

```text
0–2.1 pp
0–7.32%
```

No elevar el lower bound: existe contrato, pero no sector split del +2.1.

### Empresas

Misma lógica para el bucket explícito de intereses:

```text
0–2.1 pp
0–7.32%
```

---

## 8. Por qué los máximos no suman 100%

Los upper bounds de BCRA, Tesoro, mercado, hogares y empresas son **envolventes marginales**.

Compiten por los mismos buckets mixtos:

```text
securities 7.3
interest   2.1
```

Por eso nunca deben sumarse entre categorías.

La única partición disjunta defendible en V53 es:

```text
BCRA passes          7.7
FX valuation class  11.3
mixed/N-D             9.7
                    ----
                    28.7
```

---

## 9. Qué datos faltan para romper N/D

El BCRA publica páginas oficiales con archivos descargables para:

- préstamos/de depósitos privados por tipo de titular;
- sector público por jurisdicción;
- tenencia de títulos públicos por emisor/jurisdicción;
- préstamos UVA;
- series/anexos de Informes sobre Bancos.

En esta ejecución se verificó la existencia documental de esas aperturas, pero no se obtuvieron bytes homogéneos de los XLS/XLSX necesarios para construir un bridge contable de ingreso/devengamiento por sector.

Por lo tanto, V53 **no usa stocks como sustituto**.

El siguiente gate exige:

```text
accounting income by sector/instrument
OR
compatible stock × effective accrued rate bridge
+
same accounting window
```

---

## 10. Veredicto metodológico

```text
COUNTERPARTY_QUANTIFICATION_V53
= PARTIALLY_IDENTIFIED_WITH_BOUNDS

STRICTLY_CLASSIFIED_Q4_GROSS_POSITIVE
= 66.20%

UNRESOLVED_Q4_GROSS_POSITIVE
= 33.80%

HOUSEHOLD_DIRECT_POSITIVE_SHARE
= NOT_POINT_IDENTIFIED
STRICT_ISOLATED_BUCKET_BOUND
= [0, 7.32%]

DIRECT_HOUSEHOLD_TO_BANK_TRANSFER
= NOT_IDENTIFIED_AT_ABNORMAL_GAP_LEVEL
```
