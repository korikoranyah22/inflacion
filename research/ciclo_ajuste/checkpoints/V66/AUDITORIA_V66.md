# AUDITORIA V66 — Individual AQ retrieval and network expansion

## 1. Gate de base

Se mantuvo sin cambios:

```text
SYSTEM_PANEL_BASIS = INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING
```

No se incorporó ningún filing consolidado al numerador sistémico.

## 2. Banco de Valores — nuevo exacto Q4

Se recuperaron tablas de Anexo Q **separadas** para 9M y FY 2023. Ambas expresan cifras en miles de pesos en moneda homogénea. Se aplicó la regla congelada:

```text
Q4_Dec = FY_Dec - 9M_Sep * (1.532908152197492)
```

Resultado Q4 (miles de ARS de diciembre 2023):

```text
income BCRA     = 132269429.624
expense BCRA    = 0
income otherFI  = 47920.656
expense otherFI = 204552.353
net BCRA        = 132269429.624
net otherFI     = -156631.697
```

Calidad: `EXACT_FROM_COMPATIBLE_9M_AND_FY_HOMOGENEOUS_DIFFERENCING`.

Caveat de fuente: el 9M fue recuperado como copia del filing original desde un repositorio/mirror de filings; el FY proviene del sitio oficial del emisor. La tabla 9M contiene firmas/fecha y estructura del filing original. Se conserva el caveat de jerarquía documental, pero no se redondeó ni imputó ningún valor.

## 3. Cobertura estricta

El BCRA informa activos Dic-2023 de Banco de Valores = **1.071.950,1 millones ARS**.

Por tanto:

```text
ICBC + Banco de Valores exact full-four-leg Q4
= 5037563 million ARS assets
= 5.2096% of bank assets
```

Esto es un **diagnóstico de retrieval**, no ponderación de flujos.

## 4. Supervielle — exactitud del total, bound de contraparte

Los estados 9M separados publican en Nota 25:

```text
9M pass income total  = 88,903,285
9M pass expense total = 420,309
```

El FY separado Anexo Q publica:

```text
FY income BCRA     = 219,708,132
FY income otherFI  =   3,285,840
FY expense BCRA    = 0
FY expense otherFI =   1,235,416
```

La diferenciación homogénea da:

```text
Q4 total pass income  = 86713401.666
Q4 total pass expense = 591120.907
```

El split de ingreso 9M no está publicado en la Nota 25 usada. No se lo inventó. Bajo no negatividad de patas brutas:

```text
Q4 income otherFI in [0 ; 3,285,840]
Q4 income BCRA    in [83427561.666 ; 86713401.666]
Q4 expense BCRA   = 0
Q4 expense otherFI= 591120.907
```

Por eso Supervielle entra como `BOUND`, no como entidad four-leg exacta.

## 5. Test de netting

Exact subset ICBC + Banco de Valores:

```text
otherFI income  = 89754.381
otherFI expense = 1148423.213
otherFI net     = -1058668.831
coverage        = 5.2096% assets
```

Con Galicia (otherFI exact, BCRA expense faltante):

```text
otherFI net = 3669761.401
coverage    = 14.178874% assets
```

Ninguno es test de cancelación sistémica. El signo cambia al ampliar el subconjunto, lo que refuerza —no debilita— la regla de no inferir sistema desde una red abierta.

## 6. Retrieval que no se elevó

- Provincia: FY exacto sí; 9M compatible no recuperado.
- Credicoop: existencia 30-09-2023 confirmada; datos Anexo Q no recuperados.
- Nación: existencia de estados separados 9M confirmada; four-leg Anexo Q no extraído.
- La nomenclatura histórica de PDFs BCRA no se trató como endpoint 2023 probado.

## 7. Gates preservados

```text
CLOSED_PASS_NETWORK = NOT_ACHIEVED
SYSTEM_INTERBANK_PASS_CANCELLATION = NOT_IDENTIFIED_COVERAGE_TOO_LOW
SYSTEM_BCRA_NET_PASS_FLOW = N/D
SYSTEM_INTERBANK_NET_PASS_FLOW = N/D
IEF_7_7PP_BCRA_SHARE = N/D
HOUSEHOLD_ANNEX_Q_ACCRUED_INTEREST_FLOW_BRIDGE = NOT_IDENTIFIED
DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED
HTML_MODIFICATION = FORBIDDEN
```
