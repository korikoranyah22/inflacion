# Auditoría V52 — Contrapartes e incidencia de los componentes bancarios anormales

## Veredicto ejecutivo

```text
DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED_AT_ABNORMAL_GAP_LEVEL
DIRECT_HOUSEHOLD_CONTRACT = EXISTS_FOR_SPECIFIC_CREDIT/FEE CONTRACTS
BCRA_COUNTERPARTY = STRONG_SUPPORT_FOR_PASSES_AND_BCRA_INSTRUMENTS
TREASURY_COUNTERPARTY = SUPPORTED_ONLY_WHEN_TREASURY_INSTRUMENT/FLOW_IS_IDENTIFIED
MARKET_VALUATION = LARGE_FOR_FX_AND_PART_OF_SECURITIES
AGGREGATE_CER_COUNTERPARTY = MIXED / NOT_DECOMPOSED
TAXPAYER_IDENTITY_FOR_PASSES = REJECTED
```

V52 confirma una distinción que V51 dejaba abierta: **identificar el mecanismo que genera una ganancia bancaria no identifica automáticamente quién la paga**.

La cadena correcta es:

```text
componente contable
→ contraparte contractual inmediata
→ incidencia económica de primer orden
→ puentes monetarios/fiscales
→ vínculo con hogares
```

## 1. Pases: el caso más limpio

Para las primas por pases sí existe una contraparte contractual inmediata defendible:

```text
BCRA → prima/interés por pase → banco
```

Los estados contables 2023 del BCRA registran las `primas netas devengadas por operaciones de pases` dentro de intereses/actualizaciones perdidos sobre operaciones con el sistema financiero. El mismo balance registra obligaciones por operaciones de pase. El cambio del 19/12/2023 convirtió a los pases pasivos en el principal instrumento de absorción y el IEF de junio de 2024 describe a las primas por pases (y antes a los intereses de LELIQ) como un canal endógeno de crecimiento de emisión/pasivos monetarios.

Por tanto:

```text
PASSES_DIRECT_COUNTERPARTY = BCRA
```

Pero no:

```text
PASSES = DIRECT_TAXPAYER_PAYMENT
```

El puente a hogares/contribuyentes depende de cómo el resultado del BCRA se financie, esterilice, compense o absorba. El propio IEF señala que recursos captados por el Tesoro y luego depositados en el BCRA podían atemperar el canal de emisión asociado a primas por pases. Eso rompe una identidad uno-a-uno entre prima bancaria y contribuyente.

## 2. Títulos: hay que separar emisor, cupón y precio

`resultado por títulos` no tiene una sola contraparte.

### Instrumento BCRA

LEBAC/NOBAC/LELIQ son pasivos/instrumentos emitidos por el BCRA. Para cupón/devengamiento:

```text
BCRA → banco
```

### Instrumento Tesoro

Para cupón/indexación/devengamiento de un bono del Tesoro:

```text
Tesoro → banco
```

### Valuación secundaria / ORI

Para una suba de precio reconocida contablemente:

```text
mercado / valuación
→ resultado bancario
```

sin que exista necesariamente un pago contemporáneo del Tesoro o BCRA.

### Aplicación a 2014

La persistencia anormal anual sigue siendo `securities-led` (+1,4 pp), y la evidencia institucional muestra mayor tenencia de LEBAC/NOBAC y tasas más altas. Eso permite elevar:

```text
BCRA_INSTRUMENT_LINK_2014 = SUPPORTED
```

pero no permite resolver qué parte exacta del +1,4 pp fue:

- interés de instrumento BCRA;
- título del Tesoro;
- ganancia de precio;
- otro título.

Por eso el componente completo queda `MIXED`.

## 3. FX: ganancia de valuación no es una transferencia bilateral

Los casos 2014 inicial, mayo-2018 y Q4-2023 tienen mecanismo FX fuerte:

```text
tipo de cambio
× posición neta en moneda extranjera
→ diferencias de cotización / ORI
```

Pero la diferencia de cotización es una **revaluación del balance**. Puede existir una enorme variedad de contrapartes debajo de los activos y pasivos brutos —depositantes, empresas, Tesoro, otros bancos, derivados— sin que el resultado contable tenga un único pagador.

Por tanto:

```text
FX_GAIN = MARKET_VALUATION / OWN_POSITION EFFECT
FX_GAIN != HOUSEHOLD_LOSS_IDENTITY
```

En mayo de 2018 el BCRA sí permite identificar el mecanismo con mucha fuerza, incluso con atribución oficial, pero eso no eleva la identidad distributiva.

## 4. CER/UVA: la contraparte depende del contrato

El resultado agregado CER/CVS puede mezclar:

```text
bonos CER del Tesoro
préstamos UVA/CER a hogares
préstamos indexados a empresas
depósitos UVA/CER
otros pasivos indexados
```

Por eso:

```text
AGGREGATE_CER_GAIN != HOUSEHOLD_UVA_TRANSFER
```

Sí puede elevarse `DIRECT_HOUSEHOLD_CONTRACT` cuando se identifica explícitamente un préstamo hogar-banco indexado. Lo que no puede elevarse todavía es la **participación de ese canal dentro del abnormal gap agregado**.

## 5. Crédito y mora: el vínculo directo existe, pero no donde parecía

Hay un vínculo contractual directo real en:

```text
hogar prestatario → interés/comisión → banco
```

Eso es ingreso bruto bancario, no utilidad neta.

En cambio:

```text
mora → previsión/incobrabilidad → menor resultado bancario
```

no es una transferencia del hogar al banco. En 2018 el gap de incobrabilidad aporta -0,3 pp y en Q4-2023 -1,2 pp. La mora actúa como costo/offset para el banco en estas ventanas.

## 6. Diagnóstico cuantitativo Q4-2023 — sólo dentro de la misma ventana

Para evitar mezclar ventanas incompatibles, V52 hace una única suma diagnóstica sobre los **subcomponentes positivos del margen Q4-2023 vs Q3-2023**, todos medidos en la misma tabla homogénea.

```text
gross positive subcomponent gaps = 28.7 pp
FX valuation                      = 11.3 pp (39.4%)
passes, known BCRA counterparty   = 7.7 pp (26.8%)
securities, mixed                 = 7.3 pp (25.4%)
interest income, mixed borrowers  = 2.1 pp (7.3%)
other / N-D                       = 0.3 pp (1.0%)
```

Esto **no** es una descomposición del ROA neto ni un "beneficio total". Es una composición de impulsores positivos brutos dentro de un mismo subtotal.

Lectura defendible:

- al menos 26.8% de esos impulsores positivos brutos tiene contraparte BCRA identificada de forma directa (pases);
- al menos 39.4% es una línea de valuación FX sin pagador bilateral identificable;
- 25.4% queda en un bloque títulos que necesita separar BCRA/Tesoro/valuación;
- como máximo contable, todo el +2.1 pp de `interest_income` (7.3% del gross-positive subtotal) podría contener contratos directos con hogares, pero **la participación hogar real es N/D** y seguramente el rubro mezcla otros deudores;
- por lo tanto, `DIRECT_HOUSEHOLD_SHARE` sigue sin poder cuantificarse.

## 7. Puente cuasifiscal sin doble conteo

Se puede construir un puente institucional para pases:

```text
BCRA pass liability
→ premium expense at BCRA
→ premium income at bank
→ BCRA result / remunerated liabilities
→ possible monetary-liability growth
```

Pero el siguiente salto:

```text
→ taxpayer paid X
```

no está identificado. Para elevarlo haría falta demostrar el mecanismo concreto de absorción de pérdidas del BCRA por Tesoro/impuestos/deuda, o un contrafactual monetario-fiscal compatible. No alcanza con que el BCRA sea estatal.

Para títulos del Tesoro, el puente fiscal es más directo **sólo sobre cupón/devengamiento/principal de instrumentos identificados del Tesoro**. No debe mezclarse con revaluación secundaria.

## 8. Respuestas a las preguntas obligatorias V52

1. **Qué porcentaje de los componentes anormales tiene contraparte BCRA?**  No hay porcentaje total defendible entre episodios/ventanas. En el diagnóstico Q4-2023 de impulsores positivos brutos del margen, el piso directamente identificado es 26.8% por pases. Puede ser mayor si una parte de títulos corresponde a instrumentos BCRA, pero esa fracción es N/D.
2. **Qué componentes tienen contraparte Tesoro?**  Cupón/devengamiento de títulos del Tesoro y eventualmente otros créditos públicos identificados. El `securities_result` agregado es mixto.
3. **Qué componentes son valuación de mercado?**  FX es principalmente una revaluación de posición; títulos/ORI contienen una porción de valuación no separada.
4. **Qué componentes tienen vínculo contractual directo con hogares?**  Intereses/comisiones de créditos bancarios a hogares y ajustes UVA/CER de préstamos hogar identificados. El agregado no permite cuantificar el share.
5. **Qué componentes sólo tienen vínculo indirecto?**  Pases, títulos públicos, FX agregado, resultado monetario y gran parte de CER agregado.
6. **Puede elevarse `DIRECT_HOUSEHOLD_CONTRACT`?**  Sí, a nivel de contrato específico de crédito/fee/UVA de hogar. No como explicación cuantificada del abnormal gap agregado actual.
7. **Puede construirse puente fiscal/cuasi-fiscal sin doble conteo?**  Sí para el primer tramo BCRA/Tesoro→banco. El tramo hasta contribuyente/hogar permanece condicional y no debe sumarse como transferencia directa.
8. **Qué queda N/D?**  Share de títulos por emisor vs valuación; share hogar de interest income; composición CER por sector; contraparte de FX por activos/pasivos brutos; causal share post-10/12 dentro de Q4.

## 9. Gates actualizados

```text
DIRECT_HOUSEHOLD_CONTRACT
= PASS only for an identified household-bank contract and compatible bank revenue component

BCRA_COUNTERPARTY
= PASS for passes and identified BCRA-issued instruments

TREASURY_COUNTERPARTY
= PASS only for identified Treasury instrument contractual flows

MARKET_VALUATION
= PASS when accounting gain arises from price/FX remeasurement without required contemporaneous payer

DIRECT_HOUSEHOLD_TO_BANK_TRANSFER
= NOT_IDENTIFIED at aggregate abnormal-gap level
```

## Fuentes primarias agregadas en V52

- BCRA_IEF_JUN2024: https://www.bcra.gob.ar/publicaciones/informe-de-estabilidad-financiera-junio-de-2024/
- BCRA_POLICY_2023_12_18: https://www.bcra.gob.ar/noticias/nueva-tasa-de-politica-monetaria-y-esquema-de-gestion-de-liquidez/
- BCRA_IMM_DEC2023: https://www.bcra.gob.ar/publicaciones/informe-monetario-mensual-marzo-de-2024-2/
- BCRA_EC_2023: https://www.bcra.gob.ar/publicaciones/balance-anual-bcra-2023/
- BCRA_BANK_DEC2023: https://www.bcra.gob.ar/publicaciones/informe-sobre-bancos-diciembre-de-2023/
- BCRA_BANK_APR2024: https://www.bcra.gob.ar/publicaciones/informe-sobre-bancos-abril-2024/
- BCRA_BANK_JUN2014: https://www.bcra.gob.ar/publicaciones/informe-sobre-bancos-junio-de-2014/
- BCRA_MONETARY_JAN2014: https://www.bcra.gob.ar/publicaciones/informe-monetario-mensual-enero-de-2014/
- BCRA_MONETARY_FEB2014: https://www.bcra.gob.ar/publicaciones/informe-monetario-mensual-febrero-de-2014/
- BCRA_BANK_MAY2018: https://www.bcra.gob.ar/publicaciones/informe-sobre-bancos-mayo-de-2018/
- BCRA_BANK_JUN2018: https://www.bcra.gob.ar/publicaciones/informe-sobre-bancos-junio-de-2018/
- BCRA_FX_MAY2018: https://www.bcra.gob.ar/publicaciones/informe-de-la-evolucion-del-mercado-de-cambios-y-balance-cambiario-mayo-2018/
- BCRA_ANNUAL_2014: https://www.bcra.gob.ar/archivos/Pdfs/Publicaciones/inf2014.pdf
- BCRA_OBJECTIVES_2024: https://www.bcra.gob.ar/Pdfs/Institucional/oyp%202024.pdf
